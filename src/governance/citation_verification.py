"""Deterministic citation verification for grounded RAG answers.

This module performs a simple post-generation safety check.

It verifies whether:
- an answer claim has cited evidence;
- the cited document/chunk exists;
- the cited evidence is lifecycle-safe;
- the material claim terms are represented in the cited evidence.

This is intentionally a deterministic prototype.

It does not perform full natural-language entailment and should not be treated
as proof that a claim is factually correct.
"""

from __future__ import annotations

import re
from typing import Any


VALID_LIFECYCLE_STATUSES = {"active"}


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


def _get_evidence_text(evidence: dict[str, Any]) -> str:
    """Combine evidence fields used for support checking."""

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


def _citation_matches_evidence(
    citation: dict[str, Any],
    evidence: dict[str, Any],
) -> bool:
    """Check that citation identifiers match the supplied evidence."""

    citation_document_id = citation.get("document_id")
    evidence_document_id = evidence.get("document_id")

    if citation_document_id != evidence_document_id:
        return False

    citation_chunk_id = citation.get("chunk_id")
    evidence_chunk_id = evidence.get("chunk_id")

    if citation_chunk_id is not None:
        if citation_chunk_id != evidence_chunk_id:
            return False

    return True


def _is_lifecycle_safe(evidence: dict[str, Any]) -> bool:
    """Accept only Active evidence in this prototype."""

    status = evidence.get("status")

    if status is None:
        # Some synthetic unit-test evidence may not yet carry lifecycle
        # metadata. Missing status is treated conservatively by callers that
        # require lifecycle information, but this prototype permits it so the
        # verifier can be introduced incrementally.
        return True

    normalised_status = _normalise(str(status))

    return normalised_status in VALID_LIFECYCLE_STATUSES


def _claim_support_ratio(
    claim_text: str,
    evidence_text: str,
) -> tuple[float, list[str], list[str]]:
    """Calculate lexical coverage of material claim terms."""

    claim_terms = _material_terms(claim_text)
    evidence_terms = _material_terms(evidence_text)

    if not claim_terms:
        return 0.0, [], []

    matched = sorted(
        claim_terms & evidence_terms
    )

    missing = sorted(
        claim_terms - evidence_terms
    )

    ratio = len(matched) / len(claim_terms)

    return ratio, matched, missing


def verify_claim_citation(
    claim: dict[str, Any],
    evidence: dict[str, Any] | None,
    *,
    support_threshold: float = 0.60,
) -> dict[str, Any]:
    """Verify one claim against its cited evidence.

    Expected claim structure:

    {
        "claim_id": "C1",
        "claim_text": "...",
        "citation": {
            "document_id": "DOC-009",
            "chunk_id": "DOC-009-01"
        }
    }

    Expected evidence structure:

    {
        "document_id": "DOC-009",
        "chunk_id": "DOC-009-01",
        "status": "Active",
        "title": "...",
        "text": "..."
    }
    """

    if not isinstance(claim, dict):
        raise TypeError(
            "claim must be a dictionary"
        )

    claim_id = claim.get("claim_id")
    claim_text = claim.get("claim_text")
    citation = claim.get("citation")

    if not isinstance(claim_id, str) or not claim_id.strip():
        raise ValueError(
            "claim must contain a non-blank claim_id"
        )

    if not isinstance(claim_text, str) or not claim_text.strip():
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
                _material_terms(claim_text)
            ),
            "document_id": None,
            "chunk_id": None,
        }

    if not isinstance(citation, dict):
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
                _material_terms(claim_text)
            ),
            "document_id": citation.get(
                "document_id"
            ),
            "chunk_id": citation.get(
                "chunk_id"
            ),
        }

    if not isinstance(evidence, dict):
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
                _material_terms(claim_text)
            ),
            "document_id": citation.get(
                "document_id"
            ),
            "chunk_id": citation.get(
                "chunk_id"
            ),
        }

    if not _is_lifecycle_safe(evidence):
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
                _material_terms(claim_text)
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

    if support_ratio >= support_threshold:
        status = "SUPPORTED"
        reason = (
            "Cited evidence contains sufficient "
            "material lexical support for the claim."
        )

    elif support_ratio > 0:
        status = "PARTIALLY_SUPPORTED"
        reason = (
            "Cited evidence supports part of the claim "
            "but material terms are missing."
        )

    else:
        status = "UNSUPPORTED"
        reason = (
            "Cited evidence does not contain material "
            "support for the claim."
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
    support_threshold: float = 0.60,
) -> dict[str, Any]:
    """Verify all claims in a generated answer.

    Returns individual claim results plus an answer-level governance decision.
    """

    if not isinstance(claims, list):
        raise TypeError(
            "claims must be a list"
        )

    if not isinstance(evidence_items, list):
        raise TypeError(
            "evidence_items must be a list"
        )

    evidence_lookup: dict[
        tuple[Any, Any],
        dict[str, Any],
    ] = {}

    for evidence in evidence_items:
        if not isinstance(evidence, dict):
            raise TypeError(
                "each evidence item must be a dictionary"
            )

        key = (
            evidence.get("document_id"),
            evidence.get("chunk_id"),
        )

        evidence_lookup[key] = evidence

    claim_results = []

    for claim in claims:
        citation = claim.get("citation")

        evidence = None

        if isinstance(citation, dict):
            key = (
                citation.get("document_id"),
                citation.get("chunk_id"),
            )

            evidence = evidence_lookup.get(
                key
            )

        result = verify_claim_citation(
            claim,
            evidence,
            support_threshold=support_threshold,
        )

        claim_results.append(result)

    statuses = {
        result["status"]
        for result in claim_results
    }

    if not claim_results:
        decision = "ABSTAIN"
        reason = (
            "No answer claims were supplied for verification."
        )

    elif statuses == {"SUPPORTED"}:
        decision = "PASS"
        reason = (
            "All material answer claims are supported "
            "by their cited evidence."
        )

    elif "UNSUPPORTED" in statuses:
        decision = "REVIEW_REQUIRED"
        reason = (
            "At least one answer claim is unsupported."
        )

    elif "CITATION_MISMATCH" in statuses:
        decision = "REVIEW_REQUIRED"
        reason = (
            "At least one answer claim has a citation mismatch."
        )

    elif "PARTIALLY_SUPPORTED" in statuses:
        decision = "REVIEW_REQUIRED"
        reason = (
            "At least one answer claim is only partially supported."
        )

    else:
        decision = "REVIEW_REQUIRED"
        reason = (
            "Answer requires human review."
        )

    return {
        "decision": decision,
        "reason": reason,
        "claim_count": len(
            claim_results
        ),
        "claim_results": claim_results,
    }