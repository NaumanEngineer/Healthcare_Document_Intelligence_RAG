"""Week 23 Day 3 — deterministic grounded response generation."""

from __future__ import annotations

from typing import Any


AUTO_ANSWER = "AUTO_ANSWER"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
ABSTAIN = "ABSTAIN"

ANSWER = "ANSWER"
REVIEW = "REVIEW"
ABSTENTION = "ABSTENTION"

GENERATED = "GENERATED"
REVIEW_SUMMARY = "REVIEW_SUMMARY"
ABSTAINED = "ABSTAINED"


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
    answer_contract: dict,
    answer_context: dict,
) -> tuple[str, str, str]:
    contract_packet_id = _require_non_empty_string(
        answer_contract.get(
            "packet_id"
        ),
        "answer_contract.packet_id",
    )

    context_packet_id = _require_non_empty_string(
        answer_context.get(
            "packet_id"
        ),
        "answer_context.packet_id",
    )

    if (
        contract_packet_id
        != context_packet_id
    ):
        raise ValueError(
            "Answer Contract and Answer Context "
            "packet IDs do not match"
        )

    contract_governance = _require_non_empty_string(
        answer_contract.get(
            "governance_decision"
        ),
        "answer_contract.governance_decision",
    )

    context_governance = _require_non_empty_string(
        answer_context.get(
            "governance_decision"
        ),
        "answer_context.governance_decision",
    )

    if (
        contract_governance
        != context_governance
    ):
        raise ValueError(
            "Answer Contract and Answer Context "
            "governance decisions do not match"
        )

    contract_response_type = _require_non_empty_string(
        answer_contract.get(
            "response_type"
        ),
        "answer_contract.response_type",
    )

    context_response_type = _require_non_empty_string(
        answer_context.get(
            "response_type"
        ),
        "answer_context.response_type",
    )

    if (
        contract_response_type
        != context_response_type
    ):
        raise ValueError(
            "Answer Contract and Answer Context "
            "response types do not match"
        )

    return (
        contract_packet_id,
        contract_governance,
        contract_response_type,
    )


def _build_sources(
    citation_index: list[dict],
) -> list[dict]:
    sources = []

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

        document_id = _require_non_empty_string(
            citation.get(
                "document_id"
            ),
            "citation.document_id",
        )

        chunk_id = _require_non_empty_string(
            citation.get(
                "chunk_id"
            ),
            "citation.chunk_id",
        )

        sources.append(
            {
                "citation_id": citation_id,
                "document_id": document_id,
                "chunk_id": chunk_id,
                "page": citation.get(
                    "page"
                ),
                "source_file": citation.get(
                    "source_file"
                ),
                "version": citation.get(
                    "version"
                ),
                "status": citation.get(
                    "status"
                ),
            }
        )

    return sources


def _build_evidence_summary(
    evidence_context: list[dict],
) -> list[dict]:
    summary = []

    for index, evidence in enumerate(
        evidence_context,
        start=1,
    ):
        evidence = _require_mapping(
            evidence,
            "evidence_context item",
        )

        evidence_text = _require_non_empty_string(
            evidence.get(
                "evidence_text"
            ),
            "evidence.evidence_text",
        )

        summary.append(
            {
                "citation_id": f"E{index}",
                "document_id": (
                    evidence.get(
                        "document_id"
                    )
                ),
                "evidence_text": (
                    evidence_text
                ),
            }
        )

    return summary


def _build_auto_answer_sections(
    answer_context: dict,
) -> dict:
    evidence_context = _require_list(
        answer_context.get(
            "evidence_context"
        ),
        "answer_context.evidence_context",
    )

    citation_index = _require_list(
        answer_context.get(
            "citation_index"
        ),
        "answer_context.citation_index",
    )

    if not evidence_context:
        raise ValueError(
            "AUTO_ANSWER requires approved evidence"
        )

    if not citation_index:
        raise ValueError(
            "AUTO_ANSWER requires citations"
        )

    evidence_summary = _build_evidence_summary(
        evidence_context
    )

    return {
        "management_summary": (
            "Approved evidence is available to answer "
            "the management question."
        ),
        "evidence_based_explanation": (
            evidence_summary
        ),
        "operational_implication": (
            "Use the approved evidence above as the "
            "basis for the operational response."
        ),
        "caveats": (
            answer_context.get(
                "uncertainty_context",
                {},
            )
        ),
        "sources": _build_sources(
            citation_index
        ),
    }


def _build_review_sections(
    answer_context: dict,
) -> dict:
    evidence_context = _require_list(
        answer_context.get(
            "evidence_context"
        ),
        "answer_context.evidence_context",
    )

    citation_index = _require_list(
        answer_context.get(
            "citation_index"
        ),
        "answer_context.citation_index",
    )

    if not evidence_context:
        raise ValueError(
            "REVIEW_REQUIRED requires evidence "
            "for human review"
        )

    return {
        "evidence_summary": (
            _build_evidence_summary(
                evidence_context
            )
        ),
        "why_human_review_is_required": (
            "The upstream governance decision requires "
            "human review before an authoritative answer "
            "or operational recommendation is issued."
        ),
        "review_focus": {
            "precedence_decision": (
                answer_context.get(
                    "precedence_decision"
                )
            ),
            "question": (
                answer_context.get(
                    "question"
                )
            ),
        },
        "evidence_gaps_or_uncertainty": (
            answer_context.get(
                "uncertainty_context",
                {},
            )
        ),
        "sources": _build_sources(
            citation_index
        ),
    }


