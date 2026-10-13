"""Week 23 Day 5 — deterministic review and abstention UX."""

from __future__ import annotations

from typing import Any


REVIEW_REQUIRED = "REVIEW_REQUIRED"
ABSTAIN = "ABSTAIN"

REVIEW = "REVIEW"
ABSTENTION = "ABSTENTION"


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


def _require_bool(
    value: Any,
    field_name: str,
) -> bool:
    if not isinstance(
        value,
        bool,
    ):
        raise TypeError(
            f"{field_name} must be a boolean"
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
    claim_linkage: dict,
) -> tuple[str, str, str]:
    packet_ids = {
        _require_non_empty_string(
            grounded_response.get(
                "packet_id"
            ),
            "grounded_response.packet_id",
        ),
        _require_non_empty_string(
            answer_context.get(
                "packet_id"
            ),
            "answer_context.packet_id",
        ),
        _require_non_empty_string(
            claim_linkage.get(
                "packet_id"
            ),
            "claim_linkage.packet_id",
        ),
    }

    if len(packet_ids) != 1:
        raise ValueError(
            "Packet IDs do not match across "
            "Grounded Response, Answer Context "
            "and Claim Linkage"
        )

    governance_values = {
        _require_non_empty_string(
            grounded_response.get(
                "governance_decision"
            ),
            "grounded_response.governance_decision",
        ),
        _require_non_empty_string(
            answer_context.get(
                "governance_decision"
            ),
            "answer_context.governance_decision",
        ),
        _require_non_empty_string(
            claim_linkage.get(
                "governance_decision"
            ),
            "claim_linkage.governance_decision",
        ),
    }

    if len(governance_values) != 1:
        raise ValueError(
            "Governance decisions do not match "
            "across upstream components"
        )

    response_types = {
        _require_non_empty_string(
            grounded_response.get(
                "response_type"
            ),
            "grounded_response.response_type",
        ),
        _require_non_empty_string(
            answer_context.get(
                "response_type"
            ),
            "answer_context.response_type",
        ),
        _require_non_empty_string(
            claim_linkage.get(
                "response_type"
            ),
            "claim_linkage.response_type",
        ),
    }

    if len(response_types) != 1:
        raise ValueError(
            "Response types do not match "
            "across upstream components"
        )

    return (
        next(iter(packet_ids)),
        next(iter(governance_values)),
        next(iter(response_types)),
    )


def _build_source_summary(
    answer_context: dict,
) -> list[dict]:
    citation_index = _require_list(
        answer_context.get(
            "citation_index",
            [],
        ),
        "answer_context.citation_index",
    )

    sources = []

    for citation in citation_index:
        citation = _require_mapping(
            citation,
            "citation item",
        )

        sources.append(
            {
                "citation_id": (
                    _require_non_empty_string(
                        citation.get(
                            "citation_id"
                        ),
                        "citation.citation_id",
                    )
                ),
                "document_id": (
                    citation.get(
                        "document_id"
                    )
                ),
                "page": (
                    citation.get(
                        "page"
                    )
                ),
                "source_file": (
                    citation.get(
                        "source_file"
                    )
                ),
                "version": (
                    citation.get(
                        "version"
                    )
                ),
                "status": (
                    citation.get(
                        "status"
                    )
                ),
            }
        )

    return sources


def _build_review_ux(
    grounded_response: dict,
    answer_context: dict,
    claim_linkage: dict,
) -> dict:
    requires_human_review = _require_bool(
        grounded_response.get(
            "requires_human_review"
        ),
        "grounded_response.requires_human_review",
    )

    if requires_human_review is not True:
        raise ValueError(
            "REVIEW_REQUIRED must require human review"
        )

    sections = _require_mapping(
        grounded_response.get(
            "sections"
        ),
        "grounded_response.sections",
    )

    claims = _require_list(
        claim_linkage.get(
            "claims"
        ),
        "claim_linkage.claims",
    )

    supported_claims = [
        claim
        for claim in claims
        if (
            isinstance(
                claim,
                dict,
            )
            and claim.get(
                "support_status"
            )
            == "SUPPORTED"
        )
    ]

    uncertainty = _require_mapping(
        answer_context.get(
            "uncertainty_context",
            {},
        ),
        "answer_context.uncertainty_context",
    )

    return {
        "status": "HUMAN_REVIEW_REQUIRED",
        "headline": (
            "Relevant approved evidence was found, "
            "but human review is required before a "
            "final operational decision is made."
        ),
        "evidence_summary": (
            supported_claims
        ),
        "why_review_is_required": (
            sections.get(
                "why_human_review_is_required"
            )
            or (
                "The upstream governance decision "
                "requires human review."
            )
        ),
        "review_focus": (
            sections.get(
                "review_focus",
                {},
            )
        ),
        "uncertainty": (
            uncertainty
        ),
        "sources": (
            _build_source_summary(
                answer_context
            )
        ),
        "next_action": (
            "A responsible operational manager should "
            "review the cited evidence before making "
            "the final decision."
        ),
    }


