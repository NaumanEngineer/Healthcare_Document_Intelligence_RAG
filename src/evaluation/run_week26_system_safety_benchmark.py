"""Week 26 end-to-end system safety benchmark.

This runner applies cross-layer safety invariants to all 12 Week 26
adversarial benchmark cases.

It does not introduce new content detectors.

Instead, it verifies that the system-level combination of:

- upstream governance;
- final assurance decision;
- adversarial safety signals;

never increases answer authority or allows an unsafe case to PASS.

Important vocabulary boundary:

Benchmark upstream governance uses:

    AUTO_ANSWER
    REVIEW_REQUIRED
    ABSTAIN

The system-safety authority lattice uses:

    PASS
    REVIEW_REQUIRED
    ABSTAIN

Therefore AUTO_ANSWER is normalised to PASS only for authority
comparison. The original governance state is preserved in the report.

Run with:

    python -m src.evaluation.run_week26_system_safety_benchmark
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


from src.evaluation.week26_system_safety_invariants import (
    ABSTAIN,
    PASS,
    REVIEW_REQUIRED,
    audit_case_collection,
)
from src.evaluation.validate_week26_benchmark import (
    BENCHMARK_PATH,
    validate_benchmark,
)


OUTPUT_PATH = (
    ROOT
    / "outputs"
    / "week26_system_safety_benchmark.json"
)


UPSTREAM_GOVERNANCE_TO_AUTHORITY = {
    "AUTO_ANSWER": PASS,
    "REVIEW_REQUIRED": REVIEW_REQUIRED,
    "ABSTAIN": ABSTAIN,
}


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


def _normalise_upstream_governance(
    decision: str,
) -> str:
    """Map benchmark governance into the authority lattice.

    AUTO_ANSWER is equivalent to the maximum permitted answer-authority
    state before downstream assurance is applied.

    This mapping does not change the benchmark record itself.
    """

    if decision not in UPSTREAM_GOVERNANCE_TO_AUTHORITY:
        raise ValueError(
            "Unknown Week 26 upstream governance decision: "
            f"{decision}"
        )

    return UPSTREAM_GOVERNANCE_TO_AUTHORITY[
        decision
    ]


def _claim_map(
    case: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Index expected claim results by claim_id."""

    return {
        claim[
            "claim_id"
        ]: claim
        for claim
        in case.get(
            "expected_claim_results",
            []
        )
    }


def _has_unsupported_high_risk_claim(
    case: dict[str, Any],
) -> bool:
    """Detect benchmark-declared unsupported high-risk claims."""

    for claim in _claim_map(
        case
    ).values():
        status = claim.get(
            "expected_support_status"
        )

        authority = bool(
            claim.get(
                "expected_authority_increase_detected",
                False,
            )
        )

        role = bool(
            claim.get(
                "expected_role_hallucination_detected",
                False,
            )
        )

        if (
            status
            in {
                "UNSUPPORTED",
                "CITATION_MISMATCH",
            }
            and (
                authority
                or role
            )
        ):
            return True

    return False


def _signals_for_case(
    case: dict[str, Any],
) -> dict[str, Any]:
    """Map benchmark expectations into system-level safety signals."""

    groundedness = case.get(
        "expected_groundedness_decision"
    )

    temporal = case.get(
        "expected_temporal_result"
    )

    prompt_injection = case.get(
        "expected_prompt_injection_decision"
    )

    abstention = case.get(
        "expected_abstention_decision"
    )

    claim_results = case.get(
        "expected_claim_results",
        []
    )

    return {
        "prompt_injection_detected": (
            prompt_injection
            not in {
                None,
                "NO_INJECTION_DETECTED",
                "NOT_APPLICABLE",
            }
        ),
        "conflict_blocked": (
            groundedness
            == "CONFLICT_BLOCKED"
            or case.get(
                "expected_precedence_decision"
            )
            == "BLOCK_COMBINATION"
        ),
        "unsafe_temporal_evidence": (
            temporal
            in {
                "TEMPORALLY_EXPIRED",
                "FUTURE_EFFECTIVE",
                "TEMPORALLY_UNKNOWN",
            }
        ),
        "unsupported_high_risk_claim": (
            _has_unsupported_high_risk_claim(
                case
            )
        ),
        "authority_increase_detected": any(
            bool(
                claim.get(
                    "expected_authority_increase_detected",
                    False,
                )
            )
            for claim
            in claim_results
        ),
        "role_hallucination_detected": any(
            bool(
                claim.get(
                    "expected_role_hallucination_detected",
                    False,
                )
            )
            for claim
            in claim_results
        ),
        "abstention_violation_detected": (
            abstention
            not in {
                None,
                "SAFE_ABSTENTION",
                "NOT_APPLICABLE",
            }
        ),
    }


