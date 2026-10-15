"""Deterministic multi-source relationship-claim verification.

Week 25 Day 3.

This module verifies relational claims whose meaning depends on more than one
approved evidence source.

Examples:

- two approved documents conflict;
- one document replaces another;
- one document takes precedence over another.

The module does not infer relationships from semantic similarity.

Instead it requires:

1. approved citation IDs;
2. citation-to-evidence identity preservation;
3. Active lifecycle state;
4. complete required citation coverage;
5. an explicit relationship established by Evidence Precedence;
6. claim wording consistent with that relationship.

This module complements the existing single-citation verifier. It does not
replace it.
"""

from __future__ import annotations

from typing import Any


SUPPORTED = "SUPPORTED"
PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
UNSUPPORTED = "UNSUPPORTED"
CITATION_MISMATCH = "CITATION_MISMATCH"


CONFLICT = "CONFLICT"
REPLACES = "REPLACES"
TAKES_PRECEDENCE = "TAKES_PRECEDENCE"


SUPPORTED_RELATIONSHIP_TYPES = {
    CONFLICT,
    REPLACES,
    TAKES_PRECEDENCE,
}


RELATIONSHIP_REQUIRED_PRECEDENCE = {
    CONFLICT: "BLOCK_COMBINATION",
    REPLACES: "REVIEW_BEFORE_COMBINATION",
    TAKES_PRECEDENCE: "REVIEW_BEFORE_COMBINATION",
}


RELATIONSHIP_CLAIM_TERMS = {
    CONFLICT: {
        "conflict",
        "conflicts",
        "conflicting",
        "inconsistent",
        "inconsistency",
        "disagree",
        "disagrees",
        "disagreement",
    },
    REPLACES: {
        "replace",
        "replaces",
        "replaced",
        "replacement",
        "supersede",
        "supersedes",
        "superseded",
    },
    TAKES_PRECEDENCE: {
        "precedence",
        "priority",
        "prevails",
        "override",
        "overrides",
        "takes precedence",
    },
}


def _require_mapping(
    value: Any,
    field_name: str,
) -> dict:
    """Require a dictionary."""

    if not isinstance(
        value,
        dict,
    ):
        raise TypeError(
            f"{field_name} must be a dictionary"
        )

    return value


def _require_list(
    value: Any,
    field_name: str,
) -> list:
    """Require a list."""

    if not isinstance(
        value,
        list,
    ):
        raise TypeError(
            f"{field_name} must be a list"
        )

    return value


def _require_non_empty_string(
    value: Any,
    field_name: str,
) -> str:
    """Require a non-empty string."""

    if not isinstance(
        value,
        str,
    ):
        raise TypeError(
            f"{field_name} must be a string"
        )

    cleaned = value.strip()

    if not cleaned:
        raise ValueError(
            f"{field_name} must not be blank"
        )

    return cleaned


def _normalise_text(
    value: str,
) -> str:
    """Normalise text for deterministic relationship wording checks."""

    return " ".join(
        value.lower().strip().split()
    )


def _normalise_unique_ids(
    values: list,
    field_name: str,
) -> list[str]:
    """Validate and de-duplicate citation identifiers."""

    cleaned = []

    seen = set()

    for value in values:
        item = _require_non_empty_string(
            value,
            field_name,
        )

        if item in seen:
            continue

        seen.add(
            item
        )

        cleaned.append(
            item
        )

    return cleaned


