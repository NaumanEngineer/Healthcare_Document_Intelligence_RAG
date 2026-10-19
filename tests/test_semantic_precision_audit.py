"""Tests for Week 26 semantic precision auditing."""

from __future__ import annotations

from src.evaluation.semantic_precision_audit import (
    CLEAR,
    MULTIPLE_PRECISION_RISKS,
    PARTIALLY_SUPPORTED,
    SUPPORTED,
    UNSUPPORTED,
    audit_semantic_precision,
)


def _evidence(
    text: str,
) -> dict:
    return {
        "evidence_id": "E1",
        "status": "active",
        "text": text,
    }


def test_exact_supported_claim_remains_supported():
    result = audit_semantic_precision(
        claim_id="C1",
        claim_text=(
            "Bed occupancy is high."
        ),
        evidence_items=[
            _evidence(
                "Bed occupancy is high."
            )
        ],
        existing_support_status=SUPPORTED,
    )

    assert (
        result[
            "revised_support_status"
        ]
        == SUPPORTED
    )

    assert (
        result[
            "decision"
        ]
        == CLEAR
    )

    assert result[
        "support_reduced"
    ] is False


def test_may_to_expected_reduces_supported_to_partial():
    result = audit_semantic_precision(
        claim_id="C1",
        claim_text=(
            "Escalation is expected to proceed."
        ),
        evidence_items=[
            _evidence(
                "Escalation may be considered "
                "where appropriate."
            )
        ],
        existing_support_status=SUPPORTED,
    )

    assert (
        result[
            "revised_support_status"
        ]
        == PARTIALLY_SUPPORTED
    )

    assert result[
        "modal_strengthening_detected"
    ] is True


def test_may_considered_to_can_reduces_to_partial():
    result = audit_semantic_precision(
        claim_id="C1",
        claim_text=(
            "Elective activity can be reduced."
        ),
        evidence_items=[
            _evidence(
                "Reduction of elective activity "
                "may be considered where appropriate."
            )
        ],
        existing_support_status=SUPPORTED,
    )

    assert (
        result[
            "revised_support_status"
        ]
        == PARTIALLY_SUPPORTED
    )

    assert result[
        "modal_strengthening_detected"
    ] is True


def test_immediacy_without_evidence_becomes_unsupported():
    result = audit_semantic_precision(
        claim_id="C1",
        claim_text=(
            "This should happen immediately."
        ),
        evidence_items=[
            _evidence(
                "Reduction of elective activity "
                "may be considered where appropriate."
            )
        ],
        existing_support_status=PARTIALLY_SUPPORTED,
    )

    assert (
        result[
            "revised_support_status"
        ]
        == UNSUPPORTED
    )

    assert result[
        "immediacy_strengthening_detected"
    ] is True


def test_role_responsibility_requires_explicit_support():
    result = audit_semantic_precision(
        claim_id="C1",
        claim_text=(
            "The site operations manager is responsible "
            "for initiating evacuation."
        ),
        evidence_items=[
            _evidence(
                "Evacuation may be required. "
                "This extract does not identify "
                "the decision-maker."
            )
        ],
        existing_support_status=PARTIALLY_SUPPORTED,
    )

    assert (
        result[
            "revised_support_status"
        ]
        == UNSUPPORTED
    )

    assert result[
        "role_responsibility_unsupported"
    ] is True


def test_explicit_role_responsibility_can_remain_supported():
    result = audit_semantic_precision(
        claim_id="C1",
        claim_text=(
            "The site operations manager is responsible "
            "for initiating evacuation."
        ),
        evidence_items=[
            _evidence(
                "The site operations manager is responsible "
                "for initiating evacuation."
            )
        ],
        existing_support_status=SUPPORTED,
    )

    assert (
        result[
            "revised_support_status"
        ]
        == SUPPORTED
    )

    assert result[
        "role_responsibility_unsupported"
    ] is False


def test_existing_unsupported_status_is_never_upgraded():
    result = audit_semantic_precision(
        claim_id="C1",
        claim_text=(
            "Escalation may be considered."
        ),
        evidence_items=[
            _evidence(
                "Escalation may be considered."
            )
        ],
        existing_support_status=UNSUPPORTED,
    )

    assert (
        result[
            "revised_support_status"
        ]
        == UNSUPPORTED
    )

    assert result[
        "support_reduced"
    ] is False


def test_existing_partial_status_is_never_upgraded():
    result = audit_semantic_precision(
        claim_id="C1",
        claim_text=(
            "Escalation may be considered."
        ),
        evidence_items=[
            _evidence(
                "Escalation may be considered."
            )
        ],
        existing_support_status=PARTIALLY_SUPPORTED,
    )

    assert (
        result[
            "revised_support_status"
        ]
        == PARTIALLY_SUPPORTED
    )


def test_multiple_precision_risks_are_preserved():
    result = audit_semantic_precision(
        claim_id="C1",
        claim_text=(
            "The manager must immediately "
            "initiate evacuation."
        ),
        evidence_items=[
            _evidence(
                "Evacuation may be considered."
            )
        ],
        existing_support_status=SUPPORTED,
    )

    assert (
        result[
            "revised_support_status"
        ]
        == UNSUPPORTED
    )

    assert (
        result[
            "decision"
        ]
        == MULTIPLE_PRECISION_RISKS
    )

    assert len(
        result[
            "risk_signals"
        ]
    ) >= 2