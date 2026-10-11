"""Manager-ready Evidence Brief.

Week 22 Day 5.

This module converts a structured Evidence Packet into a concise,
manager-readable evidence brief.

It does not generate new facts.

It does not override:

- retrieval;
- evidence sufficiency;
- provenance;
- precedence assessment;
- governance.

The Evidence Packet remains the source of truth.
"""

from __future__ import annotations

from typing import Any


BRIEF_READY = "BRIEF_READY"
BRIEF_REVIEW_REQUIRED = "BRIEF_REVIEW_REQUIRED"
BRIEF_UNAVAILABLE = "BRIEF_UNAVAILABLE"


def _require_mapping(
    value: Any,
    field_name: str,
) -> dict:
    """Require dictionary input."""

    if not isinstance(
        value,
        dict,
    ):
        raise TypeError(
            f"{field_name} must be a dictionary"
        )

    return value


def _require_string(
    value: Any,
    field_name: str,
) -> str:
    """Require non-empty string."""

    if (
        not isinstance(
            value,
            str,
        )
        or not value.strip()
    ):
        raise ValueError(
            f"{field_name} must be a non-empty string"
        )

    return value.strip()


def _build_document_summary(
    packet: dict,
) -> dict:
    """Summarize the documents represented in the packet."""

    document_ids = packet.get(
        "document_ids",
        [],
    )

    if not isinstance(
        document_ids,
        list,
    ):
        raise TypeError(
            "document_ids must be a list"
        )

    return {
        "document_count": len(
            document_ids
        ),
        "document_ids": (
            document_ids
        ),
    }


def _build_assurance_summary(
    packet: dict,
) -> dict:
    """Build concise evidence assurance summary."""

    provenance_summary = (
        _require_mapping(
            packet.get(
                "provenance_summary",
                {},
            ),
            "provenance_summary",
        )
    )

    lifecycle_summary = (
        _require_mapping(
            packet.get(
                "lifecycle_summary",
                {},
            ),
            "lifecycle_summary",
        )
    )

    precedence_assessment = (
        _require_mapping(
            packet.get(
                "precedence_assessment",
                {},
            ),
            "precedence_assessment",
        )
    )

    return {
        "provenance_verified": (
            provenance_summary.get(
                "all_verified"
            )
            is True
        ),
        "all_evidence_active": (
            lifecycle_summary.get(
                "all_active"
            )
            is True
        ),
        "precedence_decision": (
            precedence_assessment.get(
                "decision"
            )
        ),
        "precedence_reason": (
            precedence_assessment.get(
                "reason"
            )
        ),
    }


def _build_evidence_summary(
    packet: dict,
) -> dict:
    """Summarize evidence sufficiency and unresolved gaps."""

    evidence_sufficiency = (
        _require_mapping(
            packet.get(
                "evidence_sufficiency",
                {},
            ),
            "evidence_sufficiency",
        )
    )

    missing_evidence = (
        _require_mapping(
            packet.get(
                "missing_evidence",
                {},
            ),
            "missing_evidence",
        )
    )

    return {
        "evidence_count": (
            packet.get(
                "evidence_count",
                0,
            )
        ),
        "sufficient": (
            evidence_sufficiency.get(
                "sufficient"
            )
            is True
        ),
        "sufficiency_reason": (
            evidence_sufficiency.get(
                "reason"
            )
        ),
        "final_missing_topics": (
            missing_evidence.get(
                "final_missing_topics",
                [],
            )
        ),
        "unsupported_claims": (
            missing_evidence.get(
                "unsupported_claims",
                [],
            )
        ),
    }


def _build_governance_summary(
    packet: dict,
) -> dict:
    """Summarize authoritative governance outcome."""

    governance = _require_mapping(
        packet.get(
            "governance",
            {},
        ),
        "governance",
    )

    return {
        "decision": (
            governance.get(
                "decision"
            )
        ),
        "requires_human_review": (
            governance.get(
                "requires_human_review"
            )
            is True
        ),
        "may_generate_answer": (
            governance.get(
                "may_generate_answer"
            )
            is True
        ),
        "reason": (
            governance.get(
                "reason"
            )
        ),
    }


def _determine_brief_status(
    evidence_summary: dict,
    assurance_summary: dict,
    governance_summary: dict,
) -> str:
    """Determine manager brief availability.

    BRIEF_UNAVAILABLE:
        Evidence is absent or insufficient.

    BRIEF_REVIEW_REQUIRED:
        Evidence exists but human review or evidence-combination review
        is required.

    BRIEF_READY:
        Evidence is sufficient, assurance checks do not require review,
        and governance does not require human review.
    """

    if (
        evidence_summary[
            "sufficient"
        ]
        is not True
        or evidence_summary[
            "evidence_count"
        ]
        <= 0
    ):
        return BRIEF_UNAVAILABLE

    if (
        governance_summary[
            "requires_human_review"
        ]
        is True
        or assurance_summary[
            "precedence_decision"
        ]
        in {
            "REVIEW_BEFORE_COMBINATION",
            "BLOCK_COMBINATION",
        }
    ):
        return BRIEF_REVIEW_REQUIRED

    return BRIEF_READY


def _build_manager_action(
    brief_status: str,
    governance_summary: dict,
    assurance_summary: dict,
) -> str:
    """Return deterministic manager-facing next action."""

    if (
        brief_status
        == BRIEF_UNAVAILABLE
    ):
        return (
            "Do not rely on this evidence set for an operational "
            "decision. Additional or more suitable evidence is required."
        )

    if (
        assurance_summary[
            "precedence_decision"
        ]
        == "BLOCK_COMBINATION"
    ):
        return (
            "Do not combine the identified evidence automatically. "
            "A human reviewer must resolve the explicit conflict first."
        )

    if (
        brief_status
        == BRIEF_REVIEW_REQUIRED
    ):
        return (
            "Use this brief as review material only. "
            "A human reviewer must assess the evidence before it is "
            "used for an operational decision."
        )

    if (
        governance_summary[
            "may_generate_answer"
        ]
        is True
    ):
        return (
            "The evidence is suitable for the next controlled workflow "
            "step, subject to existing organisational governance."
        )

    return (
        "The evidence is available, but the existing governance "
        "decision must remain authoritative."
    )


def build_manager_evidence_brief(
    packet: dict,
) -> dict:
    """Build a deterministic manager-ready Evidence Brief."""

    packet = _require_mapping(
        packet,
        "packet",
    )

    packet_id = _require_string(
        packet.get(
            "packet_id"
        ),
        "packet_id",
    )

    question = _require_string(
        packet.get(
            "question"
        ),
        "question",
    )

    document_summary = (
        _build_document_summary(
            packet
        )
    )

    evidence_summary = (
        _build_evidence_summary(
            packet
        )
    )

    assurance_summary = (
        _build_assurance_summary(
            packet
        )
    )

    governance_summary = (
        _build_governance_summary(
            packet
        )
    )

    brief_status = (
        _determine_brief_status(
            evidence_summary,
            assurance_summary,
            governance_summary,
        )
    )

    manager_action = (
        _build_manager_action(
            brief_status,
            governance_summary,
            assurance_summary,
        )
    )

    return {
        "brief_version": "1.0",
        "packet_id": packet_id,
        "question": question,
        "brief_status": (
            brief_status
        ),
        "document_summary": (
            document_summary
        ),
        "evidence_summary": (
            evidence_summary
        ),
        "assurance_summary": (
            assurance_summary
        ),
        "governance_summary": (
            governance_summary
        ),
        "manager_action": (
            manager_action
        ),
    }