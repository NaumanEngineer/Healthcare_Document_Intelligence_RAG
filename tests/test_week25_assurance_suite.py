"""Tests for the Week 25 consolidated assurance suite."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import src.evaluation.run_week25_assurance_suite as suite


def _perfect_summary() -> dict:
    """Return a perfect 18-case benchmark summary."""

    return {
        "case_count": 18,
        "matched_case_count": 18,
        "mismatched_case_count": 0,
        "match_rate": 1.0,
        "mismatched_case_ids": [],
    }


def _perfect_day3() -> dict:
    """Return a minimal perfect Day 3 result."""

    summary = _perfect_summary()

    summary[
        "multi_source_case_count"
    ] = 1

    results = [
        {
            "case_id": f"W25-C{i:03d}",
            "baseline_match": True,
        }
        for i in range(
            1,
            19,
        )
    ]

    return {
        "evaluation_type": (
            "week25_day3_hardened_baseline"
        ),
        "summary": summary,
        "results": results,
    }


def _perfect_day4() -> dict:
    """Return a minimal perfect Day 4 result."""

    summary = _perfect_summary()

    summary.update(
        {
            "hallucination_risk_cases": 11,
            "overstatement_cases": 11,
            "review_authority_increase_cases": 2,
            "abstention_violation_cases": 1,
            "conflict_ignored_cases": 1,
        }
    )

    results = []

    for i in range(
        1,
        19,
    ):
        results.append(
            {
                "case_id": (
                    f"W25-C{i:03d}"
                ),
                "benchmark_match": True,
                "hallucination_risk_count": (
                    1
                    if i >= 7
                    else 0
                ),
                "overstatement_count": (
                    1
                    if i >= 7
                    else 0
                ),
                "review_authority_increase_detected": (
                    i in {14, 15}
                ),
                "abstention_violation_detected": (
                    i == 17
                ),
                "conflict_ignored_detected": (
                    i == 13
                ),
            }
        )

    return {
        "evaluation_type": (
            "week25_day4_integrated_faithfulness"
        ),
        "summary": summary,
        "results": results,
    }


def _benchmark() -> dict:
    """Return a minimal 18-case benchmark."""

    return {
        "benchmark_name": (
            "Week 25 Citation and Faithfulness Benchmark"
        ),
        "benchmark_version": "1.0",
        "cases": [
            {
                "case_id": (
                    f"W25-C{i:03d}"
                )
            }
            for i in range(
                1,
                19,
            )
        ],
    }


def _validation_result() -> dict:
    """Return representative benchmark validation evidence."""

    return {
        "benchmark_name": (
            "Week 25 Citation and Faithfulness Benchmark"
        ),
        "case_count": 18,
        "governance_counts": {
            "ABSTAIN": 2,
            "AUTO_ANSWER": 10,
            "REVIEW_REQUIRED": 6,
        },
        "verification_counts": {
            "ABSTAIN": 1,
            "PASS": 4,
            "REVIEW_REQUIRED": 13,
        },
        "overall_status_counts": {
            "PASS_WITH_WARNINGS": 0,
            "FAIL": 12,
            "PASS": 6,
        },
        "human_review_count": 14,
        "validation_status": "PASS",
    }


def _alignment(
    status: str = suite.SUITE_PASS,
) -> dict:
    """Return representative cross-layer alignment."""

    case_ids = [
        f"W25-C{i:03d}"
        for i in range(
            1,
            19,
        )
    ]

    passed = (
        status
        == suite.SUITE_PASS
    )

    return {
        "status": status,
        "benchmark_case_ids": (
            case_ids
        ),
        "day3_case_ids": (
            case_ids
        ),
        "day4_case_ids": (
            case_ids
        ),
        "benchmark_case_ids_unique": (
            passed
        ),
        "day3_case_ids_unique": (
            passed
        ),
        "day4_case_ids_unique": (
            passed
        ),
        "same_case_set": (
            passed
        ),
        "same_case_order": (
            passed
        ),
    }


def _sample_report() -> dict:
    """Build a realistic report for output tests."""

    benchmark = _benchmark()
    day3 = _perfect_day3()
    day4 = _perfect_day4()
    validation = _validation_result()

    alignment = (
        suite._validate_case_alignment(
            benchmark,
            day3["results"],
            day4["results"],
        )
    )

    failures = (
        suite._derive_suite_failures(
            validation_succeeded=True,
            benchmark=benchmark,
            day3=day3,
            day4=day4,
            alignment=alignment,
        )
    )

    return suite._build_report(
        benchmark=benchmark,
        validation_result=validation,
        day3=day3,
        day4=day4,
        alignment=alignment,
        failures=failures,
    )


def test_perfect_18_case_suite_has_no_failures() -> None:
    """Perfect Day 3 and Day 4 results should pass."""

    benchmark = _benchmark()
    day3 = _perfect_day3()
    day4 = _perfect_day4()

    alignment = (
        suite._validate_case_alignment(
            benchmark,
            day3["results"],
            day4["results"],
        )
    )

    failures = (
        suite._derive_suite_failures(
            validation_succeeded=True,
            benchmark=benchmark,
            day3=day3,
            day4=day4,
            alignment=alignment,
        )
    )

    assert alignment[
        "status"
    ] == suite.SUITE_PASS

    assert failures == []


def test_wrong_benchmark_case_count_fails_closed() -> None:
    """A benchmark with fewer than 18 cases must fail."""

    benchmark = _benchmark()

    benchmark[
        "cases"
    ] = benchmark[
        "cases"
    ][:-1]

    failures = (
        suite._derive_suite_failures(
            validation_succeeded=True,
            benchmark=benchmark,
            day3=_perfect_day3(),
            day4=_perfect_day4(),
            alignment=_alignment(),
        )
    )

    assert any(
        "exactly 18 cases"
        in failure
        for failure in failures
    )


def test_day3_mismatch_fails_closed() -> None:
    """Any Day 3 mismatch must fail the suite."""

    day3 = _perfect_day3()

    day3[
        "summary"
    ][
        "matched_case_count"
    ] = 17

    day3[
        "summary"
    ][
        "mismatched_case_count"
    ] = 1

    day3[
        "summary"
    ][
        "match_rate"
    ] = 17 / 18

    day3[
        "summary"
    ][
        "mismatched_case_ids"
    ] = [
        "W25-C007"
    ]

    failures = (
        suite._derive_suite_failures(
            validation_succeeded=True,
            benchmark=_benchmark(),
            day3=day3,
            day4=_perfect_day4(),
            alignment=_alignment(),
        )
    )

    assert any(
        "Day 3"
        in failure
        for failure in failures
    )


def test_day4_mismatch_fails_closed() -> None:
    """Any Day 4 mismatch must fail the suite."""

    day4 = _perfect_day4()

    day4[
        "summary"
    ][
        "matched_case_count"
    ] = 17

    day4[
        "summary"
    ][
        "mismatched_case_count"
    ] = 1

    day4[
        "summary"
    ][
        "match_rate"
    ] = 17 / 18

    day4[
        "summary"
    ][
        "mismatched_case_ids"
    ] = [
        "W25-C017"
    ]

    failures = (
        suite._derive_suite_failures(
            validation_succeeded=True,
            benchmark=_benchmark(),
            day3=_perfect_day3(),
            day4=day4,
            alignment=_alignment(),
        )
    )

    assert any(
        "Day 4"
        in failure
        for failure in failures
    )


def test_case_order_mismatch_fails_alignment() -> None:
    """Cross-layer case order differences must fail alignment."""

    benchmark = _benchmark()
    day3 = _perfect_day3()
    day4 = _perfect_day4()

    day4[
        "results"
    ][0], day4[
        "results"
    ][1] = (
        day4[
            "results"
        ][1],
        day4[
            "results"
        ][0],
    )

    alignment = (
        suite._validate_case_alignment(
            benchmark,
            day3["results"],
            day4["results"],
        )
    )

    assert alignment[
        "same_case_set"
    ] is True

    assert alignment[
        "same_case_order"
    ] is False

    assert alignment[
        "status"
    ] == suite.SUITE_FAIL


def test_duplicate_case_ids_fail_alignment() -> None:
    """Duplicate benchmark IDs must fail cross-layer assurance."""

    benchmark = _benchmark()

    benchmark[
        "cases"
    ][1][
        "case_id"
    ] = "W25-C001"

    alignment = (
        suite._validate_case_alignment(
            benchmark,
            _perfect_day3()[
                "results"
            ],
            _perfect_day4()[
                "results"
            ],
        )
    )

    assert alignment[
        "benchmark_case_ids_unique"
    ] is False

    assert alignment[
        "status"
    ] == suite.SUITE_FAIL


def test_failed_benchmark_validation_fails_suite() -> None:
    """Benchmark validation failure must propagate."""

    failures = (
        suite._derive_suite_failures(
            validation_succeeded=False,
            benchmark=_benchmark(),
            day3=_perfect_day3(),
            day4=_perfect_day4(),
            alignment=_alignment(),
        )
    )

    assert (
        "Authoritative benchmark validation failed."
        in failures
    )


def test_adversarial_register_uses_count_fields() -> None:
    """Hallucination and overstatement use Day 4 count fields."""

    day4 = _perfect_day4()

    register = (
        suite._build_adversarial_case_register(
            day4
        )
    )

    assert (
        "W25-C007"
        in register[
            "hallucination_risk"
        ]
    )

    assert (
        "W25-C007"
        in register[
            "overstatement"
        ]
    )

    assert register[
        "review_authority_increase"
    ] == [
        "W25-C014",
        "W25-C015",
    ]

    assert register[
        "abstention_violation"
    ] == [
        "W25-C017"
    ]

    assert register[
        "conflict_ignored"
    ] == [
        "W25-C013"
    ]


def test_report_preserves_safety_properties() -> None:
    """Generated report must preserve governance safety claims."""

    report = _sample_report()

    assert report[
        "overall_status"
    ] == suite.SUITE_PASS

    assert report[
        "failure_count"
    ] == 0

    assert report[
        "safety_properties"
    ][
        "benchmark_weakened"
    ] is False

    assert report[
        "safety_properties"
    ][
        "external_knowledge_used"
    ] is False

    assert report[
        "safety_properties"
    ][
        "governance_authority_may_be_increased"
    ] is False

    assert report[
        "interpretation"
    ][
        "zero_mismatches_required_for_pass"
    ] is True


def test_json_report_is_written(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Machine-readable output must be written successfully."""

    output_path = (
        tmp_path
        / "assurance.json"
    )

    monkeypatch.setattr(
        suite,
        "JSON_OUTPUT_PATH",
        output_path,
    )

    report = _sample_report()

    suite._write_json_report(
        report
    )

    assert output_path.exists()

    loaded = json.loads(
        output_path.read_text(
            encoding="utf-8"
        )
    )

    assert loaded[
        "overall_status"
    ] == suite.SUITE_PASS

    assert loaded[
        "failure_count"
    ] == 0


