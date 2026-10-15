"""Deterministic citation completeness auditing.

Week 25 Day 3.

This module checks whether material answer claims contain the citations
required by their evidence contract.

It does not decide semantic entailment.
It does not override citation verification.
It does not override lifecycle, precedence, or governance.

Core distinction:

Citation correctness:
    Does a citation resolve to approved evidence and support the claim?

Citation completeness:
    Does the material claim contain every citation required for its support
    contract?

This layer is intentionally deterministic.
"""

from __future__ import annotations

from typing import Any


COMPLETE = "COMPLETE"
INCOMPLETE = "INCOMPLETE"
UNCITED = "UNCITED"
INVALID_CITATION = "INVALID_CITATION"
NOT_REQUIRED = "NOT_REQUIRED"

PASS = "PASS"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
ABSTAIN = "ABSTAIN"


VALID_CLAIM_COMPLETENESS_STATUSES = {
    COMPLETE,
    INCOMPLETE,
    UNCITED,
    INVALID_CITATION,
    NOT_REQUIRED,
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


def _normalise_unique_strings(
    values: list,
    field_name: str,
) -> list[str]:
    """Validate and de-duplicate string identifiers deterministically."""

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
    citation_index: list[dict],
) -> dict[str, dict]:
    """Create validated citation lookup from approved citation index."""

    lookup = {}

    for citation in citation_index:
        citation = _require_mapping(
            citation,
            "citation_index item",
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


def _validate_required_citations(
    required_citation_ids: list[str],
    citation_lookup: dict[str, dict],
) -> None:
    """Ensure benchmark or support contract does not require unknown sources."""

    for citation_id in required_citation_ids:
        if citation_id not in citation_lookup:
            raise ValueError(
                "Required citation ID does not exist "
                "in approved citation index: "
                f"{citation_id}"
            )


def audit_claim_citation_completeness(
    claim: dict[str, Any],
    citation_index: list[dict[str, Any]],
    *,
    required_citation_ids: list[str] | None = None,
    material: bool = True,
) -> dict[str, Any]:
    """Audit one claim for citation completeness.

    Parameters
    ----------
    claim:
        Claim record. It may contain either:

        citation_ids: ["E1", "E2"]

        or, for legacy verifier compatibility:

        citation: {
            "citation_id": "E1"
        }

        or:

        citation: {
            "document_id": "...",
            "chunk_id": "..."
        }

        The completeness auditor only treats citation IDs as complete
        citation references. Document/chunk-only citation objects remain
        compatible with the older verifier but do not establish benchmark
        citation-ID completeness.

    citation_index:
        Approved Answer Context citation index.

    required_citation_ids:
        Explicit citation set required to support this claim.

        If omitted, every attached valid citation is treated as the support
        contract for a material claim. This preserves backward compatibility
        for ordinary single-source claims.

    material:
        False only for genuinely non-substantive statements.
    """

    claim = _require_mapping(
        claim,
        "claim",
    )

    citation_index = _require_list(
        citation_index,
        "citation_index",
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

    citation_lookup = (
        _build_citation_lookup(
            citation_index
        )
    )

    if not isinstance(
        material,
        bool,
    ):
        raise TypeError(
            "material must be a boolean"
        )

    if not material:
        return {
            "claim_id": claim_id,
            "claim_text": claim_text,
            "material": False,
            "status": NOT_REQUIRED,
            "reason": (
                "Claim is classified as non-substantive "
                "and does not require evidence citation."
            ),
            "attached_citation_ids": [],
            "required_citation_ids": [],
            "missing_citation_ids": [],
            "invalid_citation_ids": [],
        }

    attached_citation_ids = []

    claim_citation_ids = claim.get(
        "citation_ids"
    )

    if claim_citation_ids is not None:
        claim_citation_ids = _require_list(
            claim_citation_ids,
            "claim.citation_ids",
        )

        attached_citation_ids = (
            _normalise_unique_strings(
                claim_citation_ids,
                "claim citation ID",
            )
        )

    elif isinstance(
        claim.get(
            "citation"
        ),
        dict,
    ):
        legacy_citation = claim[
            "citation"
        ]

        citation_id = legacy_citation.get(
            "citation_id"
        )

        if citation_id is not None:
            attached_citation_ids = [
                _require_non_empty_string(
                    citation_id,
                    "claim.citation.citation_id",
                )
            ]

    if required_citation_ids is None:
        required_citation_ids = list(
            attached_citation_ids
        )

    else:
        required_citation_ids = (
            _normalise_unique_strings(
                _require_list(
                    required_citation_ids,
                    "required_citation_ids",
                ),
                "required citation ID",
            )
        )

    _validate_required_citations(
        required_citation_ids,
        citation_lookup,
    )

    invalid_citation_ids = [
        citation_id
        for citation_id
        in attached_citation_ids
        if citation_id
        not in citation_lookup
    ]

    if invalid_citation_ids:
        return {
            "claim_id": claim_id,
            "claim_text": claim_text,
            "material": True,
            "status": INVALID_CITATION,
            "reason": (
                "Claim contains citation IDs that are not "
                "present in the approved citation index."
            ),
            "attached_citation_ids": (
                attached_citation_ids
            ),
            "required_citation_ids": (
                required_citation_ids
            ),
            "missing_citation_ids": [],
            "invalid_citation_ids": (
                invalid_citation_ids
            ),
        }

    if not attached_citation_ids:
        return {
            "claim_id": claim_id,
            "claim_text": claim_text,
            "material": True,
            "status": UNCITED,
            "reason": (
                "Material claim contains no citation IDs."
            ),
            "attached_citation_ids": [],
            "required_citation_ids": (
                required_citation_ids
            ),
            "missing_citation_ids": list(
                required_citation_ids
            ),
            "invalid_citation_ids": [],
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
            "claim_text": claim_text,
            "material": True,
            "status": INCOMPLETE,
            "reason": (
                "Material claim is missing one or more "
                "required citations."
            ),
            "attached_citation_ids": (
                attached_citation_ids
            ),
            "required_citation_ids": (
                required_citation_ids
            ),
            "missing_citation_ids": (
                missing_citation_ids
            ),
            "invalid_citation_ids": [],
        }

    return {
        "claim_id": claim_id,
        "claim_text": claim_text,
        "material": True,
        "status": COMPLETE,
        "reason": (
            "Material claim contains every citation "
            "required by its support contract."
        ),
        "attached_citation_ids": (
            attached_citation_ids
        ),
        "required_citation_ids": (
            required_citation_ids
        ),
        "missing_citation_ids": [],
        "invalid_citation_ids": [],
    }


def audit_answer_citation_completeness(
    claims: list[dict[str, Any]],
    citation_index: list[dict[str, Any]],
    *,
    required_citations_by_claim: dict[
        str,
        list[str],
    ] | None = None,
    non_substantive_claim_ids: list[str] | None = None,
    upstream_governance_decision: str | None = None,
) -> dict[str, Any]:
    """Audit citation completeness across all answer claims."""

    claims = _require_list(
        claims,
        "claims",
    )

    citation_index = _require_list(
        citation_index,
        "citation_index",
    )

    _build_citation_lookup(
        citation_index
    )

    if required_citations_by_claim is None:
        required_citations_by_claim = {}

    required_citations_by_claim = (
        _require_mapping(
            required_citations_by_claim,
            "required_citations_by_claim",
        )
    )

    if non_substantive_claim_ids is None:
        non_substantive_claim_ids = []

    non_substantive_claim_ids = (
        _normalise_unique_strings(
            _require_list(
                non_substantive_claim_ids,
                "non_substantive_claim_ids",
            ),
            "non-substantive claim ID",
        )
    )

    non_substantive_set = set(
        non_substantive_claim_ids
    )

    claim_results = []

    for claim in claims:
        claim = _require_mapping(
            claim,
            "claim",
        )

        claim_id = _require_non_empty_string(
            claim.get(
                "claim_id"
            ),
            "claim.claim_id",
        )

        required_citations = (
            required_citations_by_claim.get(
                claim_id
            )
        )

        result = (
            audit_claim_citation_completeness(
                claim,
                citation_index,
                required_citation_ids=(
                    required_citations
                ),
                material=(
                    claim_id
                    not in non_substantive_set
                ),
            )
        )

        claim_results.append(
            result
        )

    material_results = [
        result
        for result
        in claim_results
        if result[
            "material"
        ]
    ]

    if (
        upstream_governance_decision
        == "ABSTAIN"
        and not material_results
    ):
        decision = ABSTAIN

        reason = (
            "Upstream governance requires abstention "
            "and no material claims require citation assurance."
        )

    elif not material_results:
        decision = PASS

        reason = (
            "No material claims require citation completeness auditing."
        )

    elif all(
        result[
            "status"
        ]
        == COMPLETE
        for result
        in material_results
    ):
        decision = PASS

        reason = (
            "Every material claim contains all required "
            "approved citations."
        )

    else:
        decision = REVIEW_REQUIRED

        reason = (
            "At least one material claim is uncited, "
            "citation-incomplete, or contains an invalid citation."
        )

    status_counts = {
        status: sum(
            1
            for result
            in claim_results
            if result[
                "status"
            ]
            == status
        )
        for status
        in (
            COMPLETE,
            INCOMPLETE,
            UNCITED,
            INVALID_CITATION,
            NOT_REQUIRED,
        )
    }

    return {
        "decision": decision,
        "reason": reason,
        "claim_count": len(
            claim_results
        ),
        "material_claim_count": len(
            material_results
        ),
        "claim_results": (
            claim_results
        ),
        "status_counts": (
            status_counts
        ),
        "safety_summary": {
            "citation_index_validated": True,
            "required_citation_sets_preserved": True,
            "governance_upgrade_performed": False,
        },
    }