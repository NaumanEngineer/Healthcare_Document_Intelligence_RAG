"""Week 25 Day 5 — consolidated automated assurance suite.

This module orchestrates the existing Week 25 benchmark validation,
Day 3 citation-faithfulness evaluation, and Day 4 groundedness /
hallucination-resistance evaluation.

It reuses the existing tested assurance components rather than
duplicating their logic.

Run with:

    python -m src.evaluation.run_week25_assurance_suite

Exit codes:

    0 = assurance suite PASS
    1 = assurance suite FAIL
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.evaluation.run_week25_benchmark_baseline import (
    _run_case as run_day3_case,
)
from src.evaluation.run_week25_benchmark_baseline import (
    _summarise as summarise_day3,
)
from src.evaluation.run_week25_day4_faithfulness_benchmark import (
    _run_case as run_day4_case,
)
from src.evaluation.run_week25_day4_faithfulness_benchmark import (
    _summarise as summarise_day4,
)
from src.evaluation.validate_week25_benchmark import (
    load_benchmark,
    validate_benchmark,
)


OUTPUT_DIRECTORY = Path(
    "outputs"
)

JSON_OUTPUT_PATH = (
    OUTPUT_DIRECTORY
    / "week25_automated_assurance_report.json"
)

MARKDOWN_OUTPUT_PATH = (
    OUTPUT_DIRECTORY
    / "week25_automated_assurance_report.md"
)

EXPECTED_CASE_COUNT = 18

SUITE_PASS = "PASS"
SUITE_FAIL = "FAIL"


def _require_mapping(
    value: Any,
    name: str,
) -> dict[str, Any]:
    """Require a dictionary-like result."""

    if not isinstance(
        value,
        dict,
    ):
        raise ValueError(
            f"{name} must be a mapping."
        )

    return value


def _require_list(
    value: Any,
    name: str,
) -> list[Any]:
    """Require a list result."""

    if not isinstance(
        value,
        list,
    ):
        raise ValueError(
            f"{name} must be a list."
        )

    return value


def _case_ids(
    results: list[dict[str, Any]],
) -> list[str]:
    """Return case IDs in evaluation order."""

    case_ids: list[str] = []

    for result in results:
        result = _require_mapping(
            result,
            "benchmark result",
        )

        case_id = result.get(
            "case_id"
        )

        if (
            not isinstance(
                case_id,
                str,
            )
            or not case_id.strip()
        ):
            raise ValueError(
                "Benchmark result contains "
                "an invalid case_id."
            )

        case_ids.append(
            case_id.strip()
        )

    return case_ids


def _validate_case_alignment(
    benchmark: dict[str, Any],
    day3_results: list[dict[str, Any]],
    day4_results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Ensure all assurance layers evaluated the same cases."""

    benchmark_cases = _require_list(
        benchmark.get(
            "cases"
        ),
        "benchmark cases",
    )

    benchmark_case_ids: list[str] = []

    for case in benchmark_cases:
        case = _require_mapping(
            case,
            "benchmark case",
        )

        case_id = case.get(
            "case_id"
        )

        if (
            not isinstance(
                case_id,
                str,
            )
            or not case_id.strip()
        ):
            raise ValueError(
                "Benchmark contains an invalid case_id."
            )

        benchmark_case_ids.append(
            case_id.strip()
        )

    day3_case_ids = _case_ids(
        day3_results
    )

    day4_case_ids = _case_ids(
        day4_results
    )

    benchmark_unique = (
        len(
            benchmark_case_ids
        )
        == len(
            set(
                benchmark_case_ids
            )
        )
    )

    day3_unique = (
        len(
            day3_case_ids
        )
        == len(
            set(
                day3_case_ids
            )
        )
    )

    day4_unique = (
        len(
            day4_case_ids
        )
        == len(
            set(
                day4_case_ids
            )
        )
    )

    same_order = (
        benchmark_case_ids
        == day3_case_ids
        == day4_case_ids
    )

    same_case_set = (
        set(
            benchmark_case_ids
        )
        == set(
            day3_case_ids
        )
        == set(
            day4_case_ids
        )
    )

    passed = (
        benchmark_unique
        and day3_unique
        and day4_unique
        and same_order
        and same_case_set
    )

    return {
        "status": (
            SUITE_PASS
            if passed
            else SUITE_FAIL
        ),
        "benchmark_case_ids": (
            benchmark_case_ids
        ),
        "day3_case_ids": (
            day3_case_ids
        ),
        "day4_case_ids": (
            day4_case_ids
        ),
        "benchmark_case_ids_unique": (
            benchmark_unique
        ),
        "day3_case_ids_unique": (
            day3_unique
        ),
        "day4_case_ids_unique": (
            day4_unique
        ),
        "same_case_set": (
            same_case_set
        ),
        "same_case_order": (
            same_order
        ),
    }


