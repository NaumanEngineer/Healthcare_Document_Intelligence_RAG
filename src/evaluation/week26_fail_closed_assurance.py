"""Week 26 fail-closed assurance boundary.

This module provides a defensive boundary around the Week 26
system-safety invariant layer.

Day 4 proved that valid assurance states obey cross-layer safety
invariants.

Day 5 asks a different question:

    What happens when assurance inputs themselves are malformed,
    incomplete, unknown, or corrupted?

Core principle:

    Assurance failure must never become answer authority.

If the system cannot safely evaluate an assurance record, the boundary
returns ABSTAIN rather than PASS.

This module does not replace the underlying invariant evaluator.
It protects the system from malformed integration inputs and unexpected
evaluation failures.
"""

from __future__ import annotations

from typing import Any

from src.evaluation.week26_system_safety_invariants import (
    ABSTAIN,
    PASS,
    REVIEW_REQUIRED,
    audit_system_safety_invariants,
)


FAIL_CLOSED = "FAIL_CLOSED"
NORMAL_ASSURANCE = "NORMAL_ASSURANCE"


VALID_DECISIONS = {
    PASS,
    REVIEW_REQUIRED,
    ABSTAIN,
}


def _valid_non_blank_string(
    value: Any,
) -> bool:
    """Return True for a non-blank string."""

    return (
        isinstance(
            value,
            str,
        )
        and bool(
            value.strip()
        )
    )


def _fail_closed_result(
    *,
    case_id: str,
    reason: str,
    error_type: str,
) -> dict[str, Any]:
    """Build a deterministic fail-closed result."""

    return {
        "case_id": case_id,
        "boundary_status": FAIL_CLOSED,
        "final_decision": ABSTAIN,
        "assurance_completed": False,
        "authority_increased": False,
        "error_type": error_type,
        "reason": reason,
        "underlying_result": None,
    }


def safe_audit_system_safety(
    record: Any,
) -> dict[str, Any]:
    """Safely audit a system-safety record.

    Any malformed, incomplete, or unexpected input results in ABSTAIN.

    Expected record:

        {
            "case_id": str,
            "upstream_decision": "PASS" | "REVIEW_REQUIRED" | "ABSTAIN",
            "final_decision": "PASS" | "REVIEW_REQUIRED" | "ABSTAIN",
            "signals": dict,
        }

    The wrapper never converts an input failure into PASS.
    """

    if not isinstance(
        record,
        dict,
    ):
        return _fail_closed_result(
            case_id="UNKNOWN_CASE",
            reason=(
                "System-safety record must be a dictionary."
            ),
            error_type="INVALID_RECORD_TYPE",
        )

    raw_case_id = record.get(
        "case_id"
    )

    case_id = (
        raw_case_id.strip()
        if _valid_non_blank_string(
            raw_case_id
        )
        else "UNKNOWN_CASE"
    )

    if not _valid_non_blank_string(
        raw_case_id
    ):
        return _fail_closed_result(
            case_id=case_id,
            reason=(
                "case_id is missing or blank."
            ),
            error_type="INVALID_CASE_ID",
        )

    if "upstream_decision" not in record:
        return _fail_closed_result(
            case_id=case_id,
            reason=(
                "upstream_decision is missing."
            ),
            error_type="MISSING_UPSTREAM_DECISION",
        )

    if "final_decision" not in record:
        return _fail_closed_result(
            case_id=case_id,
            reason=(
                "final_decision is missing."
            ),
            error_type="MISSING_FINAL_DECISION",
        )

    if "signals" not in record:
        return _fail_closed_result(
            case_id=case_id,
            reason=(
                "signals are missing."
            ),
            error_type="MISSING_SIGNALS",
        )

    upstream_decision = record.get(
        "upstream_decision"
    )

    final_decision = record.get(
        "final_decision"
    )

    signals = record.get(
        "signals"
    )

    if upstream_decision not in VALID_DECISIONS:
        return _fail_closed_result(
            case_id=case_id,
            reason=(
                "Unknown upstream assurance decision: "
                f"{upstream_decision!r}."
            ),
            error_type="UNKNOWN_UPSTREAM_DECISION",
        )

    if final_decision not in VALID_DECISIONS:
        return _fail_closed_result(
            case_id=case_id,
            reason=(
                "Unknown final assurance decision: "
                f"{final_decision!r}."
            ),
            error_type="UNKNOWN_FINAL_DECISION",
        )

    if not isinstance(
        signals,
        dict,
    ):
        return _fail_closed_result(
            case_id=case_id,
            reason=(
                "signals must be a dictionary."
            ),
            error_type="INVALID_SIGNALS_TYPE",
        )

    try:
        result = (
            audit_system_safety_invariants(
                case_id=case_id,
                upstream_decision=(
                    upstream_decision
                ),
                final_decision=(
                    final_decision
                ),
                signals=signals,
            )
        )

    except Exception as exc:
        return _fail_closed_result(
            case_id=case_id,
            reason=(
                "Unexpected system-safety evaluation "
                f"failure: {type(exc).__name__}: {exc}"
            ),
            error_type="ASSURANCE_RUNTIME_FAILURE",
        )

    return {
        "case_id": case_id,
        "boundary_status": (
            NORMAL_ASSURANCE
        ),
        "final_decision": (
            result[
                "final_decision"
            ]
        ),
        "assurance_completed": True,
        "authority_increased": (
            not result[
                "checks"
            ][
                "authority_not_increased"
            ]
        ),
        "error_type": None,
        "reason": (
            "System-safety assurance completed."
        ),
        "underlying_result": (
            result
        ),
    }


