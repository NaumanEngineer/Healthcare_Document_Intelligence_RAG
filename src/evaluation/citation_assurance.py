"""Integrated citation assurance.

Week 25 Day 3.

This module connects:

Answer Context
→ Claim-Citation Linkage
→ Citation Completeness Audit

Its job is to validate that claim-linked citations originate from the approved
Answer Context citation index and that material claims satisfy their citation
support contract.

It does not perform semantic entailment.
It does not replace citation verification.
It does not override evidence lifecycle, precedence, or governance.
"""

from __future__ import annotations

from typing import Any

from src.evaluation.citation_completeness import (
    audit_answer_citation_completeness,
)


REQUIRED_CITATION_SOURCE_FIELDS = (
    "citation_id",
    "evidence_id",
    "document_id",
    "chunk_id",
    "page",
    "source_file",
    "version",
    "status",
)


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


def _validate_positive_page(
    value: Any,
) -> int:
    """Require a positive page number."""

    if (
        not isinstance(
            value,
            int,
        )
        or isinstance(
            value,
            bool,
        )
        or value <= 0
    ):
        raise ValueError(
            "citation.page must be a positive integer"
        )

    return value


def _validate_shared_state(
    claim_linkage: dict[str, Any],
    answer_context: dict[str, Any],
) -> tuple[
    str,
    str,
    str,
]:
    """Ensure linkage and Answer Context describe the same governed answer."""

    linkage_packet_id = (
        _require_non_empty_string(
            claim_linkage.get(
                "packet_id"
            ),
            "claim_linkage.packet_id",
        )
    )

    context_packet_id = (
        _require_non_empty_string(
            answer_context.get(
                "packet_id"
            ),
            "answer_context.packet_id",
        )
    )

    if (
        linkage_packet_id
        != context_packet_id
    ):
        raise ValueError(
            "Claim Linkage and Answer Context "
            "packet IDs do not match"
        )

    linkage_governance = (
        _require_non_empty_string(
            claim_linkage.get(
                "governance_decision"
            ),
            "claim_linkage.governance_decision",
        )
    )

    context_governance = (
        _require_non_empty_string(
            answer_context.get(
                "governance_decision"
            ),
            "answer_context.governance_decision",
        )
    )

    if (
        linkage_governance
        != context_governance
    ):
        raise ValueError(
            "Claim Linkage and Answer Context "
            "governance decisions do not match"
        )

    linkage_response_type = (
        _require_non_empty_string(
            claim_linkage.get(
                "response_type"
            ),
            "claim_linkage.response_type",
        )
    )

    context_response_type = (
        _require_non_empty_string(
            answer_context.get(
                "response_type"
            ),
            "answer_context.response_type",
        )
    )

    if (
        linkage_response_type
        != context_response_type
    ):
        raise ValueError(
            "Claim Linkage and Answer Context "
            "response types do not match"
        )

    return (
        linkage_packet_id,
        linkage_governance,
        linkage_response_type,
    )