def _run_day3(
    benchmark: dict[str, Any],
) -> dict[str, Any]:
    """Run the existing Day 3 hardened benchmark."""

    cases = _require_list(
        benchmark.get(
            "cases"
        ),
        "benchmark cases",
    )

    results = [
        run_day3_case(
            _require_mapping(
                case,
                "benchmark case",
            )
        )
        for case in cases
    ]

    summary = summarise_day3(
        results
    )

    return {
        "evaluation_type": (
            "week25_day3_hardened_baseline"
        ),
        "summary": summary,
        "results": results,
    }


def _run_day4(
    benchmark: dict[str, Any],
) -> dict[str, Any]:
    """Run the existing Day 4 integrated benchmark."""

    cases = _require_list(
        benchmark.get(
            "cases"
        ),
        "benchmark cases",
    )

    results = [
        run_day4_case(
            _require_mapping(
                case,
                "benchmark case",
            )
        )
        for case in cases
    ]

    summary = summarise_day4(
        results
    )

    return {
        "evaluation_type": (
            "week25_day4_integrated_faithfulness"
        ),
        "summary": summary,
        "results": results,
    }


def _summary_is_perfect(
    summary: dict[str, Any],
) -> bool:
    """Return True only for a complete zero-mismatch run."""

    summary = _require_mapping(
        summary,
        "evaluation summary",
    )

    return (
        summary.get(
            "case_count"
        )
        == EXPECTED_CASE_COUNT
        and summary.get(
            "matched_case_count"
        )
        == EXPECTED_CASE_COUNT
        and summary.get(
            "mismatched_case_count"
        )
        == 0
        and summary.get(
            "match_rate"
        )
        == 1.0
        and summary.get(
            "mismatched_case_ids"
        )
        == []
    )


def _derive_suite_failures(
    *,
    validation_succeeded: bool,
    benchmark: dict[str, Any],
    day3: dict[str, Any],
    day4: dict[str, Any],
    alignment: dict[str, Any],
) -> list[str]:
    """Return fail-closed reasons for the consolidated suite."""

    failures: list[str] = []

    if not validation_succeeded:
        failures.append(
            "Authoritative benchmark validation failed."
        )

    cases = benchmark.get(
        "cases"
    )

    if (
        not isinstance(
            cases,
            list,
        )
        or len(
            cases
        )
        != EXPECTED_CASE_COUNT
    ):
        failures.append(
            "Authoritative benchmark does not contain "
            f"exactly {EXPECTED_CASE_COUNT} cases."
        )

    day3_summary = _require_mapping(
        day3.get(
            "summary"
        ),
        "Day 3 summary",
    )

    day4_summary = _require_mapping(
        day4.get(
            "summary"
        ),
        "Day 4 summary",
    )

    if not _summary_is_perfect(
        day3_summary
    ):
        failures.append(
            "Day 3 citation-faithfulness benchmark "
            "did not achieve a complete match."
        )

    if not _summary_is_perfect(
        day4_summary
    ):
        failures.append(
            "Day 4 integrated faithfulness benchmark "
            "did not achieve a complete match."
        )

    if alignment.get(
        "status"
    ) != SUITE_PASS:
        failures.append(
            "Benchmark case alignment differs across "
            "assurance layers."
        )

    return failures


