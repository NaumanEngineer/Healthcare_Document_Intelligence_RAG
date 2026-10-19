"""Focused Week 26 abstention-safety benchmark.

Target:

    W26-C011 - Unsafe Abstention Formatting

Purpose:

Prove that an ABSTAIN governance decision is not considered fully safe
merely because the overall response type is abstention.

The response body must also remain:

- non-directive;
- uncertainty preserving;
- free from unsupported authority;
- free from assumed operational action.

Run with:

    python -m src.evaluation.run_week26_abstention_safety_benchmark
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


from src.evaluation.abstention_safety import (
    audit_abstention_safety,
)
from src.evaluation.validate_week26_benchmark import (
    BENCHMARK_PATH,
    validate_benchmark,
)


OUTPUT_PATH = (
    ROOT
    / "outputs"
    / "week26_abstention_safety_benchmark.json"
)


TARGET_CASE_ID = "W26-C011"


def _load_benchmark() -> dict[str, Any]:
    """Load and validate the authoritative Week 26 benchmark."""

    with Path(
        BENCHMARK_PATH
    ).open(
        "r",
        encoding="utf-8",
    ) as file:
        benchmark = json.load(
            file
        )

    validate_benchmark(
        benchmark
    )

    return benchmark


def _target_case(
    benchmark: dict[str, Any],
) -> dict[str, Any]:
    """Return C011 from the benchmark."""

    for case in benchmark[
        "cases"
    ]:
        if case[
            "case_id"
        ] == TARGET_CASE_ID:
            return case

    raise ValueError(
        f"Benchmark missing required case {TARGET_CASE_ID}."
    )


def _candidate_response(
    case: dict[str, Any],
) -> dict[str, Any]:
    """Return the structured abstention response.

    C011 is expected to contain a candidate_response object with the
    governed abstention sections defined by the Week 26 data contract.
    """

    response = case.get(
        "candidate_response"
    )

    if not isinstance(
        response,
        dict,
    ):
        raise ValueError(
            f"{case['case_id']} must contain a "
            "candidate_response dictionary."
        )

    return response


def _run_case(
    case: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate C011 through abstention safety."""

    response = (
        _candidate_response(
            case
        )
    )

    assurance = (
        audit_abstention_safety(
            response
        )
    )

    expected_abstention = case[
        "expected_abstention_decision"
    ]

    actual_abstention = assurance[
        "decision"
    ]

    abstention_matches = (
        actual_abstention
        == expected_abstention
    )

    expected_final = case[
        "expected_final_assurance_decision"
    ]

    # The content audit must never promote an ABSTAIN case to ANSWER.
    #
    # C011 remains ABSTAIN at the final governance level even though
    # the abstention body contains unsafe directive leakage.
    final_decision = (
        "ABSTAIN"
        if case[
            "expected_governance_decision"
        ] == "ABSTAIN"
        else expected_final
    )

    final_matches = (
        final_decision
        == expected_final
    )

    violation_expected = case[
        "abstention_violation_expected"
    ]

    violation_actual = (
        actual_abstention
        != "SAFE_ABSTENTION"
    )

    violation_matches = (
        violation_actual
        == violation_expected
    )

    case_match = all(
        (
            abstention_matches,
            final_matches,
            violation_matches,
        )
    )

    failure_reasons = []

    if not abstention_matches:
        failure_reasons.append(
            "Abstention-safety mismatch: "
            f"expected {expected_abstention}, "
            f"got {actual_abstention}"
        )

    if not violation_matches:
        failure_reasons.append(
            "Abstention violation flag mismatch: "
            f"expected {violation_expected}, "
            f"got {violation_actual}"
        )

    if not final_matches:
        failure_reasons.append(
            "Final assurance mismatch: "
            f"expected {expected_final}, "
            f"got {final_decision}"
        )

    return {
        "case_id": case[
            "case_id"
        ],
        "case_name": case[
            "case_name"
        ],
        "expected_governance_decision": case[
            "expected_governance_decision"
        ],
        "expected_response_type": case[
            "expected_response_type"
        ],
        "expected_abstention_decision": (
            expected_abstention
        ),
        "actual_abstention_decision": (
            actual_abstention
        ),
        "expected_abstention_violation": (
            violation_expected
        ),
        "actual_abstention_violation": (
            violation_actual
        ),
        "expected_final_assurance_decision": (
            expected_final
        ),
        "actual_final_assurance_decision": (
            final_decision
        ),
        "candidate_response": (
            response
        ),
        "directive_leakage_detected": assurance[
            "directive_leakage_detected"
        ],
        "authority_leakage_detected": assurance[
            "authority_leakage_detected"
        ],
        "unsupported_certainty_detected": assurance[
            "unsupported_certainty_detected"
        ],
        "action_assumption_detected": assurance[
            "action_assumption_detected"
        ],
        "structure_valid": assurance[
            "structure_valid"
        ],
        "risk_signals": assurance[
            "risk_signals"
        ],
        "directive_sections": assurance.get(
            "directive_sections",
            [],
        ),
        "case_match": (
            case_match
        ),
        "assurance": assurance,
        "failure_reasons": (
            failure_reasons
        ),
    }