def test_markdown_report_is_written(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Human-readable assurance report must be written."""

    output_path = (
        tmp_path
        / "assurance.md"
    )

    monkeypatch.setattr(
        suite,
        "MARKDOWN_OUTPUT_PATH",
        output_path,
    )

    report = _sample_report()

    suite._write_markdown_report(
        report
    )

    assert output_path.exists()

    content = output_path.read_text(
        encoding="utf-8"
    )

    assert (
        "# Week 25 Automated Assurance Report"
        in content
    )

    assert (
        "**PASS**"
        in content
    )

    assert (
        "Adversarial Case Register"
        in content
    )

    assert (
        "unsafe outputs escaped"
        in content
    )


def test_cli_exits_non_zero_when_suite_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CLI must return non-zero for an assurance failure."""

    failed_report = _sample_report()

    failed_report[
        "overall_status"
    ] = suite.SUITE_FAIL

    failed_report[
        "failure_count"
    ] = 1

    failed_report[
        "failure_reasons"
    ] = [
        "Synthetic assurance failure."
    ]

    monkeypatch.setattr(
        suite,
        "run_assurance_suite",
        lambda: failed_report,
    )

    with pytest.raises(
        SystemExit
    ) as exc_info:
        suite.main()

    assert (
        exc_info.value.code
        == 1
    )


def test_cli_exits_non_zero_on_internal_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unexpected runner errors must also fail closed."""

    def raise_error() -> dict:
        raise RuntimeError(
            "Synthetic runner failure."
        )

    monkeypatch.setattr(
        suite,
        "run_assurance_suite",
        raise_error,
    )

    with pytest.raises(
        SystemExit
    ) as exc_info:
        suite.main()

    assert (
        exc_info.value.code
        == 1
    )