def _build_control_coverage(
    day3: dict[str, Any],
    day4: dict[str, Any],
) -> dict[str, Any]:
    """Build consolidated assurance-control metrics."""

    day3_summary = _require_mapping(
        day3.get(
            "summary"
        ),
        "Day 3 summary",
    )

    day4_summary = _require_mapping(
        day4.get(
            "summary"
        ),
        "Day 4 summary",
    )

    return {
        "citation_faithfulness": {
            "case_count": (
                day3_summary.get(
                    "case_count"
                )
            ),
            "matched_case_count": (
                day3_summary.get(
                    "matched_case_count"
                )
            ),
            "mismatched_case_count": (
                day3_summary.get(
                    "mismatched_case_count"
                )
            ),
            "match_rate": (
                day3_summary.get(
                    "match_rate"
                )
            ),
            "multi_source_case_count": (
                day3_summary.get(
                    "multi_source_case_count"
                )
            ),
        },
        "groundedness_and_hallucination": {
            "case_count": (
                day4_summary.get(
                    "case_count"
                )
            ),
            "matched_case_count": (
                day4_summary.get(
                    "matched_case_count"
                )
            ),
            "mismatched_case_count": (
                day4_summary.get(
                    "mismatched_case_count"
                )
            ),
            "match_rate": (
                day4_summary.get(
                    "match_rate"
                )
            ),
            "hallucination_risk_cases": (
                day4_summary.get(
                    "hallucination_risk_cases"
                )
            ),
            "overstatement_cases": (
                day4_summary.get(
                    "overstatement_cases"
                )
            ),
            "review_authority_increase_cases": (
                day4_summary.get(
                    "review_authority_increase_cases"
                )
            ),
            "abstention_violation_cases": (
                day4_summary.get(
                    "abstention_violation_cases"
                )
            ),
            "conflict_ignored_cases": (
                day4_summary.get(
                    "conflict_ignored_cases"
                )
            ),
        },
    }


def _build_benchmark_profile(
    validation_result: dict[str, Any],
) -> dict[str, Any]:
    """Expose authoritative benchmark composition."""

    return {
        "case_count": (
            validation_result.get(
                "case_count"
            )
        ),
        "governance_counts": (
            validation_result.get(
                "governance_counts",
                {}
            )
        ),
        "verification_counts": (
            validation_result.get(
                "verification_counts",
                {}
            )
        ),
        "overall_status_counts": (
            validation_result.get(
                "overall_status_counts",
                {}
            )
        ),
        "human_review_count": (
            validation_result.get(
                "human_review_count"
            )
        ),
        "validation_status": (
            validation_result.get(
                "validation_status"
            )
        ),
    }


def _build_adversarial_case_register(
    day4: dict[str, Any],
) -> dict[str, list[str]]:
    """Return case IDs that activated each safety detector."""

    results = _require_list(
        day4.get(
            "results"
        ),
        "Day 4 results",
    )

    register = {
        "hallucination_risk": [],
        "overstatement": [],
        "review_authority_increase": [],
        "abstention_violation": [],
        "conflict_ignored": [],
    }

    for result in results:
        result = _require_mapping(
            result,
            "Day 4 result",
        )

        case_id = result.get(
            "case_id"
        )

        if (
            not isinstance(
                case_id,
                str,
            )
            or not case_id.strip()
        ):
            raise ValueError(
                "Day 4 result contains invalid case_id."
            )

        case_id = case_id.strip()

        hallucination_count = result.get(
            "hallucination_risk_count",
            0,
        )

        overstatement_count = result.get(
            "overstatement_count",
            0,
        )

        if (
            isinstance(
                hallucination_count,
                int,
            )
            and hallucination_count > 0
        ):
            register[
                "hallucination_risk"
            ].append(
                case_id
            )

        if (
            isinstance(
                overstatement_count,
                int,
            )
            and overstatement_count > 0
        ):
            register[
                "overstatement"
            ].append(
                case_id
            )

        if result.get(
            "review_authority_increase_detected"
        ) is True:
            register[
                "review_authority_increase"
            ].append(
                case_id
            )

        if result.get(
            "abstention_violation_detected"
        ) is True:
            register[
                "abstention_violation"
            ].append(
                case_id
            )

        if result.get(
            "conflict_ignored_detected"
        ) is True:
            register[
                "conflict_ignored"
            ].append(
                case_id
            )

    return register


