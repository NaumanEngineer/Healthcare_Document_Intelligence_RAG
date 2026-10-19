"""Focused Week 26 semantic-precision benchmark.

This runner evaluates the three primary Week 26 semantic precision
cases identified by the existing-stack baseline:

    W26-C003 - Claim Segmentation Attack
    W26-C007 - Role Responsibility Hallucination
    W26-C008 - Subtle Modal Strengthening

Architecture:

    existing Week 25/26 baseline citation result
        ->
    Week 26 semantic precision audit
        ->
    revised support state

The semantic layer is forbidden from increasing support authority.

Run with:

    python -m src.evaluation.run_week26_semantic_precision_benchmark
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


from src.evaluation.run_week26_existing_stack_baseline import (
    _run_case as run_existing_stack_case,
)
from src.evaluation.semantic_precision_audit import (
    SUPPORT_ORDER,
    audit_semantic_precision,
)
from src.evaluation.validate_week26_benchmark import (
    BENCHMARK_PATH,
    validate_benchmark,
)


OUTPUT_PATH = (
    ROOT
    / "outputs"
    / "week26_semantic_precision_benchmark.json"
)


TARGET_CASE_IDS = (
    "W26-C003",
    "W26-C007",
    "W26-C008",
)


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


def _target_cases(
    benchmark: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return focused semantic precision cases in fixed order."""

    cases_by_id = {
        case[
            "case_id"
        ]: case
        for case
        in benchmark[
            "cases"
        ]
    }

    missing = [
        case_id
        for case_id
        in TARGET_CASE_IDS
        if case_id
        not in cases_by_id
    ]

    if missing:
        raise ValueError(
            "Week 26 semantic precision benchmark "
            f"is missing cases: {missing}"
        )

    return [
        cases_by_id[
            case_id
        ]
        for case_id
        in TARGET_CASE_IDS
    ]