def _build_citation_lookup(
    citation_index: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Build approved citation lookup."""

    lookup = {}

    for citation in citation_index:
        citation = _require_mapping(
            citation,
            "citation index item",
        )

        citation_id = (
            _require_non_empty_string(
                citation.get(
                    "citation_id"
                ),
                "citation.citation_id",
            )
        )

        if citation_id in lookup:
            raise ValueError(
                "Duplicate citation ID in citation index: "
                f"{citation_id}"
            )

        lookup[
            citation_id
        ] = citation

    return lookup


def _claim_matches_relationship_type(
    claim_text: str,
    relationship_type: str,
) -> bool:
    """Require claim wording that actually asserts the relationship."""

    normalised_claim = (
        _normalise_text(
            claim_text
        )
    )

    terms = (
        RELATIONSHIP_CLAIM_TERMS[
            relationship_type
        ]
    )

    return any(
        term in normalised_claim
        for term in terms
    )


def _citation_matches_evidence(
    citation: dict[str, Any],
    evidence: dict[str, Any],
) -> bool:
    """Require citation source identity to match supplied evidence."""

    if (
        citation.get(
            "document_id"
        )
        != evidence.get(
            "document_id"
        )
    ):
        return False

    citation_chunk_id = citation.get(
        "chunk_id"
    )

    evidence_chunk_id = evidence.get(
        "chunk_id"
    )

    if (
        citation_chunk_id
        != evidence_chunk_id
    ):
        return False

    return True


def _evidence_is_active(
    evidence: dict[str, Any],
) -> bool:
    """Require Active lifecycle state."""

    status = evidence.get(
        "status"
    )

    if not isinstance(
        status,
        str,
    ):
        return False

    return (
        status.strip().lower()
        == "active"
    )


def _relationship_is_established(
    precedence_assessment: dict[str, Any],
    relationship_type: str,
    required_document_ids: set[str],
) -> bool:
    """Check Evidence Precedence for an explicit supported relationship."""

    relationship_checks = _require_list(
        precedence_assessment.get(
            "relationship_checks",
            [],
        ),
        "precedence_assessment.relationship_checks",
    )

    for check in relationship_checks:
        check = _require_mapping(
            check,
            "relationship check",
        )

        if (
            check.get(
                "relationship_type"
            )
            != relationship_type
        ):
            continue

        if (
            check.get(
                "decision"
            )
            != "RELATIONSHIP_SUPPORTED"
        ):
            continue

        document_ids = check.get(
            "document_ids",
            [],
        )

        if not isinstance(
            document_ids,
            list,
        ):
            continue

        cleaned_document_ids = {
            document_id.strip()
            for document_id
            in document_ids
            if isinstance(
                document_id,
                str,
            )
            and document_id.strip()
        }

        if (
            required_document_ids
            <= cleaned_document_ids
        ):
            return True

    return False


def verify_multi_source_relationship_claim(
    claim: dict[str, Any],
    citation_index: list[dict[str, Any]],
    evidence_by_citation_id: dict[
        str,
        dict[str, Any],
    ],
    precedence_assessment: dict[str, Any],
    *,
    relationship_type: str,
    required_citation_ids: list[str],
) -> dict[str, Any]:
    """Verify one governed multi-source relationship claim."""

    claim = _require_mapping(
        claim,
        "claim",
    )

    citation_index = _require_list(
        citation_index,
        "citation_index",
    )

    evidence_by_citation_id = (
        _require_mapping(
            evidence_by_citation_id,
            "evidence_by_citation_id",
        )
    )

    precedence_assessment = (
        _require_mapping(
            precedence_assessment,
            "precedence_assessment",
        )
    )

    claim_id = _require_non_empty_string(
        claim.get(
            "claim_id"
        ),
        "claim.claim_id",
    )

    claim_text = _require_non_empty_string(
        claim.get(
            "claim_text"
        ),
        "claim.claim_text",
    )

    relationship_type = (
        _require_non_empty_string(
            relationship_type,
            "relationship_type",
        )
    )

    if (
        relationship_type
        not in SUPPORTED_RELATIONSHIP_TYPES
    ):
        raise ValueError(
            "Unsupported relationship_type: "
            f"{relationship_type}"
        )

    attached_citation_ids = (
        _normalise_unique_ids(
            _require_list(
                claim.get(
                    "citation_ids",
                    [],
                ),
                "claim.citation_ids",
            ),
            "claim citation ID",
        )
    )

    required_citation_ids = (
        _normalise_unique_ids(
            _require_list(
                required_citation_ids,
                "required_citation_ids",
            ),
            "required citation ID",
        )
    )

    if len(
        required_citation_ids
    ) < 2:
        raise ValueError(
            "Multi-source relationship verification "
            "requires at least two required citations."
        )

    citation_lookup = (
        _build_citation_lookup(
            citation_index
        )
    )

    unknown_required = [
        citation_id
        for citation_id
        in required_citation_ids
        if citation_id
        not in citation_lookup
    ]

    if unknown_required:
        return {
            "claim_id": claim_id,
            "status": CITATION_MISMATCH,
            "reason": (
                "Required citation IDs are not present "
                "in the approved citation index."
            ),
            "relationship_type": (
                relationship_type
            ),
            "required_citation_ids": (
                required_citation_ids
            ),
            "attached_citation_ids": (
                attached_citation_ids
            ),
            "missing_citation_ids": [],
            "invalid_citation_ids": (
                unknown_required
            ),
        }

    unknown_attached = [
        citation_id
        for citation_id
        in attached_citation_ids
        if citation_id
        not in citation_lookup
    ]

    if unknown_attached:
        return {
            "claim_id": claim_id,
            "status": CITATION_MISMATCH,
            "reason": (
                "Claim contains citation IDs that are "
                "not approved by the Answer Context."
            ),
            "relationship_type": (
                relationship_type
            ),
            "required_citation_ids": (
                required_citation_ids
            ),
            "attached_citation_ids": (
                attached_citation_ids
            ),
            "missing_citation_ids": [],
            "invalid_citation_ids": (
                unknown_attached
            ),
        }

    missing_citation_ids = [
        citation_id
        for citation_id
        in required_citation_ids
        if citation_id
        not in attached_citation_ids
    ]

    if missing_citation_ids:
        return {
            "claim_id": claim_id,
            "status": PARTIALLY_SUPPORTED,
            "reason": (
                "The relational claim does not include "
                "every required approved citation."
            ),
            "relationship_type": (
                relationship_type
            ),
            "required_citation_ids": (
                required_citation_ids
            ),
            "attached_citation_ids": (
                attached_citation_ids
            ),
            "missing_citation_ids": (
                missing_citation_ids
            ),
            "invalid_citation_ids": [],
        }

    evidence_items = []

    required_document_ids = set()

    for citation_id in required_citation_ids:
        citation = citation_lookup[
            citation_id
        ]

        evidence = (
            evidence_by_citation_id.get(
                citation_id
            )
        )

        if not isinstance(
            evidence,
            dict,
        ):
            return {
                "claim_id": claim_id,
                "status": CITATION_MISMATCH,
                "reason": (
                    "A required citation does not resolve "
                    "to supplied evidence."
                ),
                "relationship_type": (
                    relationship_type
                ),
                "required_citation_ids": (
                    required_citation_ids
                ),
                "attached_citation_ids": (
                    attached_citation_ids
                ),
                "missing_citation_ids": [],
                "invalid_citation_ids": [
                    citation_id
                ],
            }

        if not _citation_matches_evidence(
            citation,
            evidence,
        ):
            return {
                "claim_id": claim_id,
                "status": CITATION_MISMATCH,
                "reason": (
                    "Citation source identity does not "
                    "match supplied evidence."
                ),
                "relationship_type": (
                    relationship_type
                ),
                "required_citation_ids": (
                    required_citation_ids
                ),
                "attached_citation_ids": (
                    attached_citation_ids
                ),
                "missing_citation_ids": [],
                "invalid_citation_ids": [
                    citation_id
                ],
            }

        if not _evidence_is_active(
            evidence
        ):
            return {
                "claim_id": claim_id,
                "status": CITATION_MISMATCH,
                "reason": (
                    "Multi-source relationship verification "
                    "requires Active evidence."
                ),
                "relationship_type": (
                    relationship_type
                ),
                "required_citation_ids": (
                    required_citation_ids
                ),
                "attached_citation_ids": (
                    attached_citation_ids
                ),
                "missing_citation_ids": [],
                "invalid_citation_ids": [
                    citation_id
                ],
            }

        document_id = (
            _require_non_empty_string(
                evidence.get(
                    "document_id"
                ),
                "evidence.document_id",
            )
        )

        required_document_ids.add(
            document_id
        )

        evidence_items.append(
            evidence
        )

    expected_precedence = (
        RELATIONSHIP_REQUIRED_PRECEDENCE[
            relationship_type
        ]
    )

    actual_precedence = (
        precedence_assessment.get(
            "decision"
        )
    )

    if (
        actual_precedence
        != expected_precedence
    ):
        return {
            "claim_id": claim_id,
            "status": UNSUPPORTED,
            "reason": (
                "Evidence Precedence does not establish "
                "the required governed relationship state."
            ),
            "relationship_type": (
                relationship_type
            ),
            "required_citation_ids": (
                required_citation_ids
            ),
            "attached_citation_ids": (
                attached_citation_ids
            ),
            "missing_citation_ids": [],
            "invalid_citation_ids": [],
        }

    if not _relationship_is_established(
        precedence_assessment,
        relationship_type,
        required_document_ids,
    ):
        return {
            "claim_id": claim_id,
            "status": UNSUPPORTED,
            "reason": (
                "The required explicit relationship was "
                "not established by Evidence Precedence."
            ),
            "relationship_type": (
                relationship_type
            ),
            "required_citation_ids": (
                required_citation_ids
            ),
            "attached_citation_ids": (
                attached_citation_ids
            ),
            "missing_citation_ids": [],
            "invalid_citation_ids": [],
        }

    if not _claim_matches_relationship_type(
        claim_text,
        relationship_type,
    ):
        return {
            "claim_id": claim_id,
            "status": UNSUPPORTED,
            "reason": (
                "Claim wording does not assert the "
                "verified relationship type."
            ),
            "relationship_type": (
                relationship_type
            ),
            "required_citation_ids": (
                required_citation_ids
            ),
            "attached_citation_ids": (
                attached_citation_ids
            ),
            "missing_citation_ids": [],
            "invalid_citation_ids": [],
        }

    return {
        "claim_id": claim_id,
        "status": SUPPORTED,
        "reason": (
            "The multi-source claim preserves all required "
            "approved citations and matches an explicit "
            "relationship established by Evidence Precedence."
        ),
        "relationship_type": (
            relationship_type
        ),
        "required_citation_ids": (
            required_citation_ids
        ),
        "attached_citation_ids": (
            attached_citation_ids
        ),
        "missing_citation_ids": [],
        "invalid_citation_ids": [],
        "document_ids": sorted(
            required_document_ids
        ),
        "evidence_count": len(
            evidence_items
        ),
        "precedence_decision": (
            actual_precedence
        ),
    }