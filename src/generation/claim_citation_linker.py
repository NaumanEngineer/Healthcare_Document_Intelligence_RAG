"""Week 23 Day 4 — deterministic claim-to-citation linking."""

from __future__ import annotations

from typing import Any


SUPPORTED = "SUPPORTED"
NON_SUBSTANTIVE = "NON_SUBSTANTIVE"
UNSUPPORTED = "UNSUPPORTED"


def _require_mapping(
    value: Any,
    field_name: str,
) -> dict:
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


def _validate_shared_state(
    grounded_response: dict,
    answer_context: dict,
) -> tuple[str, str, str]:
    response_packet_id = _require_non_empty_string(
        grounded_response.get(
            "packet_id"
        ),
        "grounded_response.packet_id",
    )

    context_packet_id = _require_non_empty_string(
        answer_context.get(
            "packet_id"
        ),
        "answer_context.packet_id",
    )

    if (
        response_packet_id
        != context_packet_id
    ):
        raise ValueError(
            "Grounded Response and Answer Context "
            "packet IDs do not match"
        )

    response_governance = _require_non_empty_string(
        grounded_response.get(
            "governance_decision"
        ),
        "grounded_response.governance_decision",
    )

    context_governance = _require_non_empty_string(
        answer_context.get(
            "governance_decision"
        ),
        "answer_context.governance_decision",
    )

    if (
        response_governance
        != context_governance
    ):
        raise ValueError(
            "Grounded Response and Answer Context "
            "governance decisions do not match"
        )

    response_type = _require_non_empty_string(
        grounded_response.get(
            "response_type"
        ),
        "grounded_response.response_type",
    )

    context_response_type = _require_non_empty_string(
        answer_context.get(
            "response_type"
        ),
        "answer_context.response_type",
    )

    if (
        response_type
        != context_response_type
    ):
        raise ValueError(
            "Grounded Response and Answer Context "
            "response types do not match"
        )

    return (
        response_packet_id,
        response_governance,
        response_type,
    )


def _build_citation_lookup(
    answer_context: dict,
) -> dict[str, dict]:
    citation_index = _require_list(
        answer_context.get(
            "citation_index"
        ),
        "answer_context.citation_index",
    )

    lookup = {}

    for citation in citation_index:
        citation = _require_mapping(
            citation,
            "citation item",
        )

        citation_id = _require_non_empty_string(
            citation.get(
                "citation_id"
            ),
            "citation.citation_id",
        )

        if citation_id in lookup:
            raise ValueError(
                "Duplicate citation ID in Answer Context: "
                f"{citation_id}"
            )

        lookup[
            citation_id
        ] = citation

    return lookup


def _validate_response_citations(
    grounded_response: dict,
    citation_lookup: dict[str, dict],
) -> list[str]:
    citations_used = _require_list(
        grounded_response.get(
            "citations_used",
            [],
        ),
        "grounded_response.citations_used",
    )

    validated = []

    for citation_id in citations_used:
        citation_id = _require_non_empty_string(
            citation_id,
            "grounded_response citation ID",
        )

        if citation_id not in citation_lookup:
            raise ValueError(
                "Grounded Response cites unknown "
                f"citation ID: {citation_id}"
            )

        validated.append(
            citation_id
        )

    return validated


def _claim_record(
    claim_id: str,
    claim_text: str,
    section: str,
    citation_ids: list[str],
    support_status: str,
) -> dict:
    return {
        "claim_id": claim_id,
        "claim_text": claim_text,
        "section": section,
        "citation_ids": citation_ids,
        "support_status": support_status,
    }


def _extract_answer_claims(
    grounded_response: dict,
    citation_lookup: dict[str, dict],
) -> list[dict]:
    sections = _require_mapping(
        grounded_response.get(
            "sections"
        ),
        "grounded_response.sections",
    )

    evidence_items = _require_list(
        sections.get(
            "evidence_based_explanation",
            [],
        ),
        (
            "grounded_response.sections."
            "evidence_based_explanation"
        ),
    )

    claims = []

    for index, item in enumerate(
        evidence_items,
        start=1,
    ):
        item = _require_mapping(
            item,
            "evidence-based explanation item",
        )

        claim_text = _require_non_empty_string(
            item.get(
                "evidence_text"
            ),
            "evidence claim text",
        )

        citation_id = _require_non_empty_string(
            item.get(
                "citation_id"
            ),
            "evidence claim citation_id",
        )

        if citation_id not in citation_lookup:
            raise ValueError(
                "Claim references unknown citation ID: "
                f"{citation_id}"
            )

        claims.append(
            _claim_record(
                claim_id=f"C{index}",
                claim_text=claim_text,
                section="evidence_based_explanation",
                citation_ids=[
                    citation_id
                ],
                support_status=SUPPORTED,
            )
        )

    management_summary = sections.get(
        "management_summary"
    )

    if management_summary:
        claims.append(
            _claim_record(
                claim_id=f"C{len(claims) + 1}",
                claim_text=_require_non_empty_string(
                    management_summary,
                    "management_summary",
                ),
                section="management_summary",
                citation_ids=[],
                support_status=NON_SUBSTANTIVE,
            )
        )

    operational_implication = sections.get(
        "operational_implication"
    )

    if operational_implication:
        claims.append(
            _claim_record(
                claim_id=f"C{len(claims) + 1}",
                claim_text=_require_non_empty_string(
                    operational_implication,
                    "operational_implication",
                ),
                section="operational_implication",
                citation_ids=[],
                support_status=NON_SUBSTANTIVE,
            )
        )

    return claims