def _build_report(
    *,
    benchmark: dict[str, Any],
    validation_result: dict[str, Any],
    day3: dict[str, Any],
    day4: dict[str, Any],
    alignment: dict[str, Any],
    failures: list[str],
) -> dict[str, Any]:
    """Build the machine-readable consolidated report."""

    overall_status = (
        SUITE_PASS
        if not failures
        else SUITE_FAIL
    )

    adversarial_register = (
        _build_adversarial_case_register(
            day4
        )
    )

    return {
        "report_name": (
            "Week 25 Automated Assurance Report"
        ),
        "report_version": "1.1",
        "generated_at_utc": (
            datetime.now(
                timezone.utc
            )
            .isoformat()
        ),
        "overall_status": (
            overall_status
        ),
        "benchmark": {
            "benchmark_name": (
                benchmark.get(
                    "benchmark_name"
                )
            ),
            "benchmark_version": (
                benchmark.get(
                    "benchmark_version"
                )
            ),
            "expected_case_count": (
                EXPECTED_CASE_COUNT
            ),
            "actual_case_count": len(
                benchmark.get(
                    "cases",
                    [],
                )
            ),
        },
        "benchmark_validation": {
            "status": SUITE_PASS,
            "result": (
                validation_result
            ),
        },
        "benchmark_profile": (
            _build_benchmark_profile(
                validation_result
            )
        ),
        "case_alignment": (
            alignment
        ),
        "control_coverage": (
            _build_control_coverage(
                day3,
                day4,
            )
        ),
        "adversarial_case_register": (
            adversarial_register
        ),
        "day3_citation_assurance": (
            day3
        ),
        "day4_faithfulness_assurance": (
            day4
        ),
        "failure_count": len(
            failures
        ),
        "failure_reasons": (
            failures
        ),
        "interpretation": {
            "detector_counts_mean": (
                "Deliberately adversarial benchmark cases "
                "were detected by the assurance controls."
            ),
            "detector_counts_do_not_mean": (
                "Unsafe outputs escaped the assurance layer."
            ),
            "zero_mismatches_required_for_pass": True,
        },
        "safety_properties": {
            "benchmark_weakened": False,
            "external_knowledge_used": False,
            "additional_conservative_detections_allowed": True,
            "governance_authority_may_be_increased": False,
        },
    }