def safe_audit_collection(
    records: Any,
) -> dict[str, Any]:
    """Safely audit a collection of system-safety records.

    Invalid collection structure fails closed as a synthetic ABSTAIN
    result rather than raising an uncontrolled exception.
    """

    if not isinstance(
        records,
        list,
    ):
        result = _fail_closed_result(
            case_id="UNKNOWN_CASE",
            reason=(
                "System-safety record collection "
                "must be a list."
            ),
            error_type="INVALID_COLLECTION_TYPE",
        )

        return {
            "record_count": 1,
            "normal_assurance_count": 0,
            "fail_closed_count": 1,
            "pass_decision_count": 0,
            "review_decision_count": 0,
            "abstain_decision_count": 1,
            "fail_closed_case_ids": [
                "UNKNOWN_CASE"
            ],
            "overall_status": (
                FAIL_CLOSED
            ),
            "results": [
                result
            ],
        }

    results = [
        safe_audit_system_safety(
            record
        )
        for record
        in records
    ]

    fail_closed = [
        result
        for result
        in results
        if result[
            "boundary_status"
        ]
        == FAIL_CLOSED
    ]

    normal = [
        result
        for result
        in results
        if result[
            "boundary_status"
        ]
        == NORMAL_ASSURANCE
    ]

    pass_count = sum(
        result[
            "final_decision"
        ]
        == PASS
        for result
        in results
    )

    review_count = sum(
        result[
            "final_decision"
        ]
        == REVIEW_REQUIRED
        for result
        in results
    )

    abstain_count = sum(
        result[
            "final_decision"
        ]
        == ABSTAIN
        for result
        in results
    )

    return {
        "record_count": len(
            results
        ),
        "normal_assurance_count": len(
            normal
        ),
        "fail_closed_count": len(
            fail_closed
        ),
        "pass_decision_count": (
            pass_count
        ),
        "review_decision_count": (
            review_count
        ),
        "abstain_decision_count": (
            abstain_count
        ),
        "fail_closed_case_ids": [
            result[
                "case_id"
            ]
            for result
            in fail_closed
        ],
        "overall_status": (
            FAIL_CLOSED
            if fail_closed
            else NORMAL_ASSURANCE
        ),
        "results": (
            results
        ),
    }