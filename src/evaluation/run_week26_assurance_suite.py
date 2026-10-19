"""Unified Week 26 adversarial assurance suite.

This runner combines the Week 26 benchmark validator, existing-stack
baseline evidence, and the new standalone adversarial controls.

Dedicated Week 26 controls:

    C001, C012
        relationship-aware groundedness

    C003, C007, C008
        semantic precision

    C004, C005
        version and temporal assurance

    C009
        retrieved-evidence prompt injection

    C011
        abstention safety

Regression-anchor cases:

    C002, C006, C010

These anchor cases already had correct claim and final-governance
outcomes in the BEFORE baseline. Their earlier exact-case mismatch was
caused by detector-state vocabulary differences rather than an unsafe
final decision.

Core principle:

    Detector labels are not governance decisions.

Run with:

    python -m src.evaluation.run_week26_assurance_suite
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


from src.evaluation.run_week26_abstention_safety_benchmark import (
    run_abstention_safety_benchmark,
)
from src.evaluation.run_week26_prompt_injection_benchmark import (
    run_prompt_injection_benchmark,
)
from src.evaluation.run_week26_relationship_groundedness_benchmark import (
    run_relationship_benchmark,
)
from src.evaluation.run_week26_semantic_precision_benchmark import (
    run_semantic_precision_benchmark,
)
from src.evaluation.run_week26_version_temporal_benchmark import (
    run_version_temporal_benchmark,
)
from src.evaluation.validate_week26_benchmark import (
    BENCHMARK_PATH,
    validate_benchmark,
)


BASELINE_OUTPUT_PATH = (
    ROOT
    / "outputs"
    / "week26_existing_stack_baseline.json"
)


JSON_OUTPUT_PATH = (
    ROOT
    / "outputs"
    / "week26_automated_assurance_report.json"
)


MARKDOWN_OUTPUT_PATH = (
    ROOT
    / "outputs"
    / "week26_automated_assurance_report.md"
)


DEDICATED_CASE_IDS = {
    "W26-C001",
    "W26-C003",
    "W26-C004",
    "W26-C005",
    "W26-C007",
    "W26-C008",
    "W26-C009",
    "W26-C011",
    "W26-C012",
}


ANCHOR_CASE_IDS = {
    "W26-C002",
    "W26-C006",
    "W26-C010",
}


ALL_EXPECTED_CASE_IDS = {
    *(f"W26-C{number:03d}" for number in range(1, 13))
}


def _load_json(
    path: Path,
) -> dict[str, Any]:
    """Load a JSON file."""

    if not path.exists():
        raise FileNotFoundError(
            f"Required file does not exist: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(
            file
        )


def _load_benchmark() -> dict[str, Any]:
    """Load and validate authoritative Week 26 benchmark."""

    benchmark = _load_json(
        Path(
            BENCHMARK_PATH
        )
    )

    validate_benchmark(
        benchmark
    )

    return benchmark


def _load_baseline() -> dict[str, Any]:
    """Load the immutable BEFORE baseline output."""

    return _load_json(
        BASELINE_OUTPUT_PATH
    )


def _baseline_results(
    baseline: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return baseline per-case results."""

    results = baseline.get(
        "results"
    )

    if not isinstance(
        results,
        list,
    ):
        raise ValueError(
            "Week 26 baseline output must contain a results list."
        )

    return results


