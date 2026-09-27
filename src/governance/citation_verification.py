"""Citation verification for grounded RAG answers.

This module performs post-generation safety checks.

It verifies whether:
- an answer claim has cited evidence;
- the cited document/chunk exists;
- the cited evidence is lifecycle-safe;
- lexical evidence supports the claim;
- material high-risk mismatches are absent;
- safe borderline paraphrases can be recovered through semantic similarity.

Safety principle:

Semantic rescue can never override:
- citation mismatch;
- non-Active evidence;
- unsupported numbers;
- unsupported mandatory wording;
- unsupported actors;
- unsupported actions;
- negation mismatch;
- unsupported prohibitions.

This remains a governed prototype. Semantic similarity is not treated as proof
of factual entailment.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Any

from src.governance.high_risk_claim_guard import (
    detect_high_risk_mismatch,
)


VALID_LIFECYCLE_STATUSES = {"active"}

DEFAULT_SUPPORT_THRESHOLD = 0.60
DEFAULT_SEMANTIC_RESCUE_THRESHOLD = 0.75


IGNORED_TERMS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "been",
    "being",
    "by",
    "can",
    "could",
    "did",
    "do",
    "does",
    "for",
    "from",
    "had",
    "has",
    "have",
    "how",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "may",
    "must",
    "of",
    "on",
    "or",
    "should",
    "that",
    "the",
    "their",
    "them",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "to",
    "was",
    "were",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "will",
    "with",
    "would",
}


def _normalise(text: str) -> str:
    """Normalise text for deterministic comparison."""

    if not isinstance(text, str):
        return ""

    return re.sub(
        r"[^a-z0-9]+",
        " ",
        text.lower(),
    ).strip()


def _material_terms(text: str) -> set[str]:
    """Extract simple material lexical terms from text."""

    terms = set()

    for term in _normalise(text).split():
        if len(term) <= 2:
            continue

        if term in IGNORED_TERMS:
            continue

        if term.isdigit():
            terms.add(term)
            continue

        terms.add(term)

    return terms


def _get_evidence_text(
    evidence: dict[str, Any],
) -> str:
    """Combine evidence fields used for lexical support checking."""

    parts = []

    for field in (
        "title",
        "section",
        "text",
    ):
        value = evidence.get(field)

        if isinstance(value, str) and value.strip():
            parts.append(value.strip())

    return " ".join(parts)


def _get_semantic_evidence_text(
    evidence: dict[str, Any],
) -> str:
    """Return the most appropriate evidence text for semantic comparison.

    Prefer the actual chunk text so title overlap does not artificially inflate
    semantic similarity.
    """

    text = evidence.get("text")

    if isinstance(text, str) and text.strip():
        return text.strip()

    return _get_evidence_text(
        evidence
    )


def _citation_matches_evidence(
    citation: dict[str, Any],
    evidence: dict[str, Any],
) -> bool:
    """Check that citation identifiers match the supplied evidence."""

    citation_document_id = citation.get(
        "document_id"
    )

    evidence_document_id = evidence.get(
        "document_id"
    )

    if citation_document_id != evidence_document_id:
        return False

    citation_chunk_id = citation.get(
        "chunk_id"
    )

    evidence_chunk_id = evidence.get(
        "chunk_id"
    )

    if citation_chunk_id is not None:
        if citation_chunk_id != evidence_chunk_id:
            return False

    return True


def _is_lifecycle_safe(
    evidence: dict[str, Any],
) -> bool:
    """Accept only Active evidence when lifecycle status is provided."""

    status = evidence.get(
        "status"
    )

    if status is None:
        # Preserve backward compatibility for older synthetic tests that
        # pre-date lifecycle metadata.
        return True

    normalised_status = _normalise(
        str(status)
    )

    return (
        normalised_status
        in VALID_LIFECYCLE_STATUSES
    )


def _claim_support_ratio(
    claim_text: str,
    evidence_text: str,
) -> tuple[
    float,
    list[str],
    list[str],
]:
    """Calculate lexical coverage of material claim terms."""

    claim_terms = _material_terms(
        claim_text
    )

    evidence_terms = _material_terms(
        evidence_text
    )

    if not claim_terms:
        return 0.0, [], []

    matched = sorted(
        claim_terms
        & evidence_terms
    )

    missing = sorted(
        claim_terms
        - evidence_terms
    )

    ratio = (
        len(matched)
        / len(claim_terms)
    )

    return (
        ratio,
        matched,
        missing,
    )


@lru_cache(maxsize=1)
def _get_embedding_model():
    """Load the embedding model lazily and cache it.

    Lazy loading avoids paying the model-loading cost unless a claim actually
    reaches the semantic-rescue stage.
    """

    from sentence_transformers import (
        SentenceTransformer,
    )

    return SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2"
    )


def _semantic_similarity(
    claim_text: str,
    evidence_text: str,
) -> float:
    """Calculate semantic similarity for low-risk paraphrase rescue."""

    from sklearn.metrics.pairwise import (
        cosine_similarity,
    )

    model = _get_embedding_model()

    embeddings = model.encode(
        [
            claim_text,
            evidence_text,
        ]
    )

    score = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]],
    )[0][0]

    return float(score)


def verify_claim_citation(
    claim: dict[str, Any],
    evidence: dict[str, Any] | None,
    *,
    support_threshold: float = DEFAULT_SUPPORT_THRESHOLD,
    semantic_rescue: bool = True,
    semantic_rescue_threshold: float = (
        DEFAULT_SEMANTIC_RESCUE_THRESHOLD
    ),
) -> dict[str, Any]:
    """Verify one claim against its cited evidence.

    Verification order:

    1. claim/citation validation;
    2. citation resolution;
    3. document/chunk identity;
    4. lifecycle safety;
    5. lexical support;
    6. high-risk mismatch guard;
    7. semantic rescue for low-risk paraphrases.

    Semantic rescue never overrides a hard safety failure.
    """

    if not isinstance(
        claim,
        dict,
    ):
        raise TypeError(
            "claim must be a dictionary"
        )

    claim_id = claim.get(
        "claim_id"
    )

    claim_text = claim.get(
        "claim_text"
    )

    citation = claim.get(
        "citation"
    )

    if (
        not isinstance(
            claim_id,
            str,
        )
        or not claim_id.strip()
    ):
        raise ValueError(
            "claim must contain a non-blank claim_id"
        )

    if (
        not isinstance(
            claim_text,
            str,
        )
        or not claim_text.strip()
    ):
        raise ValueError(
            "claim must contain non-blank claim_text"
        )

    if citation is None:
        return {
            "claim_id": claim_id,
            "claim_text": claim_text,
            "status": "UNSUPPORTED",
            "reason": "Claim has no citation.",
            "support_ratio": 0.0,
            "matched_terms": [],
            "missing_terms": sorted(
                _material_terms(
                    claim_text
                )
            ),
            "document_id": None,
            "chunk_id": None,
        }

    if not isinstance(
        citation,
        dict,
    ):
        raise TypeError(
            "citation must be a dictionary"
        )

    if evidence is None:
        return {
            "claim_id": claim_id,
            "claim_text": claim_text,
            "status": "CITATION_MISMATCH",
            "reason": (
                "Citation does not resolve to supplied evidence."
            ),
            "support_ratio": 0.0,
            "matched_terms": [],
            "missing_terms": sorted(
                _material_terms(
                    claim_text
                )
            ),
            "document_id": citation.get(
                "document_id"
            ),
            "chunk_id": citation.get(
                "chunk_id"
            ),
        }

    if not isinstance(
        evidence,
        dict,
    ):
        raise TypeError(
            "evidence must be a dictionary or None"
        )

    if not _citation_matches_evidence(
        citation,
        evidence,
    ):
        return {
            "claim_id": claim_id,
            "claim_text": claim_text,
            "status": "CITATION_MISMATCH",
            "reason": (
                "Citation identifiers do not match "
                "the supplied evidence."
            ),
            "support_ratio": 0.0,
            "matched_terms": [],
            "missing_terms": sorted(
                _material_terms(
                    claim_text
                )
            ),
            "document_id": citation.get(
                "document_id"
            ),
            "chunk_id": citation.get(
                "chunk_id"
            ),
        }

    if not _is_lifecycle_safe(
        evidence
    ):
        return {
            "claim_id": claim_id,
            "claim_text": claim_text,
            "status": "CITATION_MISMATCH",
            "reason": (
                "Citation points to evidence that is "
                "not lifecycle-safe."
            ),
            "support_ratio": 0.0,
            "matched_terms": [],
            "missing_terms": sorted(
                _material_terms(
                    claim_text
                )
            ),
            "document_id": evidence.get(
                "document_id"
            ),
            "chunk_id": evidence.get(
                "chunk_id"
            ),
        }

    evidence_text = _get_evidence_text(
        evidence
    )

    (
        support_ratio,
        matched_terms,
        missing_terms,
    ) = _claim_support_ratio(
        claim_text,
        evidence_text,
    )

    # --------------------------------------------------------------
    # Stage 1: ordinary lexical pass
    # --------------------------------------------------------------

    if (
        support_ratio
        >= support_threshold
    ):
        return {
            "claim_id": claim_id,
            "claim_text": claim_text,
            "status": "SUPPORTED",
            "reason": (
                "Cited evidence contains sufficient "
                "material lexical support for the claim."
            ),
            "support_ratio": round(
                support_ratio,
                4,
            ),
            "matched_terms": matched_terms,
            "missing_terms": missing_terms,
            "document_id": evidence.get(
                "document_id"
            ),
            "chunk_id": evidence.get(
                "chunk_id"
            ),
        }

    # --------------------------------------------------------------
    # Stage 2: high-risk mismatch guard
    #
    # This runs BEFORE semantic rescue.
    # --------------------------------------------------------------

    semantic_evidence_text = (
        _get_semantic_evidence_text(
            evidence
        )
    )

    guard = (
        detect_high_risk_mismatch(
            claim_text,
            semantic_evidence_text,
        )
    )

    if guard[
        "guard_triggered"
    ]:
        status = (
            "PARTIALLY_SUPPORTED"
            if support_ratio > 0
            else "UNSUPPORTED"
        )

        return {
            "claim_id": claim_id,
            "claim_text": claim_text,
            "status": status,
            "reason": (
                "Claim contains a material high-risk "
                "mismatch that blocks semantic rescue: "
                + ", ".join(
                    guard["reasons"]
                )
            ),
            "support_ratio": round(
                support_ratio,
                4,
            ),
            "matched_terms": matched_terms,
            "missing_terms": missing_terms,
            "document_id": evidence.get(
                "document_id"
            ),
            "chunk_id": evidence.get(
                "chunk_id"
            ),
        }

    # --------------------------------------------------------------
    # Stage 3: guarded semantic paraphrase rescue
    # --------------------------------------------------------------

    if semantic_rescue:
        semantic_score = (
            _semantic_similarity(
                claim_text,
                semantic_evidence_text,
            )
        )

        if (
            semantic_score
            >= semantic_rescue_threshold
        ):
            return {
                "claim_id": claim_id,
                "claim_text": claim_text,
                "status": "SUPPORTED",
                "reason": (
                    "Lexical support was below threshold, "
                    "but the claim passed high-risk guards "
                    "and met the semantic paraphrase-rescue "
                    "threshold."
                ),
                "support_ratio": round(
                    support_ratio,
                    4,
                ),
                "matched_terms": matched_terms,
                "missing_terms": missing_terms,
                "document_id": evidence.get(
                    "document_id"
                ),
                "chunk_id": evidence.get(
                    "chunk_id"
                ),
                "semantic_score": round(
                    semantic_score,
                    4,
                ),
                "verification_method": (
                    "guarded_semantic_rescue"
                ),
            }

    # --------------------------------------------------------------
    # Stage 4: unresolved evidence
    # --------------------------------------------------------------

    if support_ratio > 0:
        status = (
            "PARTIALLY_SUPPORTED"
        )

        reason = (
            "Cited evidence supports part of the claim "
            "but the claim did not qualify for safe "
            "semantic rescue."
        )

    else:
        status = "UNSUPPORTED"

        reason = (
            "Cited evidence does not contain sufficient "
            "material support for the claim."
        )

    return {
        "claim_id": claim_id,
        "claim_text": claim_text,
        "status": status,
        "reason": reason,
        "support_ratio": round(
            support_ratio,
            4,
        ),
        "matched_terms": matched_terms,
        "missing_terms": missing_terms,
        "document_id": evidence.get(
            "document_id"
        ),
        "chunk_id": evidence.get(
            "chunk_id"
        ),
    }


def verify_answer_citations(
    claims: list[dict[str, Any]],
    evidence_items: list[dict[str, Any]],
    *,
    support_threshold: float = DEFAULT_SUPPORT_THRESHOLD,
    semantic_rescue: bool = True,
    semantic_rescue_threshold: float = (
        DEFAULT_SEMANTIC_RESCUE_THRESHOLD
    ),
) -> dict[str, Any]:
    """Verify all claims in a generated answer.

    Returns individual claim results plus an answer-level governance decision.
    """

    if not isinstance(
        claims,
        list,
    ):
        raise TypeError(
            "claims must be a list"
        )

    if not isinstance(
        evidence_items,
        list,
    ):
        raise TypeError(
            "evidence_items must be a list"
        )

    evidence_lookup: dict[
        tuple[Any, Any],
        dict[str, Any],
    ] = {}

    for evidence in evidence_items:
        if not isinstance(
            evidence,
            dict,
        ):
            raise TypeError(
                "each evidence item must be a dictionary"
            )

        key = (
            evidence.get(
                "document_id"
            ),
            evidence.get(
                "chunk_id"
            ),
        )

        evidence_lookup[
            key
        ] = evidence

    claim_results = []

    for claim in claims:
        citation = claim.get(
            "citation"
        )

        evidence = None

        if isinstance(
            citation,
            dict,
        ):
            key = (
                citation.get(
                    "document_id"
                ),
                citation.get(
                    "chunk_id"
                ),
            )

            evidence = (
                evidence_lookup.get(
                    key
                )
            )

        result = (
            verify_claim_citation(
                claim,
                evidence,
                support_threshold=(
                    support_threshold
                ),
                semantic_rescue=(
                    semantic_rescue
                ),
                semantic_rescue_threshold=(
                    semantic_rescue_threshold
                ),
            )
        )

        claim_results.append(
            result
        )

    statuses = {
        result["status"]
        for result in claim_results
    }

    if not claim_results:
        decision = "ABSTAIN"

        reason = (
            "No answer claims were supplied for verification."
        )

    elif statuses == {
        "SUPPORTED"
    }:
        decision = "PASS"

        reason = (
            "All material answer claims are supported "
            "by lifecycle-safe cited evidence."
        )

    elif (
        "UNSUPPORTED"
        in statuses
    ):
        decision = (
            "REVIEW_REQUIRED"
        )

        reason = (
            "At least one answer claim is unsupported."
        )

    elif (
        "CITATION_MISMATCH"
        in statuses
    ):
        decision = (
            "REVIEW_REQUIRED"
        )

        reason = (
            "At least one answer claim has a citation mismatch."
        )

    elif (
        "PARTIALLY_SUPPORTED"
        in statuses
    ):
        decision = (
            "REVIEW_REQUIRED"
        )

        reason = (
            "At least one answer claim is only partially supported."
        )

    else:
        decision = (
            "REVIEW_REQUIRED"
        )

        reason = (
            "Answer requires human review."
        )

    return {
        "decision": decision,
        "reason": reason,
        "claim_count": len(
            claim_results
        ),
        "claim_results": (
            claim_results
        ),
    }