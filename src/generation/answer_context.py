"""Week 23 Day 2 — Evidence-to-Answer Context.

This module builds the deterministic context package that sits between:

Evidence Packet
→ Answer Contract
→ Future grounded generation

It does not retrieve evidence.

It does not decide evidence sufficiency.

It does not override provenance, lifecycle, precedence or governance.

It does not generate final answer text.
"""

from __future__ import annotations

from typing import Any


REQUIRED_EVIDENCE_FIELDS = (
    "evidence_id",
    "document_id",
    "chunk_id",
    "title",
    "document_type",
    "source_file",
    "version",
    "status",
    "page",
    "evidence_text",
    "evidence_role",
)


def _require_mapping(
    value: Any,
    field_name: str,
) -> dict:
    """Require a dictionary value."""

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
    """Require a list value."""

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


def _flatten_evidence(
    grouped_evidence: dict,
) -> list[dict]:
    """Flatten evidence groups in deterministic order."""

    grouped_evidence = _require_mapping(
        grouped_evidence,
        "evidence_packet.evidence",
    )

    ordered_roles = (
        "supporting",
        "relationship_evidence",
        "context",
    )

    flattened = []

    for role in ordered_roles:
        items = grouped_evidence.get(
            role,
            [],
        )

        items = _require_list(
            items,
            (
                "evidence_packet.evidence."
                f"{role}"
            ),
        )

        for evidence in items:
            evidence = _require_mapping(
                evidence,
                "evidence item",
            )

            flattened.append(
                evidence
            )

    return flattened


def _validate_evidence_item(
    evidence: dict,
) -> None:
    """Require all fields needed by the future generator."""

    missing = []

    for field in REQUIRED_EVIDENCE_FIELDS:
        value = evidence.get(
            field
        )

        if value is None:
            missing.append(
                field
            )

            continue

        if (
            isinstance(
                value,
                str,
            )
            and not value.strip()
        ):
            missing.append(
                field
            )

    if missing:
        raise ValueError(
            "Evidence item missing required "
            "Answer Context fields: "
            + ", ".join(
                missing
            )
        )


def _build_evidence_context(
    evidence_objects: list[dict],
) -> list[dict]:
    """Create the minimal approved evidence representation."""

    context_items = []

    for evidence in evidence_objects:
        _validate_evidence_item(
            evidence
        )

        context_items.append(
            {
                "evidence_id": (
                    evidence[
                        "evidence_id"
                    ]
                ),
                "document_id": (
                    evidence[
                        "document_id"
                    ]
                ),
                "chunk_id": (
                    evidence[
                        "chunk_id"
                    ]
                ),
                "title": (
                    evidence[
                        "title"
                    ]
                ),
                "document_type": (
                    evidence[
                        "document_type"
                    ]
                ),
                "source_file": (
                    evidence[
                        "source_file"
                    ]
                ),
                "version": (
                    evidence[
                        "version"
                    ]
                ),
                "status": (
                    evidence[
                        "status"
                    ]
                ),
                "page": (
                    evidence[
                        "page"
                    ]
                ),
                "evidence_text": (
                    evidence[
                        "evidence_text"
                    ]
                ),
                "evidence_role": (
                    evidence[
                        "evidence_role"
                    ]
                ),
            }
        )

    return context_items


def _build_citation_index(
    evidence_context: list[dict],
) -> list[dict]:
    """Create stable E1, E2, E3 citation references."""

    citation_index = []

    for index, evidence in enumerate(
        evidence_context,
        start=1,
    ):
        citation_index.append(
            {
                "citation_id": (
                    f"E{index}"
                ),
                "evidence_id": (
                    evidence[
                        "evidence_id"
                    ]
                ),
                "document_id": (
                    evidence[
                        "document_id"
                    ]
                ),
                "chunk_id": (
                    evidence[
                        "chunk_id"
                    ]
                ),
                "page": (
                    evidence[
                        "page"
                    ]
                ),
                "source_file": (
                    evidence[
                        "source_file"
                    ]
                ),
                "version": (
                    evidence[
                        "version"
                    ]
                ),
                "status": (
                    evidence[
                        "status"
                    ]
                ),
            }
        )

    return citation_index


