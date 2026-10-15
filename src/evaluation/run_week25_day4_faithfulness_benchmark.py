"""Week 25 Day 4 integrated faithfulness benchmark.

This runner combines the existing Week 25 citation benchmark with the Day 4
groundedness and hallucination-resistance architecture.

Layers:

1. existing citation / precedence benchmark evaluation;
2. groundedness;
3. overstatement detection;
4. governance-preservation checks;
5. abstention-boundary checks;
6. explicit conflict-coverage checks.

The benchmark remains authoritative.

Important evaluation principle:

A benchmark case may trigger more conservative safety controls than its tags
explicitly name.

That is acceptable.

The integration benchmark therefore requires that expected safety signals are
detected, but it does not fail merely because an additional safe detector also
fires.
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


from src.evaluation.hallucination_resistance import (
    audit_answer_hallucination_resistance,
)
from src.evaluation.run_week25_benchmark_baseline import (
    _run_case as run_day3_case,
)
from src.evaluation.validate_week25_benchmark import (
    BENCHMARK_PATH,
    validate_benchmark,
)


OUTPUT_PATH = (
    ROOT
    / "outputs"
    / "week25_day4_faithfulness_benchmark.json"
)


PASS = "PASS"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
ABSTAIN = "ABSTAIN"


def _load_benchmark() -> dict[str, Any]:
    """Load and validate the authoritative benchmark."""

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


def _evidence_lookup(
    case: dict[str, Any],
) -> dict[
    str,
    dict[str, Any],
]:
    """Build evidence lookup by benchmark evidence ID."""

    return {
        evidence[
            "evidence_id"
        ]: evidence
        for evidence
        in case[
            "evidence_items"
        ]
    }


def _build_claims(
    case: dict[str, Any],
) -> list[dict[str, Any]]:
    """Convert benchmark claims into Day 4 claim objects."""

    return [
        {
            "claim_id": (
                claim[
                    "claim_id"
                ]
            ),
            "claim_text": (
                claim[
                    "claim_text"
                ]
            ),
        }
        for claim
        in case[
            "expected_claims"
        ]
    ]


def _build_evidence_by_claim(
    case: dict[str, Any],
) -> dict[
    str,
    list[dict[str, Any]],
]:
    """Map each claim to benchmark-approved supporting evidence.

    Day 4 deliberately does not grant every claim access to every retrieved
    evidence item.

    The benchmark's supporting_evidence_ids define the evidence set that may
    legitimately support the claim.

    If that list is empty, the groundedness layer should see no approved
    supporting evidence. This is useful for lifecycle and citation-failure
    cases and may produce additional conservative Day 4 risk signals.
    """

    evidence_by_id = (
        _evidence_lookup(
            case
        )
    )

    result = {}

    for claim in case[
        "expected_claims"
    ]:
        claim_id = claim[
            "claim_id"
        ]

        supporting_ids = (
            claim.get(
                "supporting_evidence_ids",
                [],
            )
        )

        evidence_items = []

        for evidence_id in supporting_ids:
            evidence = (
                evidence_by_id.get(
                    evidence_id
                )
            )

            if evidence is not None:
                evidence_items.append(
                    evidence
                )

        result[
            claim_id
        ] = evidence_items

    return result


def _derive_expected_integrated_decision(
    case: dict[str, Any],
) -> str:
    """Derive expected final safe-handling decision.

    Governance is the authority ceiling.

    ABSTAIN remains ABSTAIN.

    REVIEW_REQUIRED remains REVIEW_REQUIRED.

    AUTO_ANSWER can produce PASS only when citation verification itself passes.
    """

    governance = case[
        "expected_governance_decision"
    ]

    if governance == "ABSTAIN":
        return ABSTAIN

    if governance == "REVIEW_REQUIRED":
        return REVIEW_REQUIRED

    if (
        case[
            "expected_verification_decision"
        ]
        == PASS
    ):
        return PASS

    return REVIEW_REQUIRED


def _derive_actual_integrated_decision(
    case: dict[str, Any],
    day3_result: dict[str, Any],
    hallucination_result: dict[str, Any],
) -> str:
    """Combine citation and Day 4 assurance without increasing authority."""

    governance = case[
        "expected_governance_decision"
    ]

    if governance == "ABSTAIN":
        return ABSTAIN

    if governance == "REVIEW_REQUIRED":
        return REVIEW_REQUIRED

    if (
        day3_result[
            "actual_verification_decision"
        ]
        != PASS
    ):
        return REVIEW_REQUIRED

    if (
        hallucination_result[
            "decision"
        ]
        != PASS
    ):
        return REVIEW_REQUIRED

    return PASS


def _audit_conflict_coverage(
    case: dict[str, Any],
) -> dict[str, Any]:
    """Detect one-sided use of explicitly conflicting evidence.

    Conflict coverage is based on explicit benchmark citation requirements,
    not semantic inference.

    Example:

    Case requires:
        E1 + E2

    Claim preserves:
        E1 only

    Result:
        CONFLICT_IGNORED
    """

    if not case.get(
        "conflict_expected",
        False,
    ):
        return {
            "applicable": False,
            "conflict_ignored": False,
            "reason": (
                "Case does not contain an expected "
                "evidence conflict."
            ),
            "required_citation_ids": [],
            "claim_results": [],
        }

    required_case_citations = set(
        case.get(
            "required_citation_ids",
            [],
        )
    )

    claim_results = []

    conflict_ignored = False

    for claim in case[
        "expected_claims"
    ]:
        claim_required = set(
            claim.get(
                "required_citation_ids",
                [],
            )
        )

        missing = sorted(
            required_case_citations
            - claim_required
        )

        if missing:
            status = (
                "CONFLICT_IGNORED"
            )

            conflict_ignored = True

        else:
            status = (
                "CONFLICT_PRESERVED"
            )

        claim_results.append(
            {
                "claim_id": (
                    claim[
                        "claim_id"
                    ]
                ),
                "status": status,
                "claim_required_citation_ids": sorted(
                    claim_required
                ),
                "missing_conflict_citation_ids": (
                    missing
                ),
            }
        )

    return {
        "applicable": True,
        "conflict_ignored": (
            conflict_ignored
        ),
        "reason": (
            "At least one conflict claim failed to "
            "preserve the full evidence set."
            if conflict_ignored
            else
            "Full conflict evidence coverage was preserved."
        ),
        "required_citation_ids": sorted(
            required_case_citations
        ),
        "claim_results": (
            claim_results
        ),
    }


def _expected_required_controls(
    case: dict[str, Any],
) -> dict[str, bool]:
    """Return only safety signals the benchmark explicitly requires.

    False means:

        this benchmark case does not REQUIRE the signal.

    It does NOT mean:

        the detector is forbidden from identifying the signal.

    This distinction is essential because several unsafe claims legitimately
    activate multiple conservative controls.
    """

    tags = {
        str(
            tag
        ).strip().lower()
        for tag
        in case.get(
            "benchmark_tags",
            [],
        )
    }

    expected_overall = (
        case[
            "expected_overall_faithfulness_status"
        ]
    )

    return {
        "unsafe_claim_detection_required": (
            expected_overall
            == "FAIL"
            and any(
                tag
                in tags
                for tag
                in {
                    "unsupported_claim",
                    "partial_support",
                    "overstatement",
                    "hallucination",
                    "authority",
                }
            )
        ),
        "overstatement_detection_required": (
            "overstatement"
            in tags
        ),
        "review_authority_detection_required": (
            case[
                "case_name"
            ]
            == (
                "review_required_becomes_authoritative"
            )
        ),
        "abstention_violation_detection_required": (
            case[
                "case_name"
            ]
            == (
                "abstain_contains_substantive_advice"
            )
        ),
        "conflict_ignored_detection_required": (
            case[
                "case_name"
            ]
            == "conflict_ignored"
        ),
    }


def _actual_control_signals(
    hallucination_result: dict[str, Any],
    conflict_result: dict[str, Any],
) -> dict[str, bool]:
    """Summarise actual Day 4 control activations."""

    hallucination_risk = (
        hallucination_result[
            "hallucination_risk_count"
        ]
        > 0
    )

    overstatement = (
        hallucination_result[
            "overstatement_audit"
        ][
            "overstatement_count"
        ]
        > 0
    )

    review_authority = (
        hallucination_result[
            "review_authority_increase_detected"
        ]
    )

    abstention_violation = (
        hallucination_result[
            "abstention_violation_detected"
        ]
    )

    conflict_ignored = (
        conflict_result[
            "conflict_ignored"
        ]
    )

    unsafe_claim_detected = any(
        (
            hallucination_risk,
            overstatement,
            review_authority,
            abstention_violation,
            conflict_ignored,
        )
    )

    return {
        "unsafe_claim_detected": (
            unsafe_claim_detected
        ),
        "hallucination_risk_detected": (
            hallucination_risk
        ),
        "overstatement_detected": (
            overstatement
        ),
        "review_authority_detected": (
            review_authority
        ),
        "abstention_violation_detected": (
            abstention_violation
        ),
        "conflict_ignored_detected": (
            conflict_ignored
        ),
    }


def _compare_required_controls(
    required: dict[str, bool],
    actual: dict[str, bool],
) -> tuple[
    bool,
    list[str],
]:
    """Require benchmark-mandated controls while allowing extra safe signals.

    Only required=True signals are asserted.

    Additional conservative detector activations are allowed and recorded.
    """

    failures = []

    mapping = {
        "unsafe_claim_detection_required": (
            "unsafe_claim_detected"
        ),
        "overstatement_detection_required": (
            "overstatement_detected"
        ),
        "review_authority_detection_required": (
            "review_authority_detected"
        ),
        "abstention_violation_detection_required": (
            "abstention_violation_detected"
        ),
        "conflict_ignored_detection_required": (
            "conflict_ignored_detected"
        ),
    }

    for required_name, actual_name in mapping.items():
        if not required[
            required_name
        ]:
            continue

        if not actual[
            actual_name
        ]:
            failures.append(
                f"{required_name}: required detector "
                f"signal was not produced"
            )

    return (
        len(
            failures
        )
        == 0,
        failures,
    )


def _run_case(
    case: dict[str, Any],
) -> dict[str, Any]:
    """Run one case through integrated Day 3 + Day 4 assurance."""

    day3_result = (
        run_day3_case(
            case
        )
    )

    claims = _build_claims(
        case
    )

    evidence_by_claim_id = (
        _build_evidence_by_claim(
            case
        )
    )

    hallucination_result = (
        audit_answer_hallucination_resistance(
            claims,
            evidence_by_claim_id,
            upstream_governance_decision=(
                case[
                    "expected_governance_decision"
                ]
            ),
        )
    )

    conflict_result = (
        _audit_conflict_coverage(
            case
        )
    )

    expected_decision = (
        _derive_expected_integrated_decision(
            case
        )
    )

    actual_decision = (
        _derive_actual_integrated_decision(
            case,
            day3_result,
            hallucination_result,
        )
    )

    decision_matches = (
        expected_decision
        == actual_decision
    )

    required_controls = (
        _expected_required_controls(
            case
        )
    )

    actual_controls = (
        _actual_control_signals(
            hallucination_result,
            conflict_result,
        )
    )

    (
        required_controls_match,
        control_failures,
    ) = _compare_required_controls(
        required_controls,
        actual_controls,
    )

    failure_reasons = []

    if not day3_result[
        "baseline_match"
    ]:
        failure_reasons.append(
            "Day 3 citation/precedence benchmark "
            "did not match."
        )

    if not decision_matches:
        failure_reasons.append(
            "Integrated decision mismatch: "
            f"expected {expected_decision}, "
            f"got {actual_decision}"
        )

    failure_reasons.extend(
        control_failures
    )

    benchmark_match = (
        day3_result[
            "baseline_match"
        ]
        and decision_matches
        and required_controls_match
    )

    return {
        "case_id": (
            case[
                "case_id"
            ]
        ),
        "case_name": (
            case[
                "case_name"
            ]
        ),
        "expected_overall_faithfulness_status": (
            case[
                "expected_overall_faithfulness_status"
            ]
        ),
        "expected_integrated_decision": (
            expected_decision
        ),
        "actual_integrated_decision": (
            actual_decision
        ),
        "day3_baseline_match": (
            day3_result[
                "baseline_match"
            ]
        ),
        "hallucination_decision": (
            hallucination_result[
                "decision"
            ]
        ),
        "hallucination_risk_count": (
            hallucination_result[
                "hallucination_risk_count"
            ]
        ),
        "overstatement_count": (
            hallucination_result[
                "overstatement_audit"
            ][
                "overstatement_count"
            ]
        ),
        "review_authority_increase_detected": (
            hallucination_result[
                "review_authority_increase_detected"
            ]
        ),
        "abstention_violation_detected": (
            hallucination_result[
                "abstention_violation_detected"
            ]
        ),
        "conflict_ignored_detected": (
            conflict_result[
                "conflict_ignored"
            ]
        ),
        "required_control_signals": (
            required_controls
        ),
        "actual_control_signals": (
            actual_controls
        ),
        "conflict_coverage": (
            conflict_result
        ),
        "hallucination_result": (
            hallucination_result
        ),
        "benchmark_match": (
            benchmark_match
        ),
        "failure_reasons": (
            failure_reasons
        ),
    }


def _summarise(
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Summarise Day 4 benchmark performance."""

    matched = [
        result
        for result
        in results
        if result[
            "benchmark_match"
        ]
    ]

    mismatched = [
        result
        for result
        in results
        if not result[
            "benchmark_match"
        ]
    ]

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
        "hallucination_risk_cases": sum(
            1
            for result
            in results
            if result[
                "hallucination_risk_count"
            ]
            > 0
        ),
        "overstatement_cases": sum(
            1
            for result
            in results
            if result[
                "overstatement_count"
            ]
            > 0
        ),
        "review_authority_increase_cases": sum(
            1
            for result
            in results
            if result[
                "review_authority_increase_detected"
            ]
        ),
        "abstention_violation_cases": sum(
            1
            for result
            in results
            if result[
                "abstention_violation_detected"
            ]
        ),
        "conflict_ignored_cases": sum(
            1
            for result
            in results
            if result[
                "conflict_ignored_detected"
            ]
        ),
        "mismatched_case_ids": [
            result[
                "case_id"
            ]
            for result
            in mismatched
        ],
    }


