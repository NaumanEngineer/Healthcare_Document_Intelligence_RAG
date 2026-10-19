"""Week 26 cross-layer system safety invariants.

This module does not introduce another content detector.

Instead, it audits the interaction between assurance layers and final
governance decisions.

Core principle:

    Assurance may preserve or reduce authority.
    Assurance must never increase authority.
"""

from __future__ import annotations

from typing import Any


PASS = "PASS"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
ABSTAIN = "ABSTAIN"

INVARIANT_PASS = "INVARIANT_PASS"
INVARIANT_FAIL = "INVARIANT_FAIL"


AUTHORITY_ORDER = {
    ABSTAIN: 0,
    REVIEW_REQUIRED: 1,
    PASS: 2,
}


def authority_level(
    decision: str,
) -> int:
    """Return authority level for a final assurance decision."""

    if decision not in AUTHORITY_ORDER:
        raise ValueError(
            f"Unknown assurance decision: {decision}"
        )

    return AUTHORITY_ORDER[
        decision
    ]


def authority_not_increased(
    *,
    before: str,
    after: str,
) -> bool:
    """Return True when assurance did not increase authority."""

    return (
        authority_level(after)
        <= authority_level(before)
    )


def _unsafe_signal_present(
    signals: dict[str, Any],
) -> bool:
    """Return True when any system-level unsafe condition is present."""

    unsafe_keys = (
        "prompt_injection_detected",
        "conflict_blocked",
        "unsafe_temporal_evidence",
        "unsupported_high_risk_claim",
        "authority_increase_detected",
        "role_hallucination_detected",
        "abstention_violation_detected",
    )

    return any(
        bool(
            signals.get(
                key,
                False,
            )
        )
        for key in unsafe_keys
    )


def audit_system_safety_invariants(
    *,
    case_id: str,
    upstream_decision: str,
    final_decision: str,
    signals: dict[str, Any],
) -> dict[str, Any]:
    """Audit cross-layer safety invariants for one case."""

    if not isinstance(case_id, str) or not case_id.strip():
        raise ValueError(
            "case_id must be a non-blank string."
        )

    if not isinstance(signals, dict):
        raise TypeError(
            "signals must be a dictionary."
        )

    authority_safe = authority_not_increased(
        before=upstream_decision,
        after=final_decision,
    )

    unsafe_signal = _unsafe_signal_present(
        signals
    )

    unsafe_not_passed = not (
        unsafe_signal
        and final_decision == PASS
    )

    abstain_preserved = not (
        upstream_decision == ABSTAIN
        and final_decision != ABSTAIN
    )

    review_not_upgraded = not (
        upstream_decision == REVIEW_REQUIRED
        and final_decision == PASS
    )

    abstention_violation_safe = not (
        signals.get(
            "abstention_violation_detected",
            False,
        )
        and final_decision != ABSTAIN
    )

    prompt_injection_safe = not (
        signals.get(
            "prompt_injection_detected",
            False,
        )
        and final_decision == PASS
    )

    conflict_safe = not (
        signals.get(
            "conflict_blocked",
            False,
        )
        and final_decision == PASS
    )

    temporal_safe = not (
        signals.get(
            "unsafe_temporal_evidence",
            False,
        )
        and final_decision == PASS
    )

    high_risk_claim_safe = not (
        signals.get(
            "unsupported_high_risk_claim",
            False,
        )
        and final_decision == PASS
    )

    checks = {
        "authority_not_increased": authority_safe,
        "unsafe_signal_not_passed": unsafe_not_passed,
        "upstream_abstain_preserved": abstain_preserved,
        "review_not_upgraded_to_pass": review_not_upgraded,
        "abstention_violation_preserves_abstain": (
            abstention_violation_safe
        ),
        "prompt_injection_not_passed": (
            prompt_injection_safe
        ),
        "conflict_not_passed": (
            conflict_safe
        ),
        "unsafe_temporal_evidence_not_passed": (
            temporal_safe
        ),
        "unsupported_high_risk_claim_not_passed": (
            high_risk_claim_safe
        ),
    }

    failed_invariants = [
        name
        for name, passed in checks.items()
        if not passed
    ]

    passed = not failed_invariants

    return {
        "case_id": case_id,
        "status": (
            INVARIANT_PASS
            if passed
            else INVARIANT_FAIL
        ),
        "upstream_decision": upstream_decision,
        "final_decision": final_decision,
        "upstream_authority_level": (
            authority_level(
                upstream_decision
            )
        ),
        "final_authority_level": (
            authority_level(
                final_decision
            )
        ),
        "unsafe_signal_present": unsafe_signal,
        "signals": signals,
        "checks": checks,
        "failed_invariants": failed_invariants,
    }


def audit_case_collection(
    cases: list[dict[str, Any]],
) -> dict[str, Any]:
    """Audit a collection of system-level case records."""

    if not isinstance(cases, list):
        raise TypeError(
            "cases must be a list."
        )

    results = []

    for case in cases:
        results.append(
            audit_system_safety_invariants(
                case_id=case["case_id"],
                upstream_decision=case[
                    "upstream_decision"
                ],
                final_decision=case[
                    "final_decision"
                ],
                signals=case.get(
                    "signals",
                    {},
                ),
            )
        )

    failed = [
        result
        for result in results
        if result["status"]
        == INVARIANT_FAIL
    ]

    return {
        "case_count": len(results),
        "passed_case_count": (
            len(results)
            - len(failed)
        ),
        "failed_case_count": len(failed),
        "failed_case_ids": [
            result["case_id"]
            for result in failed
        ],
        "overall_status": (
            "PASS"
            if not failed
            else "FAIL"
        ),
        "results": results,
    }