def _baseline_case_lookup(
    baseline: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Index baseline cases."""

    return {
        result[
            "case_id"
        ]: result
        for result
        in _baseline_results(
            baseline
        )
    }


def _claim_statuses_match(
    result: dict[str, Any],
) -> bool:
    """Compare expected and actual baseline claim-status mappings."""

    return (
        result.get(
            "expected_claim_statuses"
        )
        == result.get(
            "actual_claim_statuses"
        )
    )


def _final_decision_matches(
    result: dict[str, Any],
) -> bool:
    """Compare expected and actual final governance decision."""

    return (
        result.get(
            "expected_final_assurance_decision"
        )
        == result.get(
            "actual_final_assurance_decision"
        )
    )


def _run_dedicated_controls() -> dict[str, Any]:
    """Execute all dedicated Week 26 control benchmarks."""

    relationship = (
        run_relationship_benchmark()
    )

    semantic = (
        run_semantic_precision_benchmark()
    )

    temporal = (
        run_version_temporal_benchmark()
    )

    injection = (
        run_prompt_injection_benchmark()
    )

    abstention = (
        run_abstention_safety_benchmark()
    )

    return {
        "relationship_groundedness": (
            relationship
        ),
        "semantic_precision": (
            semantic
        ),
        "version_temporal": (
            temporal
        ),
        "prompt_injection": (
            injection
        ),
        "abstention_safety": (
            abstention
        ),
    }


def _dedicated_case_results(
    controls: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Create one normalized result for every dedicated case."""

    normalized: dict[str, dict[str, Any]] = {}

    relationship = controls[
        "relationship_groundedness"
    ]

    for result in relationship[
        "results"
    ]:
        normalized[
            result[
                "case_id"
            ]
        ] = {
            "control": (
                "relationship_groundedness"
            ),
            "matched": result[
                "case_match"
            ],
            "failure_reasons": result.get(
                "failure_reasons",
                [],
            ),
        }

    semantic = controls[
        "semantic_precision"
    ]

    for result in semantic[
        "results"
    ]:
        normalized[
            result[
                "case_id"
            ]
        ] = {
            "control": (
                "semantic_precision"
            ),
            "matched": result[
                "case_match"
            ],
            "failure_reasons": result.get(
                "failure_reasons",
                [],
            ),
        }

    temporal = controls[
        "version_temporal"
    ]

    for result in temporal[
        "results"
    ]:
        normalized[
            result[
                "case_id"
            ]
        ] = {
            "control": (
                "version_temporal"
            ),
            "matched": result[
                "case_match"
            ],
            "failure_reasons": result.get(
                "failure_reasons",
                [],
            ),
        }

    injection = controls[
        "prompt_injection"
    ]

    for result in injection[
        "results"
    ]:
        normalized[
            result[
                "case_id"
            ]
        ] = {
            "control": (
                "prompt_injection"
            ),
            "matched": result[
                "case_match"
            ],
            "failure_reasons": result.get(
                "failure_reasons",
                [],
            ),
        }

    abstention = controls[
        "abstention_safety"
    ]

    for result in abstention[
        "results"
    ]:
        normalized[
            result[
                "case_id"
            ]
        ] = {
            "control": (
                "abstention_safety"
            ),
            "matched": result[
                "case_match"
            ],
            "failure_reasons": result.get(
                "failure_reasons",
                [],
            ),
        }

    return normalized


def _anchor_case_results(
    baseline: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Evaluate the three regression-anchor cases.

    Exact detector-state vocabulary is intentionally excluded here.

    The safety questions are:

    1. Did claim support match the benchmark?
    2. Did final governance match the benchmark?

    Both must be true.
    """

    lookup = _baseline_case_lookup(
        baseline
    )

    normalized = {}

    for case_id in sorted(
        ANCHOR_CASE_IDS
    ):
        if case_id not in lookup:
            raise ValueError(
                f"Baseline missing anchor case {case_id}."
            )

        result = lookup[
            case_id
        ]

        claims_match = (
            _claim_statuses_match(
                result
            )
        )

        final_match = (
            _final_decision_matches(
                result
            )
        )

        matched = (
            claims_match
            and final_match
        )

        failure_reasons = []

        if not claims_match:
            failure_reasons.append(
                "Claim support statuses do not match benchmark."
            )

        if not final_match:
            failure_reasons.append(
                "Final assurance decision does not match benchmark."
            )

        normalized[
            case_id
        ] = {
            "control": (
                "existing_stack_regression_anchor"
            ),
            "matched": matched,
            "claim_statuses_match": (
                claims_match
            ),
            "final_decision_matches": (
                final_match
            ),
            "expected_claim_statuses": result.get(
                "expected_claim_statuses"
            ),
            "actual_claim_statuses": result.get(
                "actual_claim_statuses"
            ),
            "expected_final_assurance_decision": result.get(
                "expected_final_assurance_decision"
            ),
            "actual_final_assurance_decision": result.get(
                "actual_final_assurance_decision"
            ),
            "failure_reasons": (
                failure_reasons
            ),
        }

    return normalized


def _validate_case_coverage(
    dedicated: dict[str, dict[str, Any]],
    anchors: dict[str, dict[str, Any]],
) -> None:
    """Require complete, non-overlapping 12-case coverage."""

    dedicated_ids = set(
        dedicated
    )

    anchor_ids = set(
        anchors
    )

    if (
        dedicated_ids
        != DEDICATED_CASE_IDS
    ):
        raise ValueError(
            "Dedicated-control case coverage mismatch. "
            f"Expected {sorted(DEDICATED_CASE_IDS)}, "
            f"got {sorted(dedicated_ids)}."
        )

    if (
        anchor_ids
        != ANCHOR_CASE_IDS
    ):
        raise ValueError(
            "Anchor-case coverage mismatch. "
            f"Expected {sorted(ANCHOR_CASE_IDS)}, "
            f"got {sorted(anchor_ids)}."
        )

    overlap = (
        dedicated_ids
        & anchor_ids
    )

    if overlap:
        raise ValueError(
            "Cases cannot be both dedicated controls "
            f"and anchors: {sorted(overlap)}"
        )

    complete = (
        dedicated_ids
        | anchor_ids
    )

    if (
        complete
        != ALL_EXPECTED_CASE_IDS
    ):
        raise ValueError(
            "Unified Week 26 coverage must include exactly "
            "C001 through C012."
        )


def _baseline_final_governance_check(
    baseline: dict[str, Any],
) -> dict[str, Any]:
    """Confirm original baseline never missed final governance."""

    results = (
        _baseline_results(
            baseline
        )
    )

    mismatches = [
        result[
            "case_id"
        ]
        for result
        in results
        if not _final_decision_matches(
            result
        )
    ]

    return {
        "case_count": len(
            results
        ),
        "mismatch_case_ids": (
            mismatches
        ),
        "all_final_decisions_match": (
            not mismatches
        ),
    }


def _build_case_register(
    dedicated: dict[str, dict[str, Any]],
    anchors: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Build ordered C001-C012 case register."""

    combined = {
        **dedicated,
        **anchors,
    }

    register = []

    for case_id in sorted(
        ALL_EXPECTED_CASE_IDS
    ):
        entry = combined[
            case_id
        ]

        register.append(
            {
                "case_id": case_id,
                **entry,
            }
        )

    return register


def _summary(
    register: list[dict[str, Any]],
    baseline_governance: dict[str, Any],
) -> dict[str, Any]:
    """Build unified assurance summary."""

    matched = [
        item
        for item
        in register
        if item[
            "matched"
        ]
    ]

    mismatched = [
        item
        for item
        in register
        if not item[
            "matched"
        ]
    ]

    return {
        "case_count": len(
            register
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
                    register
                ),
                4,
            )
            if register
            else 0.0
        ),
        "dedicated_control_case_count": len(
            DEDICATED_CASE_IDS
        ),
        "regression_anchor_case_count": len(
            ANCHOR_CASE_IDS
        ),
        "mismatched_case_ids": [
            item[
                "case_id"
            ]
            for item
            in mismatched
        ],
        "baseline_final_governance_mismatch_case_ids": (
            baseline_governance[
                "mismatch_case_ids"
            ]
        ),
        "overall_status": (
            "PASS"
            if (
                not mismatched
                and baseline_governance[
                    "all_final_decisions_match"
                ]
            )
            else "FAIL"
        ),
    }