def build_answer_context(
    evidence_packet: dict,
    answer_contract: dict,
) -> dict:
    """Build deterministic generator context from approved upstream state."""

    evidence_packet = _require_mapping(
        evidence_packet,
        "evidence_packet",
    )

    answer_contract = _require_mapping(
        answer_contract,
        "answer_contract",
    )

    packet_id = _require_non_empty_string(
        evidence_packet.get(
            "packet_id"
        ),
        "evidence_packet.packet_id",
    )

    contract_packet_id = (
        _require_non_empty_string(
            answer_contract.get(
                "packet_id"
            ),
            "answer_contract.packet_id",
        )
    )

    if packet_id != contract_packet_id:
        raise ValueError(
            "Evidence Packet and Answer Contract "
            "packet IDs do not match"
        )

    question = _require_non_empty_string(
        evidence_packet.get(
            "question"
        ),
        "evidence_packet.question",
    )

    governance = _require_mapping(
        evidence_packet.get(
            "governance"
        ),
        "evidence_packet.governance",
    )

    governance_decision = (
        _require_non_empty_string(
            governance.get(
                "decision"
            ),
            (
                "evidence_packet."
                "governance.decision"
            ),
        )
    )

    contract_decision = (
        _require_non_empty_string(
            answer_contract.get(
                "governance_decision"
            ),
            (
                "answer_contract."
                "governance_decision"
            ),
        )
    )

    if (
        governance_decision
        != contract_decision
    ):
        raise ValueError(
            "Evidence Packet and Answer Contract "
            "governance decisions do not match"
        )

    response_type = (
        _require_non_empty_string(
            answer_contract.get(
                "response_type"
            ),
            "answer_contract.response_type",
        )
    )

    allowed_sections = _require_list(
        answer_contract.get(
            "response_sections"
        ),
        "answer_contract.response_sections",
    )

    generation_permitted = (
        answer_contract.get(
            "may_generate_answer"
        )
    )

    requires_human_review = (
        answer_contract.get(
            "requires_human_review"
        )
    )

    if not isinstance(
        generation_permitted,
        bool,
    ):
        raise TypeError(
            "answer_contract.may_generate_answer "
            "must be a boolean"
        )

    if not isinstance(
        requires_human_review,
        bool,
    ):
        raise TypeError(
            "answer_contract.requires_human_review "
            "must be a boolean"
        )

    evidence_objects = _flatten_evidence(
        evidence_packet.get(
            "evidence",
            {},
        )
    )

    if (
        governance_decision
        == "ABSTAIN"
    ):
        evidence_context = []

    else:
        evidence_context = (
            _build_evidence_context(
                evidence_objects
            )
        )

        if not evidence_context:
            raise ValueError(
                "Non-ABSTAIN Answer Context "
                "requires approved evidence"
            )

    citation_index = (
        _build_citation_index(
            evidence_context
        )
    )

    missing_evidence = _require_mapping(
        evidence_packet.get(
            "missing_evidence",
            {},
        ),
        "evidence_packet.missing_evidence",
    )

    initial_missing_topics = _require_list(
        missing_evidence.get(
            "initial_missing_topics",
            [],
        ),
        (
            "evidence_packet.missing_evidence."
            "initial_missing_topics"
        ),
    )

    final_missing_topics = _require_list(
        missing_evidence.get(
            "final_missing_topics",
            [],
        ),
        (
            "evidence_packet.missing_evidence."
            "final_missing_topics"
        ),
    )

    unsupported_claims = _require_list(
        missing_evidence.get(
            "unsupported_claims",
            [],
        ),
        (
            "evidence_packet.missing_evidence."
            "unsupported_claims"
        ),
    )

    precedence = _require_mapping(
        evidence_packet.get(
            "precedence_assessment"
        ),
        (
            "evidence_packet."
            "precedence_assessment"
        ),
    )

    precedence_decision = (
        _require_non_empty_string(
            precedence.get(
                "decision"
            ),
            (
                "evidence_packet."
                "precedence_assessment."
                "decision"
            ),
        )
    )

    return {
        "context_version": "1.0",
        "packet_id": packet_id,
        "question": question,
        "governance_decision": (
            governance_decision
        ),
        "response_type": (
            response_type
        ),
        "allowed_sections": list(
            allowed_sections
        ),
        "generation_permitted": (
            generation_permitted
        ),
        "requires_human_review": (
            requires_human_review
        ),
        "precedence_decision": (
            precedence_decision
        ),
        "evidence_context": (
            evidence_context
        ),
        "citation_index": (
            citation_index
        ),
        "uncertainty_context": {
            "initial_missing_topics": list(
                initial_missing_topics
            ),
            "final_missing_topics": list(
                final_missing_topics
            ),
            "unsupported_claims": list(
                unsupported_claims
            ),
        },
        "safety_constraints": [
            "Use approved evidence only.",
            "Do not invent source identifiers.",
            "Do not override governance.",
            "Do not override lifecycle or precedence controls.",
            "Do not convert uncertainty into established fact.",
        ],
    }