"""Tests for Week 26 cross-layer safety invariants."""

from __future__ import annotations

from src.evaluation.week26_system_safety_invariants import (
    ABSTAIN,
    INVARIANT_FAIL,
    INVARIANT_PASS,
    PASS,
    REVIEW_REQUIRED,
    audit_case_collection,
    audit_system_safety_invariants,
    authority_not_increased,
)


def test_pass_to_review_is_allowed():
    assert authority_not_increased(
        before=PASS,
        after=REVIEW_REQUIRED,
    ) is True


def test_review_to_pass_is_forbidden():
    assert authority_not_increased(
        before=REVIEW_REQUIRED,
        after=PASS,
    ) is False


def test_abstain_to_review_is_forbidden():
    assert authority_not_increased(
        before=ABSTAIN,
        after=REVIEW_REQUIRED,
    ) is False


def test_clean_pass_case_can_remain_pass():
    result = audit_system_safety_invariants(
        case_id="CLEAN",
        upstream_decision=PASS,
        final_decision=PASS,
        signals={},
    )

    assert result["status"] == INVARIANT_PASS


def test_prompt_injection_can_never_pass():
    result = audit_system_safety_invariants(
        case_id="INJECTION",
        upstream_decision=PASS,
        final_decision=PASS,
        signals={
            "prompt_injection_detected": True,
        },
    )

    assert result["status"] == INVARIANT_FAIL
    assert (
        "prompt_injection_not_passed"
        in result["failed_invariants"]
    )


def test_prompt_injection_review_is_safe():
    result = audit_system_safety_invariants(
        case_id="INJECTION",
        upstream_decision=PASS,
        final_decision=REVIEW_REQUIRED,
        signals={
            "prompt_injection_detected": True,
        },
    )

    assert result["status"] == INVARIANT_PASS


def test_conflict_blocked_case_cannot_pass():
    result = audit_system_safety_invariants(
        case_id="CONFLICT",
        upstream_decision=PASS,
        final_decision=PASS,
        signals={
            "conflict_blocked": True,
        },
    )

    assert result["status"] == INVARIANT_FAIL


def test_expired_evidence_cannot_pass():
    result = audit_system_safety_invariants(
        case_id="TEMPORAL",
        upstream_decision=PASS,
        final_decision=PASS,
        signals={
            "unsafe_temporal_evidence": True,
        },
    )

    assert result["status"] == INVARIANT_FAIL


def test_unsupported_high_risk_claim_cannot_pass():
    result = audit_system_safety_invariants(
        case_id="HIGH-RISK",
        upstream_decision=PASS,
        final_decision=PASS,
        signals={
            "unsupported_high_risk_claim": True,
        },
    )

    assert result["status"] == INVARIANT_FAIL


def test_abstention_violation_must_remain_abstain():
    result = audit_system_safety_invariants(
        case_id="ABSTENTION",
        upstream_decision=ABSTAIN,
        final_decision=ABSTAIN,
        signals={
            "abstention_violation_detected": True,
        },
    )

    assert result["status"] == INVARIANT_PASS


def test_abstention_violation_cannot_be_review():
    result = audit_system_safety_invariants(
        case_id="ABSTENTION",
        upstream_decision=ABSTAIN,
        final_decision=REVIEW_REQUIRED,
        signals={
            "abstention_violation_detected": True,
        },
    )

    assert result["status"] == INVARIANT_FAIL
    assert (
        "abstention_violation_preserves_abstain"
        in result["failed_invariants"]
    )


def test_collection_reports_all_pass():
    report = audit_case_collection(
        [
            {
                "case_id": "C1",
                "upstream_decision": PASS,
                "final_decision": REVIEW_REQUIRED,
                "signals": {
                    "prompt_injection_detected": True,
                },
            },
            {
                "case_id": "C2",
                "upstream_decision": ABSTAIN,
                "final_decision": ABSTAIN,
                "signals": {
                    "abstention_violation_detected": True,
                },
            },
        ]
    )

    assert report["overall_status"] == "PASS"
    assert report["failed_case_ids"] == []


def test_collection_identifies_failed_case():
    report = audit_case_collection(
        [
            {
                "case_id": "C1",
                "upstream_decision": PASS,
                "final_decision": PASS,
                "signals": {
                    "conflict_blocked": True,
                },
            }
        ]
    )

    assert report["overall_status"] == "FAIL"
    assert report["failed_case_ids"] == ["C1"]