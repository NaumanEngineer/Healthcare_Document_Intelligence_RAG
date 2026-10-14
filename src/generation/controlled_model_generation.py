"""Week 24 Day 1 — controlled model-generation adapter."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


AUTO_ANSWER = "AUTO_ANSWER"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
ABSTAIN = "ABSTAIN"

ANSWER = "ANSWER"
REVIEW = "REVIEW"
ABSTENTION = "ABSTENTION"

MODEL_GENERATED = "MODEL_GENERATED"
MODEL_REVIEW_SUMMARY = "MODEL_REVIEW_SUMMARY"
MODEL_ABSTAINED = "MODEL_ABSTAINED"
MODEL_REJECTED = "MODEL_REJECTED"

ALLOWED_RESPONSE_TYPES = {
    AUTO_ANSWER: ANSWER,
    REVIEW_REQUIRED: REVIEW,
    ABSTAIN: ABSTENTION,
}

ALLOWED_SECTIONS = {
    ANSWER: {
        "management_summary",
        "evidence_based_explanation",
        "operational_implication",
        "caveats",
    },
    REVIEW: {
        "evidence_summary",
        "why_human_review_is_required",
        "review_focus",
        "evidence_gaps_or_uncertainty",
    },
    ABSTENTION: {
        "unable_to_answer_safely",
        "reason",
        "missing_information",
        "what_is_needed_to_continue",
    },
}


ABSTENTION_PROHIBITED_PHRASES = {
    "you should",
    "you must",
    "we should",
    "we must",
    "immediately implement",
    "implement a",
    "implement the",
    "proceed using",
    "proceed with",
    "take action",
    "take the following action",
    "recommended action",
    "recommend that",
    "my recommendation",
    "operational recommendation",
    "should immediately",
    "must immediately",
}


def _require_mapping(
    value: Any,
    name: str,
) -> dict:
    if not isinstance(
        value,
        dict,
    ):
        raise ValueError(
            f"{name} must be a mapping."
        )

    return value


def _require_list(
    value: Any,
    name: str,
) -> list:
    if not isinstance(
        value,
        list,
    ):
        raise ValueError(
            f"{name} must be a list."
        )

    return value


def _require_bool(
    value: Any,
    name: str,
) -> bool:
    if not isinstance(
        value,
        bool,
    ):
        raise ValueError(
            f"{name} must be a boolean."
        )

    return value


def _require_non_empty_string(
    value: Any,
    name: str,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or not value.strip()
    ):
        raise ValueError(
            f"{name} must be a non-empty string."
        )

    return value.strip()


def _validate_abstention_sections(
    sections: dict,
) -> None:
    """Ensure abstention text does not smuggle in substantive advice."""

    required_sections = {
        "unable_to_answer_safely",
        "reason",
        "missing_information",
        "what_is_needed_to_continue",
    }

    missing_sections = (
        required_sections
        - set(
            sections.keys()
        )
    )

    if missing_sections:
        raise ValueError(
            "ABSTAIN output is missing required sections: "
            + ", ".join(
                sorted(
                    missing_sections
                )
            )
        )

    for section_name in required_sections:
        section_text = _require_non_empty_string(
            sections.get(
                section_name
            ),
            f"ABSTAIN section {section_name}",
        )

        normalized_text = (
            " ".join(
                section_text.lower().split()
            )
        )

        for phrase in ABSTENTION_PROHIBITED_PHRASES:
            if phrase in normalized_text:
                raise ValueError(
                    "ABSTAIN output contains prohibited "
                    "substantive or directive content: "
                    f"{phrase}"
                )


def build_model_generation_input(
    answer_context: dict,
) -> dict:
    """Build the only payload the model is allowed to receive."""

    context = _require_mapping(
        answer_context,
        "answer_context",
    )

    packet_id = _require_non_empty_string(
        context.get(
            "packet_id"
        ),
        "packet_id",
    )

    question = _require_non_empty_string(
        context.get(
            "question"
        ),
        "question",
    )

    governance_decision = _require_non_empty_string(
        context.get(
            "governance_decision"
        ),
        "governance_decision",
    )

    response_type = _require_non_empty_string(
        context.get(
            "response_type"
        ),
        "response_type",
    )

    generation_permitted = _require_bool(
        context.get(
            "generation_permitted"
        ),
        "generation_permitted",
    )

    requires_human_review = _require_bool(
        context.get(
            "requires_human_review"
        ),
        "requires_human_review",
    )

    expected_response_type = (
        ALLOWED_RESPONSE_TYPES.get(
            governance_decision
        )
    )

    if expected_response_type is None:
        raise ValueError(
            "Unsupported governance decision."
        )

    if response_type != expected_response_type:
        raise ValueError(
            "Governance and response type mismatch."
        )

    if governance_decision == AUTO_ANSWER:
        if generation_permitted is not True:
            raise ValueError(
                "AUTO_ANSWER requires generation_permitted=true."
            )

        if requires_human_review is not False:
            raise ValueError(
                "AUTO_ANSWER must not require human review."
            )

    elif governance_decision == REVIEW_REQUIRED:
        if generation_permitted is not False:
            raise ValueError(
                "REVIEW_REQUIRED must not permit authoritative generation."
            )

        if requires_human_review is not True:
            raise ValueError(
                "REVIEW_REQUIRED must require human review."
            )

    elif governance_decision == ABSTAIN:
        if generation_permitted is not False:
            raise ValueError(
                "ABSTAIN must not permit substantive generation."
            )

        if requires_human_review is not False:
            raise ValueError(
                "ABSTAIN should not convert into a review state."
            )

    allowed_sections = _require_list(
        context.get(
            "allowed_sections"
        ),
        "allowed_sections",
    )

    safety_constraints = _require_list(
        context.get(
            "safety_constraints"
        ),
        "safety_constraints",
    )

    evidence_context = _require_list(
        context.get(
            "evidence_context"
        ),
        "evidence_context",
    )

    citation_index = _require_list(
        context.get(
            "citation_index"
        ),
        "citation_index",
    )

    uncertainty_context = _require_mapping(
        context.get(
            "uncertainty_context"
        ),
        "uncertainty_context",
    )

    if governance_decision == ABSTAIN:
        if evidence_context:
            raise ValueError(
                "ABSTAIN model input must not contain substantive evidence."
            )

        if citation_index:
            raise ValueError(
                "ABSTAIN model input must not contain citations."
            )

    return {
        "packet_id": packet_id,
        "question": question,
        "governance_decision": (
            governance_decision
        ),
        "response_type": (
            response_type
        ),
        "generation_permitted": (
            generation_permitted
        ),
        "requires_human_review": (
            requires_human_review
        ),
        "allowed_sections": deepcopy(
            allowed_sections
        ),
        "safety_constraints": deepcopy(
            safety_constraints
        ),
        "evidence_context": deepcopy(
            evidence_context
        ),
        "citation_index": deepcopy(
            citation_index
        ),
        "uncertainty_context": deepcopy(
            uncertainty_context
        ),
    }


def _valid_citation_ids(
    model_input: dict,
) -> set[str]:
    citation_ids = set()

    for item in model_input[
        "citation_index"
    ]:
        citation = _require_mapping(
            item,
            "citation_index item",
        )

        citation_id = _require_non_empty_string(
            citation.get(
                "citation_id"
            ),
            "citation_id",
        )

        if citation_id in citation_ids:
            raise ValueError(
                "Duplicate citation ID in model input."
            )

        citation_ids.add(
            citation_id
        )

    return citation_ids


def validate_model_generation_output(
    model_input: dict,
    model_output: dict,
) -> dict:
    """Validate model output before it may enter the governed workflow."""

    model_input = _require_mapping(
        model_input,
        "model_input",
    )

    output = _require_mapping(
        model_output,
        "model_output",
    )

    packet_id = _require_non_empty_string(
        output.get(
            "packet_id"
        ),
        "packet_id",
    )

    governance_decision = _require_non_empty_string(
        output.get(
            "governance_decision"
        ),
        "governance_decision",
    )

    response_type = _require_non_empty_string(
        output.get(
            "response_type"
        ),
        "response_type",
    )

    requires_human_review = _require_bool(
        output.get(
            "requires_human_review"
        ),
        "requires_human_review",
    )

    if packet_id != model_input[
        "packet_id"
    ]:
        raise ValueError(
            "Model output packet identity mismatch."
        )

    if governance_decision != model_input[
        "governance_decision"
    ]:
        raise ValueError(
            "Model output governance mismatch."
        )

    if response_type != model_input[
        "response_type"
    ]:
        raise ValueError(
            "Model output response type mismatch."
        )

    if requires_human_review != model_input[
        "requires_human_review"
    ]:
        raise ValueError(
            "Model output human-review state mismatch."
        )

    sections = _require_mapping(
        output.get(
            "sections"
        ),
        "sections",
    )

    allowed_section_names = (
        ALLOWED_SECTIONS[
            response_type
        ]
    )

    unexpected_sections = (
        set(
            sections.keys()
        )
        - allowed_section_names
    )

    if unexpected_sections:
        raise ValueError(
            "Model output contains prohibited sections: "
            + ", ".join(
                sorted(
                    unexpected_sections
                )
            )
        )

    citations_used = _require_list(
        output.get(
            "citations_used"
        ),
        "citations_used",
    )

    valid_citation_ids = _valid_citation_ids(
        model_input
    )

    seen_citations = set()

    for citation_id in citations_used:
        citation_id = _require_non_empty_string(
            citation_id,
            "citation used",
        )

        if citation_id not in valid_citation_ids:
            raise ValueError(
                f"Unknown citation ID: {citation_id}"
            )

        if citation_id in seen_citations:
            raise ValueError(
                f"Duplicate citation ID: {citation_id}"
            )

        seen_citations.add(
            citation_id
        )

    if governance_decision == ABSTAIN:
        if citations_used:
            raise ValueError(
                "ABSTAIN output must not contain citations."
            )

        prohibited_abstain_sections = {
            "management_summary",
            "evidence_based_explanation",
            "operational_implication",
            "operational_recommendation",
        }

        if (
            set(
                sections.keys()
            )
            & prohibited_abstain_sections
        ):
            raise ValueError(
                "ABSTAIN output contains substantive answer content."
            )

        _validate_abstention_sections(
            sections
        )

    if governance_decision == REVIEW_REQUIRED:
        prohibited_review_sections = {
            "final_decision",
            "approved_action",
            "operational_recommendation",
        }

        if (
            set(
                sections.keys()
            )
            & prohibited_review_sections
        ):
            raise ValueError(
                "REVIEW_REQUIRED output became authoritative."
            )

    model_safety_notes = _require_list(
        output.get(
            "model_safety_notes"
        ),
        "model_safety_notes",
    )

    model_generation_status = (
        _require_non_empty_string(
            output.get(
                "model_generation_status"
            ),
            "model_generation_status",
        )
    )

    expected_status = {
        AUTO_ANSWER: MODEL_GENERATED,
        REVIEW_REQUIRED: MODEL_REVIEW_SUMMARY,
        ABSTAIN: MODEL_ABSTAINED,
    }[
        governance_decision
    ]

    if model_generation_status != expected_status:
        raise ValueError(
            "Model generation status does not match governance."
        )

    return {
        "packet_id": packet_id,
        "governance_decision": (
            governance_decision
        ),
        "response_type": (
            response_type
        ),
        "requires_human_review": (
            requires_human_review
        ),
        "model_generation_status": (
            model_generation_status
        ),
        "sections": deepcopy(
            sections
        ),
        "citations_used": list(
            seen_citations
        ),
        "model_safety_notes": deepcopy(
            model_safety_notes
        ),
        "validation_status": "VALIDATED",
    }