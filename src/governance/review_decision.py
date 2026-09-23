from __future__ import annotations

from typing import Any


AUTO_ANSWER = "AUTO_ANSWER"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
ABSTAIN = "ABSTAIN"

MIN_AUTO_ANSWER_SIMILARITY = 0.65
MIN_AUTO_ANSWER_SCORE_GAP = 0.05


def _normalise_text(
    value: str,
) -> str:
    if not isinstance(value, str):
        raise TypeError(
            "value must be a string"
        )

    return " ".join(
        value.lower().split()
    )


def _get_unique_document_ids(
    results: list[dict[str, Any]],
) -> list[str]:
    document_ids: list[str] = []

    for result in results:
        document_id = result.get(
            "document_id"
        )

        if (
            isinstance(document_id, str)
            and document_id
            and document_id not in document_ids
        ):
            document_ids.append(
                document_id
            )

    return document_ids


def _all_results_active(
    results: list[dict[str, Any]],
) -> bool:
    if not results:
        return False

    return all(
        result.get("status") == "Active"
        for result in results
    )


def _has_cross_document_intent(
    question: str,
) -> bool:
    normalised = _normalise_text(
        question
    )

    terms = {
        "across documents",
        "combine",
        "combined",
        "both",
        "together",
        "compare",
        "relationship between",
        "workforce and bed",
        "staffing and bed",
        "multiple policies",
    }

    return any(
        term in normalised
        for term in terms
    )


def _has_lifecycle_risk(
    results: list[dict[str, Any]],
) -> bool:
    risky_statuses = {
        "Draft",
        "Superseded",
        "Archived",
    }

    return any(
        result.get("status")
        in risky_statuses
        for result in results
    )


def _get_similarity_scores(
    results: list[dict[str, Any]],
) -> list[float]:
    scores: list[float] = []

    for result in results:
        score = result.get(
            "similarity_score"
        )

        if isinstance(
            score,
            (int, float),
        ):
            scores.append(
                float(score)
            )

    return scores


def _has_strong_clear_evidence(
    results: list[dict[str, Any]],
) -> bool:
    """
    AUTO_ANSWER confidence rule.

    Requirements:

    - top semantic similarity >= 0.65
    - gap between first and second result >= 0.05

    If there is only one scored result,
    top similarity alone is sufficient.
    """

    scores = (
        _get_similarity_scores(
            results
        )
    )

    if not scores:
        return False

    top_score = scores[0]

    if (
        top_score
        < MIN_AUTO_ANSWER_SIMILARITY
    ):
        return False

    if len(scores) == 1:
        return True

    score_gap = (
        scores[0]
        - scores[1]
    )

    return (
        score_gap
        >= MIN_AUTO_ANSWER_SCORE_GAP
    )


def decide_review_outcome(
    question: str,
    scope_assessment: dict[str, Any],
    results: list[dict[str, Any]],
) -> dict[str, Any]:

    if not isinstance(question, str):
        raise TypeError(
            "question must be a string"
        )

    if not question.strip():
        raise ValueError(
            "question must not be blank"
        )

    if not isinstance(
        scope_assessment,
        dict,
    ):
        raise TypeError(
            "scope_assessment must be a dictionary"
        )

    if not isinstance(
        results,
        list,
    ):
        raise TypeError(
            "results must be a list"
        )

    if (
        scope_assessment.get("allowed")
        is not True
    ):
        return {
            "decision": ABSTAIN,
            "reason": (
                "Question is outside the approved "
                "operational-policy scope."
            ),
            "requires_human_review": False,
            "may_generate_answer": False,
            "document_ids": [],
        }

    if not results:
        return {
            "decision": ABSTAIN,
            "reason": (
                "No eligible evidence was retrieved."
            ),
            "requires_human_review": False,
            "may_generate_answer": False,
            "document_ids": [],
        }

    document_ids = (
        _get_unique_document_ids(
            results
        )
    )

    if _has_lifecycle_risk(
        results
    ):
        return {
            "decision": REVIEW_REQUIRED,
            "reason": (
                "Retrieved evidence contains a lifecycle "
                "state requiring human confirmation."
            ),
            "requires_human_review": True,
            "may_generate_answer": False,
            "document_ids": document_ids,
        }

    if _has_cross_document_intent(
        question
    ):
        return {
            "decision": REVIEW_REQUIRED,
            "reason": (
                "Question requires cross-document or "
                "multi-domain reasoning."
            ),
            "requires_human_review": True,
            "may_generate_answer": False,
            "document_ids": document_ids,
        }

    if not _all_results_active(
        results
    ):
        return {
            "decision": REVIEW_REQUIRED,
            "reason": (
                "Evidence could not be confirmed as "
                "entirely Active."
            ),
            "requires_human_review": True,
            "may_generate_answer": False,
            "document_ids": document_ids,
        }

    if _has_strong_clear_evidence(
        results
    ):
        return {
            "decision": AUTO_ANSWER,
            "reason": (
                "Question is in scope and the top Active "
                "evidence meets the configured confidence "
                "and score-gap requirements."
            ),
            "requires_human_review": False,
            "may_generate_answer": True,
            "document_ids": document_ids,
        }

    return {
        "decision": REVIEW_REQUIRED,
        "reason": (
            "Evidence is relevant but does not meet the "
            "configured confidence and separation "
            "requirements for automatic answering."
        ),
        "requires_human_review": True,
        "may_generate_answer": False,
        "document_ids": document_ids,
    }


