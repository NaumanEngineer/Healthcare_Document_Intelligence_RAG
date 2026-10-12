"""Week 23 Day 1 — Answer Contract.

This module converts an existing governance decision into a deterministic
response contract.

It does not generate answer text.

It does not decide evidence sufficiency.

It does not override governance.

Governance remains authoritative.
"""

from __future__ import annotations

from typing import Any


AUTO_ANSWER = "AUTO_ANSWER"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
ABSTAIN = "ABSTAIN"

RESPONSE_TYPE_ANSWER = "ANSWER"
RESPONSE_TYPE_REVIEW = "REVIEW"
RESPONSE_TYPE_ABSTENTION = "ABSTENTION"

SUPPORTED_GOVERNANCE_DECISIONS = {
    AUTO_ANSWER,
    REVIEW_REQUIRED,
    ABSTAIN,
}


AUTO_ANSWER_SECTIONS = [
    "management_summary",
    "evidence_based_explanation",
    "operational_implication",
    "caveats",
    "sources",
]

REVIEW_REQUIRED_SECTIONS = [
    "evidence_summary",
    "why_human_review_is_required",
    "review_focus",
    "evidence_gaps_or_uncertainty",
    "sources",
]

ABSTAIN_SECTIONS = [
    "unable_to_answer_safely",
    "reason",
    "missing_evidence",
    "what_is_needed_to_continue",
]


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


def _validate_governance_consistency(
    governance: dict,
    decision: str,
) -> None:
    """Fail closed if governance permission fields contradict decision."""

    may_generate = governance.get(
        "may_generate_answer"
    )

    requires_review = governance.get(
        "requires_human_review"
    )

    if (
        decision == ABSTAIN
        and may_generate is True
    ):
        raise ValueError(
            "Governance contradiction: "
            "ABSTAIN cannot permit answer generation"
        )

    if (
        decision == REVIEW_REQUIRED
        and may_generate is True
    ):
        raise ValueError(
            "Governance contradiction: "
            "REVIEW_REQUIRED cannot permit answer generation"
        )

    if (
        decision == AUTO_ANSWER
        and may_generate is False
    ):
        raise ValueError(
            "Governance contradiction: "
            "AUTO_ANSWER cannot explicitly prohibit generation"
        )

    if (
        decision == REVIEW_REQUIRED
        and requires_review is False
    ):
        raise ValueError(
            "Governance contradiction: "
            "REVIEW_REQUIRED cannot explicitly disable human review"
        )

    if (
        decision == ABSTAIN
        and requires_review is True
    ):
        raise ValueError(
            "Governance contradiction: "
            "ABSTAIN cannot require human review in the answer contract"
        )


def build_answer_contract(
    evidence_packet: dict,
) -> dict:
    """Build a deterministic response contract from an Evidence Packet."""

    evidence_packet = _require_mapping(
        evidence_packet,
        "evidence_packet",
    )

    packet_id = _require_non_empty_string(
        evidence_packet.get(
            "packet_id"
        ),
        "evidence_packet.packet_id",
    )

    governance = _require_mapping(
        evidence_packet.get(
            "governance"
        ),
        "evidence_packet.governance",
    )

    decision = _require_non_empty_string(
        governance.get(
            "decision"
        ),
        "evidence_packet.governance.decision",
    )

    if decision not in SUPPORTED_GOVERNANCE_DECISIONS:
        raise ValueError(
            "Unsupported governance decision: "
            f"{decision}"
        )

    _validate_governance_consistency(
        governance,
        decision,
    )

    if decision == AUTO_ANSWER:
        return {
            "answer_contract_version": "1.0",
            "packet_id": packet_id,
            "governance_decision": decision,
            "response_type": RESPONSE_TYPE_ANSWER,
            "response_sections": list(
                AUTO_ANSWER_SECTIONS
            ),
            "requires_human_review": False,
            "may_generate_answer": True,
            "may_issue_authoritative_recommendation": True,
            "must_preserve_citations": True,
            "must_use_approved_evidence_only": True,
            "safety_notes": [
                "Do not introduce unsupported material claims.",
                "Do not override provenance, lifecycle, precedence or governance.",
            ],
        }

    if decision == REVIEW_REQUIRED:
        return {
            "answer_contract_version": "1.0",
            "packet_id": packet_id,
            "governance_decision": decision,
            "response_type": RESPONSE_TYPE_REVIEW,
            "response_sections": list(
                REVIEW_REQUIRED_SECTIONS
            ),
            "requires_human_review": True,
            "may_generate_answer": False,
            "may_issue_authoritative_recommendation": False,
            "must_preserve_citations": True,
            "must_use_approved_evidence_only": True,
            "safety_notes": [
                "Summarise evidence without making the final operational decision.",
                "Human review must remain explicit.",
            ],
        }

    return {
        "answer_contract_version": "1.0",
        "packet_id": packet_id,
        "governance_decision": decision,
        "response_type": RESPONSE_TYPE_ABSTENTION,
        "response_sections": list(
            ABSTAIN_SECTIONS
        ),
        "requires_human_review": False,
        "may_generate_answer": False,
        "may_issue_authoritative_recommendation": False,
        "must_preserve_citations": False,
        "must_use_approved_evidence_only": True,
        "safety_notes": [
            "Do not provide a hidden substantive answer.",
            "Explain why the system cannot answer safely.",
        ],
    }