def _case_records(
    benchmark: dict[str, Any],
) -> tuple[
    list[dict[str, Any]],
    dict[str, str],
]:
    """Build invariant-audit records.

    Returns:

    1. Normalised invariant input records.
    2. Original upstream-governance lookup for reporting.
    """

    records = []

    original_governance = {}

    for case in benchmark[
        "cases"
    ]:
        case_id = case[
            "case_id"
        ]

        raw_upstream = case[
            "expected_governance_decision"
        ]

        normalised_upstream = (
            _normalise_upstream_governance(
                raw_upstream
            )
        )

        original_governance[
            case_id
        ] = raw_upstream

        records.append(
            {
                "case_id": case_id,
                "upstream_decision": (
                    normalised_upstream
                ),
                "final_decision": case[
                    "expected_final_assurance_decision"
                ],
                "signals": (
                    _signals_for_case(
                        case
                    )
                ),
            }
        )

    return (
        records,
        original_governance,
    )


def _enrich_results(
    results: list[dict[str, Any]],
    original_governance: dict[str, str],
) -> list[dict[str, Any]]:
    """Preserve original benchmark governance alongside normalised state."""

    enriched = []

    for result in results:
        case_id = result[
            "case_id"
        ]

        enriched.append(
            {
                **result,
                "original_upstream_governance_decision": (
                    original_governance[
                        case_id
                    ]
                ),
                "normalised_upstream_authority_decision": (
                    result[
                        "upstream_decision"
                    ]
                ),
            }
        )

    return enriched


def run_system_safety_benchmark() -> dict[str, Any]:
    """Run all 12 cases through system safety invariants."""

    benchmark = _load_benchmark()

    (
        records,
        original_governance,
    ) = _case_records(
        benchmark
    )

    audit = audit_case_collection(
        records
    )

    enriched_results = (
        _enrich_results(
            audit[
                "results"
            ],
            original_governance,
        )
    )

    report = {
        "benchmark_name": (
            "Week 26 End-to-End System Safety Benchmark"
        ),
        "benchmark_version": "1.0",
        "source_benchmark": benchmark[
            "benchmark_name"
        ],
        "evaluation_type": (
            "week26_cross_layer_system_safety"
        ),
        "governance_normalisation": {
            "AUTO_ANSWER": "PASS",
            "REVIEW_REQUIRED": "REVIEW_REQUIRED",
            "ABSTAIN": "ABSTAIN",
        },
        "summary": {
            "case_count": audit[
                "case_count"
            ],
            "passed_case_count": audit[
                "passed_case_count"
            ],
            "failed_case_count": audit[
                "failed_case_count"
            ],
            "failed_case_ids": audit[
                "failed_case_ids"
            ],
            "overall_status": audit[
                "overall_status"
            ],
        },
        "results": (
            enriched_results
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
    """Print concise system-safety result."""

    summary = report[
        "summary"
    ]

    print(
        "Week 26 End-to-End System Safety Benchmark"
    )

    print(
        "------------------------------------------"
    )

    print(
        f"Overall status: {summary['overall_status']}"
    )

    print(
        f"Cases: {summary['case_count']}"
    )

    print(
        "Passed: "
        f"{summary['passed_case_count']}/"
        f"{summary['case_count']}"
    )

    print(
        f"Failed: {summary['failed_case_count']}"
    )

    print(
        "Failed cases: "
        f"{summary['failed_case_ids']}"
    )

    print(
        "Governance normalisation: "
        "AUTO_ANSWER -> PASS"
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
        run_system_safety_benchmark()
    )

    _print_summary(
        report
    )


if __name__ == "__main__":
    main()