def _validate_citation_index(
    citation_index: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Validate approved citation-source records and build lookup."""

    lookup = {}

    for citation in citation_index:
        citation = _require_mapping(
            citation,
            "citation_index item",
        )

        missing = []

        for field in REQUIRED_CITATION_SOURCE_FIELDS:
            if field not in citation:
                missing.append(
                    field
                )

        if missing:
            raise ValueError(
                "Citation index item is missing required "
                "source fields: "
                + ", ".join(
                    missing
                )
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
                "Duplicate citation ID in Answer Context: "
                f"{citation_id}"
            )

        for field in (
            "evidence_id",
            "document_id",
            "chunk_id",
            "source_file",
            "version",
            "status",
        ):
            _require_non_empty_string(
                citation.get(
                    field
                ),
                f"citation.{field}",
            )

        _validate_positive_page(
            citation.get(
                "page"
            )
        )

        lookup[
            citation_id
        ] = citation

    return lookup


def _validate_claims(
    claims: list[dict[str, Any]],
) -> tuple[
    list[dict[str, Any]],
    list[str],
]:
    """Validate linkage claims and identify non-substantive claims."""

    validated_claims = []

    non_substantive_claim_ids = []

    seen_claim_ids = set()

    for claim in claims:
        claim = _require_mapping(
            claim,
            "claim",
        )

        claim_id = (
            _require_non_empty_string(
                claim.get(
                    "claim_id"
                ),
                "claim.claim_id",
            )
        )

        if claim_id in seen_claim_ids:
            raise ValueError(
                "Duplicate claim ID in Claim Linkage: "
                f"{claim_id}"
            )

        seen_claim_ids.add(
            claim_id
        )

        claim_text = (
            _require_non_empty_string(
                claim.get(
                    "claim_text"
                ),
                "claim.claim_text",
            )
        )

        support_status = (
            _require_non_empty_string(
                claim.get(
                    "support_status"
                ),
                "claim.support_status",
            )
        )

        citation_ids = _require_list(
            claim.get(
                "citation_ids",
                [],
            ),
            "claim.citation_ids",
        )

        cleaned_citation_ids = []

        seen_citation_ids = set()

        for citation_id in citation_ids:
            citation_id = (
                _require_non_empty_string(
                    citation_id,
                    "claim citation ID",
                )
            )

            if citation_id in seen_citation_ids:
                continue

            seen_citation_ids.add(
                citation_id
            )

            cleaned_citation_ids.append(
                citation_id
            )

        validated_claim = {
            **claim,
            "claim_id": claim_id,
            "claim_text": claim_text,
            "support_status": support_status,
            "citation_ids": (
                cleaned_citation_ids
            ),
        }

        validated_claims.append(
            validated_claim
        )

        if support_status == "NON_SUBSTANTIVE":
            non_substantive_claim_ids.append(
                claim_id
            )

    return (
        validated_claims,
        non_substantive_claim_ids,
    )


def _validate_attached_citation_sources(
    claims: list[dict[str, Any]],
    citation_lookup: dict[
        str,
        dict[str, Any],
    ],
) -> None:
    """Fail closed if linked claims reference unapproved citation IDs."""

    for claim in claims:
        for citation_id in claim[
            "citation_ids"
        ]:
            if citation_id not in citation_lookup:
                raise ValueError(
                    "Claim references citation ID "
                    "that is not present in approved "
                    "Answer Context: "
                    f"{citation_id}"
                )


def build_citation_assurance(
    claim_linkage: dict[str, Any],
    answer_context: dict[str, Any],
    *,
    required_citations_by_claim: dict[
        str,
        list[str],
    ] | None = None,
) -> dict[str, Any]:
    """Build integrated citation-completeness assurance.

    Parameters
    ----------
    claim_linkage:
        Output of build_claim_citation_links().

    answer_context:
        Approved Answer Context containing the canonical citation index.

    required_citations_by_claim:
        Optional support contract mapping.

        Example:

        {
            "C1": ["E1", "E2"]
        }

        This is particularly important for relational or multi-source claims.
    """

    claim_linkage = _require_mapping(
        claim_linkage,
        "claim_linkage",
    )

    answer_context = _require_mapping(
        answer_context,
        "answer_context",
    )

    (
        packet_id,
        governance_decision,
        response_type,
    ) = _validate_shared_state(
        claim_linkage,
        answer_context,
    )

    citation_index = _require_list(
        answer_context.get(
            "citation_index"
        ),
        "answer_context.citation_index",
    )

    citation_lookup = (
        _validate_citation_index(
            citation_index
        )
    )

    claims = _require_list(
        claim_linkage.get(
            "claims"
        ),
        "claim_linkage.claims",
    )

    (
        validated_claims,
        non_substantive_claim_ids,
    ) = _validate_claims(
        claims
    )

    _validate_attached_citation_sources(
        validated_claims,
        citation_lookup,
    )

    if required_citations_by_claim is None:
        required_citations_by_claim = {}

    required_citations_by_claim = (
        _require_mapping(
            required_citations_by_claim,
            "required_citations_by_claim",
        )
    )

    completeness = (
        audit_answer_citation_completeness(
            validated_claims,
            citation_index,
            required_citations_by_claim=(
                required_citations_by_claim
            ),
            non_substantive_claim_ids=(
                non_substantive_claim_ids
            ),
            upstream_governance_decision=(
                governance_decision
            ),
        )
    )

    return {
        "assurance_version": "1.0",
        "packet_id": packet_id,
        "governance_decision": (
            governance_decision
        ),
        "response_type": (
            response_type
        ),
        "citation_source_count": len(
            citation_index
        ),
        "claim_count": len(
            validated_claims
        ),
        "material_claim_count": (
            completeness[
                "material_claim_count"
            ]
        ),
        "citation_completeness": (
            completeness
        ),
        "decision": (
            completeness[
                "decision"
            ]
        ),
        "safety_summary": {
            "packet_identity_preserved": True,
            "governance_preserved": True,
            "response_type_preserved": True,
            "citation_index_validated": True,
            "citation_sources_preserved": True,
            "unknown_citations_fail_closed": True,
            "governance_upgrade_performed": False,
        },
    }