def _build_abstention_sections(
    answer_context: dict,
) -> dict:
    evidence_context = _require_list(
        answer_context.get(
            "evidence_context"
        ),
        "answer_context.evidence_context",
    )

    citation_index = _require_list(
        answer_context.get(
            "citation_index"
        ),
        "answer_context.citation_index",
    )

    if evidence_context:
        raise ValueError(
            "ABSTAIN must not contain substantive "
            "answer evidence"
        )

    if citation_index:
        raise ValueError(
            "ABSTAIN must not contain answer citations"
        )

    uncertainty = _require_mapping(
        answer_context.get(
            "uncertainty_context",
            {},
        ),
        "answer_context.uncertainty_context",
    )

    return {
        "unable_to_answer_safely": (
            "The system cannot provide a substantive "
            "answer from the approved evidence."
        ),
        "reason": (
            "The upstream governance decision is ABSTAIN."
        ),
        "missing_evidence": uncertainty,
        "what_is_needed_to_continue": (
            "Additional approved evidence or scope "
            "clarification is required before a "
            "substantive answer can be generated."
        ),
    }


def build_grounded_response(
    answer_contract: dict,
    answer_context: dict,
) -> dict:
    """Build deterministic grounded response from governed context."""

    answer_contract = _require_mapping(
        answer_contract,
        "answer_contract",
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
        answer_contract,
        answer_context,
    )

    contract_generation = _require_bool(
        answer_contract.get(
            "may_generate_answer"
        ),
        "answer_contract.may_generate_answer",
    )

    context_generation = _require_bool(
        answer_context.get(
            "generation_permitted"
        ),
        "answer_context.generation_permitted",
    )

    if (
        contract_generation
        != context_generation
    ):
        raise ValueError(
            "Answer Contract and Answer Context "
            "generation permissions do not match"
        )

    contract_review = _require_bool(
        answer_contract.get(
            "requires_human_review"
        ),
        "answer_contract.requires_human_review",
    )

    context_review = _require_bool(
        answer_context.get(
            "requires_human_review"
        ),
        "answer_context.requires_human_review",
    )

    if (
        contract_review
        != context_review
    ):
        raise ValueError(
            "Answer Contract and Answer Context "
            "human-review flags do not match"
        )

    allowed_sections = _require_list(
        answer_context.get(
            "allowed_sections"
        ),
        "answer_context.allowed_sections",
    )

    if governance_decision == AUTO_ANSWER:
        if response_type != ANSWER:
            raise ValueError(
                "AUTO_ANSWER must use ANSWER response type"
            )

        if contract_generation is not True:
            raise ValueError(
                "AUTO_ANSWER must permit generation"
            )

        if contract_review is True:
            raise ValueError(
                "AUTO_ANSWER cannot require human review"
            )

        generation_status = GENERATED

        sections = _build_auto_answer_sections(
            answer_context
        )

    elif governance_decision == REVIEW_REQUIRED:
        if response_type != REVIEW:
            raise ValueError(
                "REVIEW_REQUIRED must use REVIEW response type"
            )

        if contract_generation is True:
            raise ValueError(
                "REVIEW_REQUIRED cannot permit "
                "authoritative answer generation"
            )

        if contract_review is not True:
            raise ValueError(
                "REVIEW_REQUIRED must require human review"
            )

        generation_status = REVIEW_SUMMARY

        sections = _build_review_sections(
            answer_context
        )

    elif governance_decision == ABSTAIN:
        if response_type != ABSTENTION:
            raise ValueError(
                "ABSTAIN must use ABSTENTION response type"
            )

        if contract_generation is True:
            raise ValueError(
                "ABSTAIN cannot permit answer generation"
            )

        if contract_review is True:
            raise ValueError(
                "ABSTAIN cannot require human review "
                "in this response contract"
            )

        generation_status = ABSTAINED

        sections = _build_abstention_sections(
            answer_context
        )

    else:
        raise ValueError(
            "Unsupported governance decision: "
            f"{governance_decision}"
        )

    unexpected_sections = (
        set(
            sections.keys()
        )
        - set(
            allowed_sections
        )
    )

    if unexpected_sections:
        raise ValueError(
            "Generated sections are not permitted "
            "by the Answer Context: "
            + ", ".join(
                sorted(
                    unexpected_sections
                )
            )
        )

    citations_used = []

    sources = sections.get(
        "sources",
        [],
    )

    if isinstance(
        sources,
        list,
    ):
        citations_used = [
            item["citation_id"]
            for item in sources
            if (
                isinstance(
                    item,
                    dict,
                )
                and "citation_id" in item
            )
        ]

    return {
        "response_version": "1.0",
        "packet_id": packet_id,
        "governance_decision": (
            governance_decision
        ),
        "response_type": (
            response_type
        ),
        "generation_status": (
            generation_status
        ),
        "requires_human_review": (
            contract_review
        ),
        "sections": sections,
        "citations_used": (
            citations_used
        ),
        "safety_summary": {
            "generation_permission_preserved": True,
            "governance_preserved": True,
            "human_review_requirement_preserved": True,
            "approved_context_only": True,
        },
    }