def main() -> None:
    """Run integrated Week 25 Day 4 benchmark."""

    benchmark = _load_benchmark()

    results = [
        _run_case(
            case
        )
        for case
        in benchmark[
            "cases"
        ]
    ]

    summary = _summarise(
        results
    )

    output = {
        "benchmark_name": (
            benchmark[
                "benchmark_name"
            ]
        ),
        "benchmark_version": (
            benchmark[
                "benchmark_version"
            ]
        ),
        "evaluation_type": (
            "week25_day4_integrated_faithfulness"
        ),
        "summary": (
            summary
        ),
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
            output,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        "Week 25 Day 4 Integrated Faithfulness Benchmark"
    )

    print(
        "-----------------------------------------------"
    )

    print(
        f"Cases: "
        f"{summary['case_count']}"
    )

    print(
        f"Matched: "
        f"{summary['matched_case_count']}"
    )

    print(
        f"Mismatched: "
        f"{summary['mismatched_case_count']}"
    )

    print(
        f"Match rate: "
        f"{summary['match_rate']:.1%}"
    )

    print(
        "Hallucination-risk cases detected: "
        f"{summary['hallucination_risk_cases']}"
    )

    print(
        "Overstatement cases detected: "
        f"{summary['overstatement_cases']}"
    )

    print(
        "Review authority increases detected: "
        f"{summary['review_authority_increase_cases']}"
    )

    print(
        "Abstention violations detected: "
        f"{summary['abstention_violation_cases']}"
    )

    print(
        "Ignored conflicts detected: "
        f"{summary['conflict_ignored_cases']}"
    )

    if summary[
        "mismatched_case_ids"
    ]:
        print(
            "Mismatched cases:"
        )

        for case_id in summary[
            "mismatched_case_ids"
        ]:
            print(
                f"  {case_id}"
            )

    else:
        print(
            "Mismatched cases: none"
        )

    print(
        f"Output: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()