def _extract_review_claims(
    grounded_response: dict,
    citation_lookup: dict[str, dict],
) -> list[dict]:
    sections = _require_mapping(
        grounded_response.get(
            "sections"
        ),
        "grounded_response.sections",
    )

    evidence_items = _require_list(
        sections.get(
            "evidence_summary",
            [],
        ),
        (
            "grounded_response.sections."
            "evidence_summary"
        ),
    )

    claims = []

    for index, item in enumerate(
        evidence_items,
        start=1,
    ):
        item = _require_mapping(
            item,
            "review evidence-summary item",
        )

        claim_text = _require_non_empty_string(
            item.get(
                "evidence_text"
            ),
            "review claim text",
        )

        citation_id = _require_non_empty_string(
            item.get(
                "citation_id"
            ),
            "review claim citation_id",
        )

        if citation_id not in citation_lookup:
            raise ValueError(
                "Review claim references unknown "
                f"citation ID: {citation_id}"
            )

        claims.append(
            _claim_record(
                claim_id=f"C{index}",
                claim_text=claim_text,
                section="evidence_summary",
                citation_ids=[
                    citation_id
                ],
                support_status=SUPPORTED,
            )
        )

    review_statement = sections.get(
        "why_human_review_is_required"
    )

    if review_statement:
        claims.append(
            _claim_record(
                claim_id=f"C{len(claims) + 1}",
                claim_text=_require_non_empty_string(
                    review_statement,
                    "why_human_review_is_required",
                ),
                section=(
                    "why_human_review_is_required"
                ),
                citation_ids=[],
                support_status=NON_SUBSTANTIVE,
            )
        )

    return claims


def _extract_abstention_claims(
    grounded_response: dict,
) -> list[dict]:
    sections = _require_mapping(
        grounded_response.get(
            "sections"
        ),
        "grounded_response.sections",
    )

    claims = []

    for section_name in (
        "unable_to_answer_safely",
        "reason",
        "what_is_needed_to_continue",
    ):
        value = sections.get(
            section_name
        )

        if value:
            claims.append(
                _claim_record(
                    claim_id=f"C{len(claims) + 1}",
                    claim_text=_require_non_empty_string(
                        value,
                        section_name,
                    ),
                    section=section_name,
                    citation_ids=[],
                    support_status=NON_SUBSTANTIVE,
                )
            )

    return claims


def build_claim_citation_links(
    grounded_response: dict,
    answer_context: dict,
) -> dict:
    """Build deterministic claim-to-citation links."""

    grounded_response = _require_mapping(
        grounded_response,
        "grounded_response",
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
        grounded_response,
        answer_context,
    )

    citation_lookup = _build_citation_lookup(
        answer_context
    )

    _validate_response_citations(
        grounded_response,
        citation_lookup,
    )

    if response_type == "ANSWER":
        claims = _extract_answer_claims(
            grounded_response,
            citation_lookup,
        )

    elif response_type == "REVIEW":
        claims = _extract_review_claims(
            grounded_response,
            citation_lookup,
        )

    elif response_type == "ABSTENTION":
        claims = _extract_abstention_claims(
            grounded_response,
        )

    else:
        raise ValueError(
            "Unsupported response type: "
            f"{response_type}"
        )

    supported_count = sum(
        1
        for claim in claims
        if (
            claim["support_status"]
            == SUPPORTED
        )
    )

    non_substantive_count = sum(
        1
        for claim in claims
        if (
            claim["support_status"]
            == NON_SUBSTANTIVE
        )
    )

    unsupported_claims = [
        claim
        for claim in claims
        if (
            claim["support_status"]
            == UNSUPPORTED
        )
    ]

    return {
        "linkage_version": "1.0",
        "packet_id": packet_id,
        "governance_decision": (
            governance_decision
        ),
        "response_type": (
            response_type
        ),
        "claims": claims,
        "linkage_summary": {
            "claim_count": len(
                claims
            ),
            "supported_count": (
                supported_count
            ),
            "non_substantive_count": (
                non_substantive_count
            ),
            "unsupported_count": len(
                unsupported_claims
            ),
        },
        "unsupported_claims": (
            unsupported_claims
        ),
        "safety_summary": {
            "citation_ids_validated": True,
            "packet_identity_preserved": True,
            "governance_preserved": True,
            "response_type_preserved": True,
        },
    }