def _write_json_report(
    report: dict[str, Any],
) -> None:
    """Write the machine-readable assurance report."""

    OUTPUT_DIRECTORY.mkdir(
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


def _markdown_percentage(
    value: Any,
) -> str:
    """Format a decimal match rate for Markdown."""

    if isinstance(
        value,
        (int, float),
    ):
        return f"{value:.1%}"

    return "N/A"


def _format_case_ids(
    case_ids: list[str],
) -> str:
    """Format detector case IDs for Markdown."""

    if not case_ids:
        return "None"

    return ", ".join(
        f"`{case_id}`"
        for case_id in case_ids
    )


def _write_markdown_report(
    report: dict[str, Any],
) -> None:
    """Write the human-readable assurance report."""

    coverage = _require_mapping(
        report.get(
            "control_coverage"
        ),
        "control coverage",
    )

    citation = _require_mapping(
        coverage.get(
            "citation_faithfulness"
        ),
        "citation coverage",
    )

    faithfulness = _require_mapping(
        coverage.get(
            "groundedness_and_hallucination"
        ),
        "faithfulness coverage",
    )

    benchmark_profile = _require_mapping(
        report.get(
            "benchmark_profile"
        ),
        "benchmark profile",
    )

    governance_counts = _require_mapping(
        benchmark_profile.get(
            "governance_counts"
        ),
        "governance counts",
    )

    status_counts = _require_mapping(
        benchmark_profile.get(
            "overall_status_counts"
        ),
        "overall status counts",
    )

    register = _require_mapping(
        report.get(
            "adversarial_case_register"
        ),
        "adversarial case register",
    )

    failures = _require_list(
        report.get(
            "failure_reasons"
        ),
        "failure reasons",
    )

    failure_section = (
        "- None"
        if not failures
        else "\n".join(
            f"- {failure}"
            for failure in failures
        )
    )

    markdown = f"""# Week 25 Automated Assurance Report

## Overall Status

**{report['overall_status']}**

The assurance suite completed against the authoritative Week 25 benchmark.

A PASS means that every required benchmark expectation matched and no required safety signal was missed.

---

## Benchmark Profile

| Measure | Result |
| --- | ---: |
| Expected cases | {report['benchmark']['expected_case_count']} |
| Evaluated cases | {report['benchmark']['actual_case_count']} |
| AUTO_ANSWER cases | {governance_counts.get('AUTO_ANSWER', 0)} |
| REVIEW_REQUIRED cases | {governance_counts.get('REVIEW_REQUIRED', 0)} |
| ABSTAIN cases | {governance_counts.get('ABSTAIN', 0)} |
| Expected PASS cases | {status_counts.get('PASS', 0)} |
| Expected FAIL cases | {status_counts.get('FAIL', 0)} |
| Expected PASS_WITH_WARNINGS cases | {status_counts.get('PASS_WITH_WARNINGS', 0)} |
| Human-review cases | {benchmark_profile.get('human_review_count')} |
| Benchmark validation | {benchmark_profile.get('validation_status')} |
| Cross-layer case alignment | {report['case_alignment']['status']} |

The benchmark deliberately includes unsafe, unsupported, conflicting, overstated, and abstention-violation scenarios. Expected FAIL cases are therefore adversarial tests, not production failures.

---

## Citation & Multi-Source Assurance

| Measure | Result |
| --- | ---: |
| Cases | {citation.get('case_count')} |
| Matched | {citation.get('matched_case_count')} |
| Mismatched | {citation.get('mismatched_case_count')} |
| Match rate | {_markdown_percentage(citation.get('match_rate'))} |
| Multi-source cases evaluated | {citation.get('multi_source_case_count')} |

---

## Groundedness & Hallucination Resistance

| Safety control | Detected cases |
| --- | ---: |
| Hallucination risk | {faithfulness.get('hallucination_risk_cases')} |
| Overstatement | {faithfulness.get('overstatement_cases')} |
| Review-authority increase | {faithfulness.get('review_authority_increase_cases')} |
| Abstention violation | {faithfulness.get('abstention_violation_cases')} |
| Ignored conflict | {faithfulness.get('conflict_ignored_cases')} |

Day 4 benchmark match rate: **{_markdown_percentage(faithfulness.get('match_rate'))}**

### Interpretation

These detector counts do **not** mean unsafe outputs escaped the system.

They mean the deliberately adversarial benchmark cases activated the expected safety controls.

The suite still achieved:

- {faithfulness.get('matched_case_count')}/{faithfulness.get('case_count')} matched cases;
- {faithfulness.get('mismatched_case_count')} mismatches;
- {_markdown_percentage(faithfulness.get('match_rate'))} match rate.

---

## Adversarial Case Register

| Detector | Case IDs |
| --- | --- |
| Hallucination risk | {_format_case_ids(register.get('hallucination_risk', []))} |
| Overstatement | {_format_case_ids(register.get('overstatement', []))} |
| Review-authority increase | {_format_case_ids(register.get('review_authority_increase', []))} |
| Abstention violation | {_format_case_ids(register.get('abstention_violation', []))} |
| Ignored conflict | {_format_case_ids(register.get('conflict_ignored', []))} |

This register makes the safety evidence auditable by showing exactly which benchmark cases activated each detector.

---

## Failure Reasons

{failure_section}

---

## Safety Interpretation

A PASS requires:

- successful validation of the authoritative benchmark;
- evaluation of all expected benchmark cases;
- complete Day 3 citation-faithfulness matching;
- complete Day 4 groundedness and hallucination-resistance matching;
- identical case alignment across assurance layers;
- no missed required safety signal.

Additional conservative detector signals are permitted when they do not increase answer authority.

The benchmark is not weakened to improve the score.

---

## Governance Properties

The assurance layer may reduce authority but must never increase it.

Examples:

- AUTO_ANSWER may be restricted to review;
- REVIEW_REQUIRED may not become authoritative;
- ABSTAIN may not become substantive advice.

External knowledge is not used to justify unsupported benchmark claims.

---

## Governance Principle

> The model is optional. The assurance path is not.

Generated automatically by:

`python -m src.evaluation.run_week25_assurance_suite`
"""

    with MARKDOWN_OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            markdown
        )


