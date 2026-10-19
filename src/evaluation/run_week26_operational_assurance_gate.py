"""Unified Week 26 operational assurance gate.

This runner combines:

1. Week 26 adversarial assurance
2. Week 26 system-safety benchmark
3. Week 26 failure-injection robustness benchmark

The gate passes only when all three layers pass.

Core principle:

    A healthcare RAG system is not ready merely because individual
    detectors work.

    It must also preserve system-level safety and fail closed when
    assurance inputs themselves are malformed.

Run with:

    python -m src.evaluation.run_week26_operational_assurance_gate
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


from src.evaluation.run_week26_assurance_suite import (
    run_week26_assurance_suite,
)
from src.evaluation.run_week26_failure_injection_benchmark import (
    run_failure_injection_benchmark,
)
from src.evaluation.run_week26_system_safety_benchmark import (
    run_system_safety_benchmark,
)


JSON_OUTPUT_PATH = (
    ROOT
    / "outputs"
    / "week26_operational_assurance_gate.json"
)


MARKDOWN_OUTPUT_PATH = (
    ROOT
    / "outputs"
    / "week26_operational_assurance_gate.md"
)


def _adversarial_summary(
    report: dict[str, Any],
) -> dict[str, Any]:
    """Extract Week 26 adversarial assurance summary."""

    summary = report[
        "summary"
    ]

    return {
        "status": summary[
            "overall_status"
        ],
        "case_count": summary[
            "case_count"
        ],
        "matched_case_count": summary[
            "matched_case_count"
        ],
        "mismatched_case_count": summary[
            "mismatched_case_count"
        ],
        "mismatched_case_ids": summary[
            "mismatched_case_ids"
        ],
    }


def _system_safety_summary(
    report: dict[str, Any],
) -> dict[str, Any]:
    """Extract cross-layer system-safety summary."""

    summary = report[
        "summary"
    ]

    return {
        "status": summary[
            "overall_status"
        ],
        "case_count": summary[
            "case_count"
        ],
        "passed_case_count": summary[
            "passed_case_count"
        ],
        "failed_case_count": summary[
            "failed_case_count"
        ],
        "failed_case_ids": summary[
            "failed_case_ids"
        ],
    }


def _failure_injection_summary(
    report: dict[str, Any],
) -> dict[str, Any]:
    """Extract fail-closed robustness summary."""

    summary = report[
        "summary"
    ]

    return {
        "status": summary[
            "overall_status"
        ],
        "case_count": summary[
            "case_count"
        ],
        "matched_case_count": summary[
            "matched_case_count"
        ],
        "mismatched_case_count": summary[
            "mismatched_case_count"
        ],
        "fail_closed_case_count": summary[
            "fail_closed_case_count"
        ],
        "unsafe_pass_case_ids": summary[
            "unsafe_pass_case_ids"
        ],
        "mismatched_case_ids": summary[
            "mismatched_case_ids"
        ],
    }


def _gate_checks(
    *,
    adversarial: dict[str, Any],
    system_safety: dict[str, Any],
    failure_injection: dict[str, Any],
) -> dict[str, bool]:
    """Build final operational gate checks."""

    return {
        "adversarial_assurance_passes": (
            adversarial[
                "status"
            ]
            == "PASS"
        ),
        "system_safety_passes": (
            system_safety[
                "status"
            ]
            == "PASS"
        ),
        "failure_injection_passes": (
            failure_injection[
                "status"
            ]
            == "PASS"
        ),
        "adversarial_has_no_mismatches": (
            adversarial[
                "mismatched_case_count"
            ]
            == 0
        ),
        "system_safety_has_no_failures": (
            system_safety[
                "failed_case_count"
            ]
            == 0
        ),
        "failure_injection_has_no_unsafe_pass": (
            failure_injection[
                "unsafe_pass_case_ids"
            ]
            == []
        ),
        "failure_injection_has_no_mismatches": (
            failure_injection[
                "mismatched_case_count"
            ]
            == 0
        ),
    }


def _markdown_report(
    report: dict[str, Any],
) -> str:
    """Generate portfolio-readable operational assurance report."""

    gate = report[
        "gate"
    ]

    adversarial = report[
        "adversarial_assurance"
    ]

    system_safety = report[
        "system_safety"
    ]

    robustness = report[
        "failure_injection"
    ]

    lines = [
        "# Week 26 Operational Assurance Gate",
        "",
        f"Overall status: **{gate['overall_status']}**",
        "",
        "## Purpose",
        "",
        (
            "This gate combines adversarial assurance, cross-layer "
            "system safety, and fail-closed robustness."
        ),
        "",
        (
            "The system passes only when all assurance layers remain "
            "safe at the same time."
        ),
        "",
        "## Adversarial assurance",
        "",
        f"- Status: {adversarial['status']}",
        f"- Cases: {adversarial['case_count']}",
        (
            "- Matched: "
            f"{adversarial['matched_case_count']}/"
            f"{adversarial['case_count']}"
        ),
        (
            "- Mismatched cases: "
            f"{adversarial['mismatched_case_ids']}"
        ),
        "",
        "## Cross-layer system safety",
        "",
        f"- Status: {system_safety['status']}",
        f"- Cases: {system_safety['case_count']}",
        (
            "- Passed: "
            f"{system_safety['passed_case_count']}/"
            f"{system_safety['case_count']}"
        ),
        (
            "- Failed cases: "
            f"{system_safety['failed_case_ids']}"
        ),
        "",
        "## Fail-closed robustness",
        "",
        f"- Status: {robustness['status']}",
        f"- Cases: {robustness['case_count']}",
        (
            "- Matched: "
            f"{robustness['matched_case_count']}/"
            f"{robustness['case_count']}"
        ),
        (
            "- Fail-closed cases: "
            f"{robustness['fail_closed_case_count']}"
        ),
        (
            "- Unsafe PASS cases: "
            f"{robustness['unsafe_pass_case_ids']}"
        ),
        "",
        "## Gate checks",
        "",
    ]

    for name, passed in gate[
        "checks"
    ].items():
        lines.append(
            f"- {name}: {'PASS' if passed else 'FAIL'}"
        )

    lines.extend(
        [
            "",
            "## Safety conclusion",
            "",
            (
                "Week 26 demonstrates that the assurance architecture "
                "can detect adversarial evidence problems, preserve "
                "cross-layer authority constraints, and fail closed "
                "when assurance inputs themselves are malformed."
            ),
            "",
            (
                "Core invariant: the system may become more cautious, "
                "but must never become more authoritative because of "
                "uncertainty, malformed inputs, or adversarial content."
            ),
            "",
        ]
    )

    return "\n".join(
        lines
    )


def run_week26_operational_assurance_gate() -> dict[str, Any]:
    """Run the complete Week 26 operational assurance gate."""

    adversarial_report = (
        run_week26_assurance_suite()
    )

    system_safety_report = (
        run_system_safety_benchmark()
    )

    failure_injection_report = (
        run_failure_injection_benchmark()
    )

    adversarial = (
        _adversarial_summary(
            adversarial_report
        )
    )

    system_safety = (
        _system_safety_summary(
            system_safety_report
        )
    )

    failure_injection = (
        _failure_injection_summary(
            failure_injection_report
        )
    )

    checks = _gate_checks(
        adversarial=adversarial,
        system_safety=system_safety,
        failure_injection=failure_injection,
    )

    failed_checks = [
        name
        for name, passed
        in checks.items()
        if not passed
    ]

    overall_status = (
        "PASS"
        if not failed_checks
        else "FAIL"
    )

    report = {
        "report_name": (
            "Week 26 Operational Assurance Gate"
        ),
        "report_version": "1.0",
        "overall_status": (
            overall_status
        ),
        "adversarial_assurance": (
            adversarial
        ),
        "system_safety": (
            system_safety
        ),
        "failure_injection": (
            failure_injection
        ),
        "gate": {
            "overall_status": (
                overall_status
            ),
            "checks": (
                checks
            ),
            "failed_checks": (
                failed_checks
            ),
        },
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
    """Print concise Week 26 operational gate result."""

    gate = report[
        "gate"
    ]

    adversarial = report[
        "adversarial_assurance"
    ]

    system_safety = report[
        "system_safety"
    ]

    failure_injection = report[
        "failure_injection"
    ]

    print(
        "Week 26 Operational Assurance Gate"
    )

    print(
        "----------------------------------"
    )

    print(
        f"Overall status: {gate['overall_status']}"
    )

    print(
        "Adversarial assurance: "
        f"{adversarial['status']} "
        f"({adversarial['matched_case_count']}/"
        f"{adversarial['case_count']})"
    )

    print(
        "System safety: "
        f"{system_safety['status']} "
        f"({system_safety['passed_case_count']}/"
        f"{system_safety['case_count']})"
    )

    print(
        "Failure injection: "
        f"{failure_injection['status']} "
        f"({failure_injection['matched_case_count']}/"
        f"{failure_injection['case_count']})"
    )

    print(
        "Unsafe PASS cases: "
        f"{failure_injection['unsafe_pass_case_ids']}"
    )

    print(
        f"Failed gate checks: {gate['failed_checks']}"
    )

    print(
        f"JSON report: {JSON_OUTPUT_PATH}"
    )

    print(
        f"Markdown report: {MARKDOWN_OUTPUT_PATH}"
    )

    if gate[
        "overall_status"
    ] != "PASS":
        raise SystemExit(
            1
        )


def main() -> None:
    """CLI entry point."""

    report = (
        run_week26_operational_assurance_gate()
    )

    _print_summary(
        report
    )


if __name__ == "__main__":
    main()