"""Integration boundary between Architecture v2 retrieval and governance.

Architecture v2 evidence sufficiency remains authoritative.

The existing review-decision module continues to control lifecycle,
cross-document reasoning, confidence, and automatic-answer eligibility.

This module does not replace those governance controls.
"""

from __future__ import annotations

from typing import Any

from src.governance.review_decision import (
    ABSTAIN,
    decide_review_outcome,
)


def decide_retrieval_governance_outcome(
    question: str,
    retrieval_output: dict[str, Any],
) -> dict[str, Any]:
    """Convert Architecture v2 retrieval output into governance outcome.

    Safety order:

    1. Validate the retrieval output contract.
    2. Honour the retrieval scope decision.
    3. Honour Architecture v2 final evidence sufficiency.
    4. Only sufficient evidence may enter the existing
       pre-generation review-decision logic.

    Retrieval evidence that remains insufficient must never be
    upgraded to AUTO_ANSWER merely because one result has a strong
    similarity score.
    """

    if not isinstance(
        question,
        str,
    ):
        raise TypeError(
            "question must be a string"
        )

    if not question.strip():
        raise ValueError(
            "question must not be blank"
        )

    if not isinstance(
        retrieval_output,
        dict,
    ):
        raise TypeError(
            "retrieval_output must be a dictionary"
        )

    audit = retrieval_output.get(
        "audit"
    )

    if not isinstance(
        audit,
        dict,
    ):
        raise ValueError(
            "retrieval_output must contain an audit dictionary"
        )

    results = retrieval_output.get(
        "results"
    )

    if not isinstance(
        results,
        list,
    ):
        raise ValueError(
            "retrieval_output must contain a results list"
        )

    scope = audit.get(
        "scope"
    )

    if not isinstance(
        scope,
        dict,
    ):
        raise ValueError(
            "retrieval audit must contain a scope dictionary"
        )

    if scope.get(
        "allowed"
    ) is not True:
        return {
            "decision": ABSTAIN,
            "reason": (
                "Architecture v2 retrieval rejected the question "
                "at the approved scope gate."
            ),
            "requires_human_review": False,
            "may_generate_answer": False,
            "document_ids": [],
            "retrieval_route": audit.get(
                "selected_route"
            ),
            "retrieval_stop_reason": audit.get(
                "stop_reason"
            ),
        }

    final_evidence = audit.get(
        "final_evidence"
    )

    if not isinstance(
        final_evidence,
        dict,
    ):
        return {
            "decision": ABSTAIN,
            "reason": (
                "Architecture v2 retrieval did not provide a valid "
                "final evidence assessment."
            ),
            "requires_human_review": False,
            "may_generate_answer": False,
            "document_ids": [],
            "retrieval_route": audit.get(
                "selected_route"
            ),
            "retrieval_stop_reason": audit.get(
                "stop_reason"
            ),
        }

    if final_evidence.get(
        "sufficient"
    ) is not True:
        return {
            "decision": ABSTAIN,
            "reason": (
                "Architecture v2 retrieval evidence remains "
                "insufficient for answer generation."
            ),
            "requires_human_review": False,
            "may_generate_answer": False,
            "document_ids": [],
            "retrieval_route": audit.get(
                "selected_route"
            ),
            "retrieval_stop_reason": audit.get(
                "stop_reason"
            ),
        }

    decision = decide_review_outcome(
        question=question,
        scope_assessment=scope,
        results=results,
    )

    return {
        **decision,
        "retrieval_route": audit.get(
            "selected_route"
        ),
        "retrieval_stop_reason": audit.get(
            "stop_reason"
        ),
    }