def _markdown_report(
    report: dict[str, Any],
) -> str:
    """Create human-readable Week 26 assurance report."""

    summary = report[
        "summary"
    ]

    lines = [
        "# Week 26 Automated Adversarial Assurance Report",
        "",
        f"Overall status: **{summary['overall_status']}**",
        "",
        "## Summary",
        "",
        f"- Benchmark cases: {summary['case_count']}",
        (
            "- Matched cases: "
            f"{summary['matched_case_count']}"
        ),
        (
            "- Mismatched cases: "
            f"{summary['mismatched_case_count']}"
        ),
        (
            "- Match rate: "
            f"{summary['match_rate']:.1%}"
        ),
        (
            "- Dedicated Week 26 control cases: "
            f"{summary['dedicated_control_case_count']}"
        ),
        (
            "- Regression-anchor cases: "
            f"{summary['regression_anchor_case_count']}"
        ),
        "",
        "## Architecture",
        "",
        (
            "Week 26 distinguishes detector-specific assurance "
            "states from final governance decisions."
        ),
        "",
        (
            "The original existing-stack baseline preserved the "
            "correct final governance outcome across all 12 cases. "
            "Week 26 adds more precise adversarial explanations "
            "without increasing answer authority."
        ),
        "",
        "## Case register",
        "",
        "| Case | Control | Result |",
        "|---|---|---|",
    ]

    for item in report[
        "case_register"
    ]:
        lines.append(
            "| "
            f"{item['case_id']} | "
            f"{item['control']} | "
            f"{'PASS' if item['matched'] else 'FAIL'} |"
        )

    lines.extend(
        [
            "",
            "## Safety invariants",
            "",
            (
                "- Dedicated assurance controls may reduce or "
                "block answer authority; they do not increase it."
            ),
            (
                "- Retrieved evidence is treated as content, "
                "not as a trusted control plane."
            ),
            (
                "- Historical or superseded evidence does not "
                "silently become current authority."
            ),
            (
                "- Abstention remains a governed safety state "
                "and cannot smuggle operational directives."
            ),
            (
                "- Detector labels are not treated as equivalent "
                "to governance decisions."
            ),
            "",
        ]
    )

    if summary[
        "mismatched_case_ids"
    ]:
        lines.append(
            "## Failures"
        )

        lines.append(
            ""
        )

        for case_id in summary[
            "mismatched_case_ids"
        ]:
            lines.append(
                f"- {case_id}"
            )

    else:
        lines.append(
            "## Failures"
        )

        lines.append(
            ""
        )

        lines.append(
            "None."
        )

    lines.append(
        ""
    )

    return "\n".join(
        lines
    )