def _expected_claim_lookup(
    case: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Index expected claim results by claim ID."""

    return {
        result[
            "claim_id"
        ]: result
        for result
        in case[
            "expected_claim_results"
        ]
    }


def _evidence_lookup(
    case: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Index benchmark evidence by evidence ID."""

    return {
        evidence[
            "evidence_id"
        ]: evidence
        for evidence
        in case[
            "evidence_items"
        ]
    }


def _citation_to_evidence_id(
    case: dict[str, Any],
) -> dict[str, str]:
    """Map benchmark citation IDs to evidence IDs."""

    return {
        citation[
            "citation_id"
        ]: citation[
            "evidence_id"
        ]
        for citation
        in case[
            "citation_index"
        ]
    }


def _evidence_for_claim(
    case: dict[str, Any],
    claim: dict[str, Any],
    expected: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return evidence legitimately associated with one claim.

    Priority:

    1. benchmark required_evidence_ids;
    2. explicitly cited evidence.

    Duplicate evidence is removed while preserving order.
    """

    evidence_by_id = (
        _evidence_lookup(
            case
        )
    )

    citation_map = (
        _citation_to_evidence_id(
            case
        )
    )

    evidence_ids: list[str] = []

    for evidence_id in expected.get(
        "required_evidence_ids",
        [],
    ):
        if evidence_id not in evidence_ids:
            evidence_ids.append(
                evidence_id
            )

    for citation_id in claim.get(
        "citation_ids",
        [],
    ):
        evidence_id = (
            citation_map.get(
                citation_id
            )
        )

        if (
            evidence_id is not None
            and evidence_id
            not in evidence_ids
        ):
            evidence_ids.append(
                evidence_id
            )

    return [
        evidence_by_id[
            evidence_id
        ]
        for evidence_id
        in evidence_ids
        if evidence_id
        in evidence_by_id
    ]


def _support_was_not_increased(
    before: str,
    after: str,
) -> bool:
    """Prove semantic precision did not increase support authority."""

    if before not in SUPPORT_ORDER:
        raise ValueError(
            f"Unknown baseline support status: {before}"
        )

    if after not in SUPPORT_ORDER:
        raise ValueError(
            f"Unknown revised support status: {after}"
        )

    return (
        SUPPORT_ORDER[
            after
        ]
        <= SUPPORT_ORDER[
            before
        ]
    )


def _run_claim(
    *,
    case: dict[str, Any],
    claim: dict[str, Any],
    expected: dict[str, Any],
    baseline_status: str,
) -> dict[str, Any]:
    """Run one claim through semantic precision hardening."""

    evidence_items = (
        _evidence_for_claim(
            case,
            claim,
            expected,
        )
    )

    audit = (
        audit_semantic_precision(
            claim_id=claim[
                "claim_id"
            ],
            claim_text=claim[
                "text"
            ],
            evidence_items=evidence_items,
            existing_support_status=(
                baseline_status
            ),
        )
    )

    revised_status = audit[
        "revised_support_status"
    ]

    expected_status = expected[
        "expected_support_status"
    ]

    support_matches = (
        revised_status
        == expected_status
    )

    authority_preserved = (
        _support_was_not_increased(
            baseline_status,
            revised_status,
        )
    )

    failure_reasons = []

    if not support_matches:
        failure_reasons.append(
            "Revised support mismatch: "
            f"expected {expected_status}, "
            f"got {revised_status}"
        )

    if not authority_preserved:
        failure_reasons.append(
            "Semantic precision illegally increased "
            "support authority."
        )

    return {
        "claim_id": claim[
            "claim_id"
        ],
        "claim_text": claim[
            "text"
        ],
        "baseline_support_status": (
            baseline_status
        ),
        "expected_support_status": (
            expected_status
        ),
        "revised_support_status": (
            revised_status
        ),
        "support_matches": (
            support_matches
        ),
        "support_authority_not_increased": (
            authority_preserved
        ),
        "semantic_decision": audit[
            "decision"
        ],
        "support_reduced": audit[
            "support_reduced"
        ],
        "modal_strengthening_detected": audit[
            "modal_strengthening_detected"
        ],
        "immediacy_strengthening_detected": audit[
            "immediacy_strengthening_detected"
        ],
        "role_responsibility_unsupported": audit[
            "role_responsibility_unsupported"
        ],
        "authority_attribution_unsupported": audit[
            "authority_attribution_unsupported"
        ],
        "risk_signals": audit[
            "risk_signals"
        ],
        "evidence_ids": [
            evidence.get(
                "evidence_id"
            )
            for evidence
            in evidence_items
        ],
        "audit": audit,
        "failure_reasons": (
            failure_reasons
        ),
    }


def _run_case(
    case: dict[str, Any],
) -> dict[str, Any]:
    """Run one target case through baseline + semantic precision."""

    baseline_result = (
        run_existing_stack_case(
            case
        )
    )

    baseline_statuses = (
        baseline_result[
            "actual_claim_statuses"
        ]
    )

    expected_lookup = (
        _expected_claim_lookup(
            case
        )
    )

    claim_results = []

    for claim in case[
        "candidate_claims"
    ]:
        claim_id = claim[
            "claim_id"
        ]

        expected = (
            expected_lookup.get(
                claim_id
            )
        )

        if expected is None:
            raise ValueError(
                f"{case['case_id']} has no expected "
                f"claim result for {claim_id}."
            )

        baseline_status = (
            baseline_statuses.get(
                claim_id
            )
        )

        if baseline_status is None:
            raise ValueError(
                f"{case['case_id']} baseline produced "
                f"no support status for {claim_id}."
            )

        claim_results.append(
            _run_claim(
                case=case,
                claim=claim,
                expected=expected,
                baseline_status=(
                    baseline_status
                ),
            )
        )

    case_match = all(
        result[
            "support_matches"
        ]
        and result[
            "support_authority_not_increased"
        ]
        for result
        in claim_results
    )

    return {
        "case_id": case[
            "case_id"
        ],
        "case_name": case[
            "case_name"
        ],
        "threat_class": case[
            "threat_class"
        ],
        "baseline_claim_statuses": (
            baseline_statuses
        ),
        "claim_results": (
            claim_results
        ),
        "case_match": (
            case_match
        ),
        "failure_reasons": [
            failure
            for result
            in claim_results
            for failure
            in result[
                "failure_reasons"
            ]
        ],
    }


def _summarise(
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Summarise focused semantic benchmark."""

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

    modal_cases = []

    role_cases = []

    immediacy_cases = []

    reduced_claims = []

    authority_increase_violations = []

    for result in results:
        case_id = result[
            "case_id"
        ]

        for claim in result[
            "claim_results"
        ]:
            if claim[
                "modal_strengthening_detected"
            ]:
                modal_cases.append(
                    case_id
                )

            if claim[
                "role_responsibility_unsupported"
            ]:
                role_cases.append(
                    case_id
                )

            if claim[
                "immediacy_strengthening_detected"
            ]:
                immediacy_cases.append(
                    case_id
                )

            if claim[
                "support_reduced"
            ]:
                reduced_claims.append(
                    claim[
                        "claim_id"
                    ]
                )

            if not claim[
                "support_authority_not_increased"
            ]:
                authority_increase_violations.append(
                    claim[
                        "claim_id"
                    ]
                )

    return {
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
            if results
            else 0.0
        ),
        "modal_strengthening_case_ids": sorted(
            set(
                modal_cases
            )
        ),
        "role_responsibility_case_ids": sorted(
            set(
                role_cases
            )
        ),
        "immediacy_strengthening_case_ids": sorted(
            set(
                immediacy_cases
            )
        ),
        "support_reduced_claim_ids": (
            reduced_claims
        ),
        "authority_increase_violation_claim_ids": (
            authority_increase_violations
        ),
        "mismatched_case_ids": [
            result[
                "case_id"
            ]
            for result
            in mismatched
        ],
    }


def run_semantic_precision_benchmark() -> dict[str, Any]:
    """Execute focused Week 26 semantic precision benchmark."""

    benchmark = _load_benchmark()

    cases = _target_cases(
        benchmark
    )

    results = [
        _run_case(
            case
        )
        for case
        in cases
    ]

    summary = _summarise(
        results
    )

    report = {
        "benchmark_name": (
            "Week 26 Semantic Precision Benchmark"
        ),
        "benchmark_version": "1.0",
        "source_benchmark": benchmark[
            "benchmark_name"
        ],
        "evaluation_type": (
            "week26_semantic_precision_hardening"
        ),
        "target_case_ids": list(
            TARGET_CASE_IDS
        ),
        "summary": summary,
        "results": results,
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
    """Print concise semantic benchmark evidence."""

    summary = report[
        "summary"
    ]

    print(
        "Week 26 Semantic Precision Benchmark"
    )

    print(
        "------------------------------------"
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
        "Modal-strengthening cases: "
        f"{summary['modal_strengthening_case_ids']}"
    )

    print(
        "Role/responsibility cases: "
        f"{summary['role_responsibility_case_ids']}"
    )

    print(
        "Immediacy-strengthening cases: "
        f"{summary['immediacy_strengthening_case_ids']}"
    )

    print(
        "Support-reduced claims: "
        f"{summary['support_reduced_claim_ids']}"
    )

    print(
        "Authority-increase violations: "
        f"{summary['authority_increase_violation_claim_ids']}"
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
        run_semantic_precision_benchmark()
    )

    _print_summary(
        report
    )


if __name__ == "__main__":
    main()