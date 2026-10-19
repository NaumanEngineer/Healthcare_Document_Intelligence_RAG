"""Week 26 failure-injection robustness benchmark.

This benchmark deliberately supplies malformed and incomplete assurance
records to the fail-closed boundary.

Purpose:

    prove that broken assurance inputs never become PASS.

Failure classes include:

- invalid record type;
- missing case identifier;
- missing upstream decision;
- missing final decision;
- missing safety signals;
- unknown upstream state;
- unknown final state;
- malformed signal container;
- mixed valid and invalid collections.

Core principle:

    Assurance failure is itself a safety event.

Run with:

    python -m src.evaluation.run_week26_failure_injection_benchmark
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT),
    )


from src.evaluation.week26_fail_closed_assurance import (
    ABSTAIN,
    FAIL_CLOSED,
    NORMAL_ASSURANCE,
    safe_audit_collection,
    safe_audit_system_safety,
)


OUTPUT_PATH = (
    ROOT
    / "outputs"
    / "week26_failure_injection_benchmark.json"
)


def _failure_cases() -> list[dict[str, Any]]:
    """Return controlled robustness test cases."""

    return [
        {
            "case_id": "W26-FI-001",
            "case_name": "invalid_record_type",
            "input": "not-a-dictionary",
            "expected_boundary_status": FAIL_CLOSED,
            "expected_final_decision": ABSTAIN,
            "expected_error_type": "INVALID_RECORD_TYPE",
        },
        {
            "case_id": "W26-FI-002",
            "case_name": "missing_case_id",
            "input": {
                "upstream_decision": "PASS",
                "final_decision": "REVIEW_REQUIRED",
                "signals": {},
            },
            "expected_boundary_status": FAIL_CLOSED,
            "expected_final_decision": ABSTAIN,
            "expected_error_type": "INVALID_CASE_ID",
        },
        {
            "case_id": "W26-FI-003",
            "case_name": "missing_upstream_decision",
            "input": {
                "case_id": "W26-FI-003",
                "final_decision": "REVIEW_REQUIRED",
                "signals": {},
            },
            "expected_boundary_status": FAIL_CLOSED,
            "expected_final_decision": ABSTAIN,
            "expected_error_type": "MISSING_UPSTREAM_DECISION",
        },
        {
            "case_id": "W26-FI-004",
            "case_name": "missing_final_decision",
            "input": {
                "case_id": "W26-FI-004",
                "upstream_decision": "PASS",
                "signals": {},
            },
            "expected_boundary_status": FAIL_CLOSED,
            "expected_final_decision": ABSTAIN,
            "expected_error_type": "MISSING_FINAL_DECISION",
        },
        {
            "case_id": "W26-FI-005",
            "case_name": "missing_signals",
            "input": {
                "case_id": "W26-FI-005",
                "upstream_decision": "PASS",
                "final_decision": "REVIEW_REQUIRED",
            },
            "expected_boundary_status": FAIL_CLOSED,
            "expected_final_decision": ABSTAIN,
            "expected_error_type": "MISSING_SIGNALS",
        },
        {
            "case_id": "W26-FI-006",
            "case_name": "unknown_upstream_decision",
            "input": {
                "case_id": "W26-FI-006",
                "upstream_decision": "AUTO_MAGIC",
                "final_decision": "REVIEW_REQUIRED",
                "signals": {},
            },
            "expected_boundary_status": FAIL_CLOSED,
            "expected_final_decision": ABSTAIN,
            "expected_error_type": "UNKNOWN_UPSTREAM_DECISION",
        },
        {
            "case_id": "W26-FI-007",
            "case_name": "unknown_final_decision",
            "input": {
                "case_id": "W26-FI-007",
                "upstream_decision": "PASS",
                "final_decision": "SAFE_ENOUGH",
                "signals": {},
            },
            "expected_boundary_status": FAIL_CLOSED,
            "expected_final_decision": ABSTAIN,
            "expected_error_type": "UNKNOWN_FINAL_DECISION",
        },
        {
            "case_id": "W26-FI-008",
            "case_name": "malformed_signals",
            "input": {
                "case_id": "W26-FI-008",
                "upstream_decision": "PASS",
                "final_decision": "REVIEW_REQUIRED",
                "signals": [
                    "prompt_injection_detected"
                ],
            },
            "expected_boundary_status": FAIL_CLOSED,
            "expected_final_decision": ABSTAIN,
            "expected_error_type": "INVALID_SIGNALS_TYPE",
        },
        {
            "case_id": "W26-FI-009",
            "case_name": "blank_case_id",
            "input": {
                "case_id": "   ",
                "upstream_decision": "PASS",
                "final_decision": "REVIEW_REQUIRED",
                "signals": {},
            },
            "expected_boundary_status": FAIL_CLOSED,
            "expected_final_decision": ABSTAIN,
            "expected_error_type": "INVALID_CASE_ID",
        },
        {
            "case_id": "W26-FI-010",
            "case_name": "valid_control_record",
            "input": {
                "case_id": "W26-FI-010",
                "upstream_decision": "PASS",
                "final_decision": "REVIEW_REQUIRED",
                "signals": {
                    "prompt_injection_detected": True,
                },
            },
            "expected_boundary_status": NORMAL_ASSURANCE,
            "expected_final_decision": "REVIEW_REQUIRED",
            "expected_error_type": None,
        },
    ]


def _run_case(
    case: dict[str, Any],
) -> dict[str, Any]:
    """Run one failure-injection case."""

    result = safe_audit_system_safety(
        case[
            "input"
        ]
    )

    boundary_matches = (
        result[
            "boundary_status"
        ]
        == case[
            "expected_boundary_status"
        ]
    )

    decision_matches = (
        result[
            "final_decision"
        ]
        == case[
            "expected_final_decision"
        ]
    )

    error_matches = (
        result[
            "error_type"
        ]
        == case[
            "expected_error_type"
        ]
    )

    never_unsafe_pass = not (
        result[
            "boundary_status"
        ]
        == FAIL_CLOSED
        and result[
            "final_decision"
        ]
        == "PASS"
    )

    case_match = all(
        (
            boundary_matches,
            decision_matches,
            error_matches,
            never_unsafe_pass,
        )
    )

    failure_reasons = []

    if not boundary_matches:
        failure_reasons.append(
            "Boundary status mismatch."
        )

    if not decision_matches:
        failure_reasons.append(
            "Final decision mismatch."
        )

    if not error_matches:
        failure_reasons.append(
            "Error type mismatch."
        )

    if not never_unsafe_pass:
        failure_reasons.append(
            "Fail-closed input incorrectly produced PASS."
        )

    return {
        "case_id": case[
            "case_id"
        ],
        "case_name": case[
            "case_name"
        ],
        "expected_boundary_status": case[
            "expected_boundary_status"
        ],
        "actual_boundary_status": result[
            "boundary_status"
        ],
        "expected_final_decision": case[
            "expected_final_decision"
        ],
        "actual_final_decision": result[
            "final_decision"
        ],
        "expected_error_type": case[
            "expected_error_type"
        ],
        "actual_error_type": result[
            "error_type"
        ],
        "never_unsafe_pass": (
            never_unsafe_pass
        ),
        "case_match": (
            case_match
        ),
        "failure_reasons": (
            failure_reasons
        ),
        "boundary_result": (
            result
        ),
    }


def _run_collection_failure_case() -> dict[str, Any]:
    """Exercise malformed collection input."""

    result = safe_audit_collection(
        {
            "invalid": "collection"
        }
    )

    matched = (
        result[
            "overall_status"
        ]
        == FAIL_CLOSED
        and result[
            "fail_closed_count"
        ]
        == 1
        and result[
            "abstain_decision_count"
        ]
        == 1
        and result[
            "pass_decision_count"
        ]
        == 0
    )

    return {
        "case_id": "W26-FI-011",
        "case_name": (
            "invalid_collection_type"
        ),
        "expected_boundary_status": (
            FAIL_CLOSED
        ),
        "actual_boundary_status": (
            result[
                "overall_status"
            ]
        ),
        "expected_final_decision": (
            ABSTAIN
        ),
        "actual_final_decision": (
            ABSTAIN
            if result[
                "abstain_decision_count"
            ]
            == 1
            else "UNKNOWN"
        ),
        "expected_error_type": (
            "INVALID_COLLECTION_TYPE"
        ),
        "actual_error_type": (
            result[
                "results"
            ][0][
                "error_type"
            ]
        ),
        "never_unsafe_pass": (
            result[
                "pass_decision_count"
            ]
            == 0
        ),
        "case_match": (
            matched
        ),
        "failure_reasons": (
            []
            if matched
            else [
                "Invalid collection did not fail closed."
            ]
        ),
        "boundary_result": (
            result
        ),
    }


def run_failure_injection_benchmark() -> dict[str, Any]:
    """Execute Week 26 failure-injection benchmark."""

    results = [
        _run_case(
            case
        )
        for case
        in _failure_cases()
    ]

    results.append(
        _run_collection_failure_case()
    )

    matched = [
        result
        for result
        in results
        if result[
            "case_match"
        ]
    ]

    mismatched = [
        result
        for result
        in results
        if not result[
            "case_match"
        ]
    ]

    fail_closed_cases = [
        result[
            "case_id"
        ]
        for result
        in results
        if result[
            "actual_boundary_status"
        ]
        == FAIL_CLOSED
    ]

    unsafe_passes = [
        result[
            "case_id"
        ]
        for result
        in results
        if not result[
            "never_unsafe_pass"
        ]
    ]

    report = {
        "benchmark_name": (
            "Week 26 Failure Injection Benchmark"
        ),
        "benchmark_version": "1.0",
        "evaluation_type": (
            "week26_fail_closed_robustness"
        ),
        "summary": {
            "case_count": len(
                results
            ),
            "matched_case_count": len(
                matched
            ),
            "mismatched_case_count": len(
                mismatched
            ),
            "match_rate": (
                round(
                    len(
                        matched
                    )
                    / len(
                        results
                    ),
                    4,
                )
            ),
            "fail_closed_case_count": len(
                fail_closed_cases
            ),
            "fail_closed_case_ids": (
                fail_closed_cases
            ),
            "unsafe_pass_case_ids": (
                unsafe_passes
            ),
            "mismatched_case_ids": [
                result[
                    "case_id"
                ]
                for result
                in mismatched
            ],
            "overall_status": (
                "PASS"
                if (
                    not mismatched
                    and not unsafe_passes
                )
                else "FAIL"
            ),
        },
        "results": (
            results
        ),
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return report


def _print_summary(
    report: dict[str, Any],
) -> None:
    """Print concise robustness benchmark result."""

    summary = report[
        "summary"
    ]

    print(
        "Week 26 Failure Injection Benchmark"
    )

    print(
        "-----------------------------------"
    )

    print(
        f"Overall status: {summary['overall_status']}"
    )

    print(
        f"Cases: {summary['case_count']}"
    )

    print(
        "Matched: "
        f"{summary['matched_case_count']}/"
        f"{summary['case_count']}"
    )

    print(
        "Fail-closed cases: "
        f"{summary['fail_closed_case_count']}"
    )

    print(
        "Unsafe PASS cases: "
        f"{summary['unsafe_pass_case_ids']}"
    )

    print(
        "Mismatched cases: "
        f"{summary['mismatched_case_ids']}"
    )

    print(
        f"Output: {OUTPUT_PATH}"
    )

    if summary[
        "overall_status"
    ] != "PASS":
        raise SystemExit(
            1
        )


def main() -> None:
    """CLI entry point."""

    report = (
        run_failure_injection_benchmark()
    )

    _print_summary(
        report
    )


if __name__ == "__main__":
    main()