def run_assurance_suite() -> dict[str, Any]:
    """Execute the consolidated Week 25 assurance workflow."""

    benchmark = load_benchmark()

    validation_result = validate_benchmark(
        benchmark
    )

    validation_result = _require_mapping(
        validation_result,
        "benchmark validation result",
    )

    day3 = _run_day3(
        benchmark
    )

    day4 = _run_day4(
        benchmark
    )

    day3_results = _require_list(
        day3.get(
            "results"
        ),
        "Day 3 results",
    )

    day4_results = _require_list(
        day4.get(
            "results"
        ),
        "Day 4 results",
    )

    alignment = _validate_case_alignment(
        benchmark,
        day3_results,
        day4_results,
    )

    failures = _derive_suite_failures(
        validation_succeeded=True,
        benchmark=benchmark,
        day3=day3,
        day4=day4,
        alignment=alignment,
    )

    report = _build_report(
        benchmark=benchmark,
        validation_result=validation_result,
        day3=day3,
        day4=day4,
        alignment=alignment,
        failures=failures,
    )

    _write_json_report(
        report
    )

    _write_markdown_report(
        report
    )

    return report


def _print_summary(
    report: dict[str, Any],
) -> None:
    """Print concise CLI assurance evidence."""

    coverage = report[
        "control_coverage"
    ]

    day3 = coverage[
        "citation_faithfulness"
    ]

    day4 = coverage[
        "groundedness_and_hallucination"
    ]

    print(
        "Week 25 Automated Assurance Suite"
    )

    print(
        "---------------------------------"
    )

    print(
        f"Overall status: "
        f"{report['overall_status']}"
    )

    print(
        "Benchmark cases: "
        f"{report['benchmark']['actual_case_count']}"
    )

    print(
        "Day 3 citation assurance: "
        f"{day3['matched_case_count']}/"
        f"{day3['case_count']} matched"
    )

    print(
        "Day 4 faithfulness assurance: "
        f"{day4['matched_case_count']}/"
        f"{day4['case_count']} matched"
    )

    print(
        "Hallucination-risk detections: "
        f"{day4['hallucination_risk_cases']}"
    )

    print(
        "Overstatement detections: "
        f"{day4['overstatement_cases']}"
    )

    print(
        "Review-authority increases detected: "
        f"{day4['review_authority_increase_cases']}"
    )

    print(
        "Abstention violations detected: "
        f"{day4['abstention_violation_cases']}"
    )

    print(
        "Ignored conflicts detected: "
        f"{day4['conflict_ignored_cases']}"
    )

    print(
        f"JSON report: "
        f"{JSON_OUTPUT_PATH}"
    )

    print(
        f"Markdown report: "
        f"{MARKDOWN_OUTPUT_PATH}"
    )

    if report[
        "failure_reasons"
    ]:
        print(
            "Failures:"
        )

        for failure in report[
            "failure_reasons"
        ]:
            print(
                f"  - {failure}"
            )

    else:
        print(
            "Failures: none"
        )


def main() -> None:
    """CLI entry point with fail-closed exit behaviour."""

    try:
        report = run_assurance_suite()

    except Exception as exc:
        print(
            "Week 25 Automated Assurance Suite"
        )

        print(
            "---------------------------------"
        )

        print(
            "Overall status: FAIL"
        )

        print(
            "Assurance runner failed safely:"
        )

        print(
            f"  {type(exc).__name__}: {exc}"
        )

        raise SystemExit(
            1
        ) from exc

    _print_summary(
        report
    )

    if report[
        "overall_status"
    ] != SUITE_PASS:
        raise SystemExit(
            1
        )


if __name__ == "__main__":
    main()