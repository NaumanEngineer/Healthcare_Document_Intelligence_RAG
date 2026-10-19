"""Focused Week 26 prompt-injection benchmark.

Target:

    W26-C009 - Prompt Injection Inside Retrieved Evidence

Purpose:

Prove that retrieved evidence is treated as untrusted content and
cannot override governance, suppress conflict, or control the response.

Run with:

    python -m src.evaluation.run_week26_prompt_injection_benchmark
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


from src.evaluation.evidence_prompt_injection import (
    assess_evidence_prompt_injection,
)
from src.evaluation.validate_week26_benchmark import (
    BENCHMARK_PATH,
    validate_benchmark,
)


OUTPUT_PATH = (
    ROOT
    / "outputs"
    / "week26_prompt_injection_benchmark.json"
)


TARGET_CASE_ID = "W26-C009"


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
    """Return the required prompt-injection benchmark case."""

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


def _run_case(
    case: dict[str, Any],
) -> dict[str, Any]:
    """Run C009 through the retrieved-evidence injection detector."""

    assurance = (
        assess_evidence_prompt_injection(
            case[
                "evidence_items"
            ]
        )
    )

    expected = case[
        "expected_prompt_injection_decision"
    ]

    actual = assurance[
        "decision"
    ]

    decision_matches = (
        expected == actual
    )

    prompt_expected = case[
        "prompt_injection_expected"
    ]

    detection_matches = (
        assurance[
            "injection_detected"
        ]
        == prompt_expected
    )

    case_match = (
        decision_matches
        and detection_matches
    )

    failure_reasons = []

    if not decision_matches:
        failure_reasons.append(
            "Prompt-injection decision mismatch: "
            f"expected {expected}, got {actual}"
        )

    if not detection_matches:
        failure_reasons.append(
            "Prompt-injection detection mismatch: "
            f"expected {prompt_expected}, got "
            f"{assurance['injection_detected']}"
        )

    return {
        "case_id": case[
            "case_id"
        ],
        "case_name": case[
            "case_name"
        ],
        "expected_prompt_injection_decision": (
            expected
        ),
        "actual_prompt_injection_decision": (
            actual
        ),
        "expected_injection_detected": (
            prompt_expected
        ),
        "actual_injection_detected": (
            assurance[
                "injection_detected"
            ]
        ),
        "injection_evidence_ids": (
            assurance[
                "injection_evidence_ids"
            ]
        ),
        "governance_override_evidence_ids": (
            assurance[
                "governance_override_evidence_ids"
            ]
        ),
        "conflict_suppression_evidence_ids": (
            assurance[
                "conflict_suppression_evidence_ids"
            ]
        ),
        "authority_override_evidence_ids": (
            assurance[
                "authority_override_evidence_ids"
            ]
        ),
        "response_override_evidence_ids": (
            assurance[
                "response_override_evidence_ids"
            ]
        ),
        "case_match": (
            case_match
        ),
        "assurance": assurance,
        "failure_reasons": (
            failure_reasons
        ),
    }


def run_prompt_injection_benchmark() -> dict[str, Any]:
    """Execute focused prompt-injection benchmark."""

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
        "injection_evidence_ids": (
            result[
                "injection_evidence_ids"
            ]
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
            "Week 26 Prompt Injection Benchmark"
        ),
        "benchmark_version": "1.0",
        "source_benchmark": benchmark[
            "benchmark_name"
        ],
        "evaluation_type": (
            "week26_prompt_injection_hardening"
        ),
        "target_case_id": (
            TARGET_CASE_ID
        ),
        "summary": summary,
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
    """Print concise benchmark evidence."""

    summary = report[
        "summary"
    ]

    result = report[
        "results"
    ][0]

    print(
        "Week 26 Prompt Injection Benchmark"
    )

    print(
        "----------------------------------"
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
        "Expected decision: "
        f"{result['expected_prompt_injection_decision']}"
    )

    print(
        "Actual decision: "
        f"{result['actual_prompt_injection_decision']}"
    )

    print(
        "Injection evidence IDs: "
        f"{summary['injection_evidence_ids']}"
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
        run_prompt_injection_benchmark()
    )

    _print_summary(
        report
    )


if __name__ == "__main__":
    main()