def run_abstention_safety_benchmark() -> dict[str, Any]:
    """Execute focused C011 abstention-safety benchmark."""

    benchmark = _load_benchmark()

    case = _target_case(
        benchmark
    )

    result = _run_case(
        case
    )

    summary = {
        "case_count": 1,
        "matched_case_count": (
            1
            if result[
                "case_match"
            ]
            else 0
        ),
        "mismatched_case_count": (
            0
            if result[
                "case_match"
            ]
            else 1
        ),
        "match_rate": (
            1.0
            if result[
                "case_match"
            ]
            else 0.0
        ),
        "directive_leakage_case_ids": (
            [
                result[
                    "case_id"
                ]
            ]
            if result[
                "directive_leakage_detected"
            ]
            else []
        ),
        "final_abstain_case_ids": (
            [
                result[
                    "case_id"
                ]
            ]
            if result[
                "actual_final_assurance_decision"
            ]
            == "ABSTAIN"
            else []
        ),
        "mismatched_case_ids": (
            []
            if result[
                "case_match"
            ]
            else [
                result[
                    "case_id"
                ]
            ]
        ),
    }

    report = {
        "benchmark_name": (
            "Week 26 Abstention Safety Benchmark"
        ),
        "benchmark_version": "1.0",
        "source_benchmark": benchmark[
            "benchmark_name"
        ],
        "evaluation_type": (
            "week26_abstention_safety_hardening"
        ),
        "target_case_id": (
            TARGET_CASE_ID
        ),
        "summary": (
            summary
        ),
        "results": [
            result
        ],
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
    """Print concise C011 benchmark summary."""

    summary = report[
        "summary"
    ]

    result = report[
        "results"
    ][0]

    print(
        "Week 26 Abstention Safety Benchmark"
    )

    print(
        "-----------------------------------"
    )

    print(
        f"Cases: {summary['case_count']}"
    )

    print(
        f"Matched: {summary['matched_case_count']}"
    )

    print(
        f"Mismatched: {summary['mismatched_case_count']}"
    )

    print(
        f"Match rate: {summary['match_rate']:.1%}"
    )

    print(
        "Expected abstention decision: "
        f"{result['expected_abstention_decision']}"
    )

    print(
        "Actual abstention decision: "
        f"{result['actual_abstention_decision']}"
    )

    print(
        "Directive leakage detected: "
        f"{result['directive_leakage_detected']}"
    )

    print(
        "Expected final assurance: "
        f"{result['expected_final_assurance_decision']}"
    )

    print(
        "Actual final assurance: "
        f"{result['actual_final_assurance_decision']}"
    )

    print(
        "Mismatched cases: "
        f"{summary['mismatched_case_ids']}"
    )

    print(
        f"Output: {OUTPUT_PATH}"
    )


def main() -> None:
    """CLI entry point."""

    report = (
        run_abstention_safety_benchmark()
    )

    _print_summary(
        report
    )


if __name__ == "__main__":
    main()