def _build_abstention_ux(
    grounded_response: dict,
    answer_context: dict,
    claim_linkage: dict,
) -> dict:
    requires_human_review = _require_bool(
        grounded_response.get(
            "requires_human_review"
        ),
        "grounded_response.requires_human_review",
    )

    if requires_human_review is True:
        raise ValueError(
            "ABSTAIN cannot require human review "
            "in this response state"
        )

    evidence_context = _require_list(
        answer_context.get(
            "evidence_context",
            [],
        ),
        "answer_context.evidence_context",
    )

    if evidence_context:
        raise ValueError(
            "ABSTAIN UX must not expose substantive "
            "answer evidence"
        )

    claims = _require_list(
        claim_linkage.get(
            "claims"
        ),
        "claim_linkage.claims",
    )

    supported_claims = [
        claim
        for claim in claims
        if (
            isinstance(
                claim,
                dict,
            )
            and claim.get(
                "support_status"
            )
            == "SUPPORTED"
        )
    ]

    if supported_claims:
        raise ValueError(
            "ABSTAIN UX must not contain supported "
            "substantive claims"
        )

    sections = _require_mapping(
        grounded_response.get(
            "sections"
        ),
        "grounded_response.sections",
    )

    uncertainty = _require_mapping(
        answer_context.get(
            "uncertainty_context",
            {},
        ),
        "answer_context.uncertainty_context",
    )

    return {
        "status": "UNABLE_TO_ANSWER_SAFELY",
        "headline": (
            "The approved evidence base does not "
            "contain enough information to answer "
            "this question safely."
        ),
        "why_no_answer": (
            sections.get(
                "reason"
            )
            or (
                "The upstream governance decision "
                "is ABSTAIN."
            )
        ),
        "missing_information": (
            uncertainty
        ),
        "what_would_allow_progress": (
            sections.get(
                "what_is_needed_to_continue"
            )
            or (
                "Additional approved evidence or "
                "scope clarification is required."
            )
        ),
        "safe_next_action": (
            "Obtain the missing approved evidence, "
            "clarify the scope, or route the question "
            "to the appropriate operational owner."
        ),
    }


def build_review_abstention_ux(
    grounded_response: dict,
    answer_context: dict,
    claim_linkage: dict,
) -> dict:
    """Build manager-facing UX for REVIEW_REQUIRED or ABSTAIN."""

    grounded_response = _require_mapping(
        grounded_response,
        "grounded_response",
    )

    answer_context = _require_mapping(
        answer_context,
        "answer_context",
    )

    claim_linkage = _require_mapping(
        claim_linkage,
        "claim_linkage",
    )

    (
        packet_id,
        governance_decision,
        response_type,
    ) = _validate_shared_state(
        grounded_response,
        answer_context,
        claim_linkage,
    )

    if (
        governance_decision
        == REVIEW_REQUIRED
    ):
        if response_type != REVIEW:
            raise ValueError(
                "REVIEW_REQUIRED must use REVIEW "
                "response type"
            )

        manager_view = _build_review_ux(
            grounded_response,
            answer_context,
            claim_linkage,
        )

    elif governance_decision == ABSTAIN:
        if response_type != ABSTENTION:
            raise ValueError(
                "ABSTAIN must use ABSTENTION "
                "response type"
            )

        manager_view = _build_abstention_ux(
            grounded_response,
            answer_context,
            claim_linkage,
        )

    else:
        raise ValueError(
            "Review/Abstention UX only supports "
            "REVIEW_REQUIRED or ABSTAIN"
        )

    return {
        "ux_version": "1.0",
        "packet_id": packet_id,
        "governance_decision": (
            governance_decision
        ),
        "response_type": (
            response_type
        ),
        "manager_view": (
            manager_view
        ),
        "safety_summary": {
            "governance_preserved": True,
            "response_type_preserved": True,
            "packet_identity_preserved": True,
            "manager_authority_not_increased": True,
        },
    }