def run_week26_assurance_suite() -> dict[str, Any]:
    """Run unified Week 26 adversarial assurance."""

    benchmark = _load_benchmark()

    baseline = _load_baseline()

    controls = (
        _run_dedicated_controls()
    )

    dedicated = (
        _dedicated_case_results(
            controls
        )
    )

    anchors = (
        _anchor_case_results(
            baseline
        )
    )

    _validate_case_coverage(
        dedicated,
        anchors,
    )

    baseline_governance = (
        _baseline_final_governance_check(
            baseline
        )
    )

    register = (
        _build_case_register(
            dedicated,
            anchors,
        )
    )

    summary = (
        _summary(
            register,
            baseline_governance,
        )
    )

    report = {
        "benchmark_name": benchmark[
            "benchmark_name"
        ],
        "benchmark_version": benchmark[
            "benchmark_version"
        ],
        "evaluation_type": (
            "week26_unified_adversarial_assurance"
        ),
        "summary": summary,
        "baseline_final_governance": (
            baseline_governance
        ),
        "case_register": (
            register
        ),
        "dedicated_control_reports": (
            controls
        ),
    }

    JSON_OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with JSON_OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )

    markdown = (
        _markdown_report(
            report
        )
    )

    with MARKDOWN_OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            markdown
        )

    return report


def _print_summary(
    report: dict[str, Any],
) -> None:
    """Print concise unified result."""

    summary = report[
        "summary"
    ]

    print(
        "Week 26 Automated Adversarial Assurance Suite"
    )

    print(
        "---------------------------------------------"
    )

    print(
        f"Overall status: {summary['overall_status']}"
    )

    print(
        f"Benchmark cases: {summary['case_count']}"
    )

    print(
        "Matched: "
        f"{summary['matched_case_count']}/"
        f"{summary['case_count']}"
    )

    print(
        "Dedicated control cases: "
        f"{summary['dedicated_control_case_count']}"
    )

    print(
        "Regression anchor cases: "
        f"{summary['regression_anchor_case_count']}"
    )

    print(
        "Final-governance mismatches in original baseline: "
        f"{summary['baseline_final_governance_mismatch_case_ids']}"
    )

    print(
        "Unified mismatched cases: "
        f"{summary['mismatched_case_ids']}"
    )

    print(
        f"JSON report: {JSON_OUTPUT_PATH}"
    )

    print(
        f"Markdown report: {MARKDOWN_OUTPUT_PATH}"
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
        run_week26_assurance_suite()
    )

    _print_summary(
        report
    )


if __name__ == "__main__":
    main()