def decide_post_generation_outcome(
    pre_generation_decision: dict[str, Any],
    citation_verification: dict[str, Any],
) -> dict[str, Any]:
    """
    Apply post-generation governance after citation verification.

    This function does not replace the existing pre-generation
    governance decision.

    It adds a second safety gate after an answer has been generated.

    Expected citation_verification decisions:

    - PASS
    - REVIEW_REQUIRED
    - ABSTAIN
    """

    if not isinstance(
        pre_generation_decision,
        dict,
    ):
        raise TypeError(
            "pre_generation_decision must be a dictionary"
        )

    if not isinstance(
        citation_verification,
        dict,
    ):
        raise TypeError(
            "citation_verification must be a dictionary"
        )

    pre_decision = (
        pre_generation_decision.get(
            "decision"
        )
    )

    citation_decision = (
        citation_verification.get(
            "decision"
        )
    )

    document_ids = (
        pre_generation_decision.get(
            "document_ids",
            [],
        )
    )

    # --------------------------------------------------------------
    # Pre-generation ABSTAIN remains authoritative.
    # --------------------------------------------------------------

    if pre_decision == ABSTAIN:
        return {
            "decision": ABSTAIN,
            "reason": (
                "Pre-generation governance requires abstention. "
                "Post-generation citation verification cannot "
                "override that decision."
            ),
            "requires_human_review": False,
            "may_return_answer": False,
            "document_ids": document_ids,
        }

    # --------------------------------------------------------------
    # Pre-generation human review remains authoritative.
    # --------------------------------------------------------------

    if pre_decision == REVIEW_REQUIRED:
        return {
            "decision": REVIEW_REQUIRED,
            "reason": (
                "Pre-generation governance already requires "
                "human review."
            ),
            "requires_human_review": True,
            "may_return_answer": False,
            "document_ids": document_ids,
        }

    # --------------------------------------------------------------
    # Only AUTO_ANSWER can proceed to post-generation validation.
    # --------------------------------------------------------------

    if pre_decision != AUTO_ANSWER:
        return {
            "decision": REVIEW_REQUIRED,
            "reason": (
                "Unrecognised pre-generation decision. "
                "Human review is required."
            ),
            "requires_human_review": True,
            "may_return_answer": False,
            "document_ids": document_ids,
        }

    # --------------------------------------------------------------
    # Citation verifier explicitly abstains.
    # --------------------------------------------------------------

    if citation_decision == ABSTAIN:
        return {
            "decision": ABSTAIN,
            "reason": (
                "Post-generation citation verification "
                "could not validate the generated answer."
            ),
            "requires_human_review": False,
            "may_return_answer": False,
            "document_ids": document_ids,
        }

    # --------------------------------------------------------------
    # Citation verifier requires human review.
    # --------------------------------------------------------------

    if citation_decision == REVIEW_REQUIRED:
        return {
            "decision": REVIEW_REQUIRED,
            "reason": (
                "Generated answer contains unsupported, "
                "partially supported, or mismatched citations."
            ),
            "requires_human_review": True,
            "may_return_answer": False,
            "document_ids": document_ids,
        }

    # --------------------------------------------------------------
    # Citation verifier passes.
    # --------------------------------------------------------------

    if citation_decision == "PASS":
        return {
            "decision": AUTO_ANSWER,
            "reason": (
                "Pre-generation governance approved automatic "
                "answering and all material answer claims passed "
                "citation verification."
            ),
            "requires_human_review": False,
            "may_return_answer": True,
            "document_ids": document_ids,
        }

    # --------------------------------------------------------------
    # Fail-safe for unknown citation decisions.
    # --------------------------------------------------------------

    return {
        "decision": REVIEW_REQUIRED,
        "reason": (
            "Citation verification returned an unrecognised "
            "decision. Human review is required."
        ),
        "requires_human_review": True,
        "may_return_answer": False,
        "document_ids": document_ids,
    }