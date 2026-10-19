"""Week 26 adversarial baseline against the existing assurance stack.

Purpose
-------

Run the new Week 26 adversarial benchmark through assurance controls
that existed before Week 26 hardening.

This establishes a BEFORE measurement.

The runner deliberately does not implement the new Week 26 controls.
Its job is to show what the existing citation, precedence,
groundedness / hallucination-resistance architecture already catches
and where new hardening is required.

Run with:

    python -m src.evaluation.run_week26_existing_stack_baseline
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


from src.evidence.evidence_precedence import (
    assess_evidence_precedence,
)
from src.evaluation.hallucination_resistance import (
    audit_answer_hallucination_resistance,
)
from src.evaluation.multi_source_claim_verification import (
    verify_multi_source_relationship_claim,
)
from src.evaluation.validate_week26_benchmark import (
    BENCHMARK_PATH,
    validate_benchmark,
)
from src.governance.citation_verification import (
    verify_answer_citations,
)


OUTPUT_PATH = (
    ROOT
    / "outputs"
    / "week26_existing_stack_baseline.json"
)


SUPPORTED = "SUPPORTED"
PASS = "PASS"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
ABSTAIN = "ABSTAIN"


def _load_benchmark() -> dict[str, Any]:
    """Load and validate the Week 26 adversarial benchmark."""

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


def _evidence_by_id(
    case: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Return benchmark evidence indexed by evidence ID."""

    return {
        evidence["evidence_id"]: evidence
        for evidence
        in case["evidence_items"]
    }


def _citation_lookup(
    case: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Resolve citation IDs to evidence items."""

    evidence_lookup = _evidence_by_id(
        case
    )

    result: dict[
        str,
        dict[str, Any],
    ] = {}

    for citation in case[
        "citation_index"
    ]:
        evidence = evidence_lookup.get(
            citation["evidence_id"]
        )

        if evidence is not None:
            result[
                citation["citation_id"]
            ] = evidence

    return result


def _convert_evidence_for_citation_verifier(
    case: dict[str, Any],
) -> list[dict[str, Any]]:
    """Adapt Week 26 evidence to the existing citation verifier."""

    converted = []

    for item in case[
        "evidence_items"
    ]:
        converted.append(
            {
                "document_id": item[
                    "document_id"
                ],
                "chunk_id": item[
                    "chunk_id"
                ],
                "status": item[
                    "status"
                ],
                "title": item[
                    "title"
                ],
                "text": item[
                    "text"
                ],
            }
        )

    return converted


def _convert_evidence_for_precedence(
    case: dict[str, Any],
) -> list[dict[str, Any]]:
    """Adapt Week 26 evidence to existing Evidence Precedence."""

    converted = []

    for item in case[
        "evidence_items"
    ]:
        converted.append(
            {
                "document_id": item[
                    "document_id"
                ],
                "status": item[
                    "status"
                ],
                "evidence_text": item[
                    "text"
                ],
            }
        )

    return converted


def _claim_expected_result_lookup(
    case: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Index expected claim outcomes."""

    return {
        result["claim_id"]: result
        for result
        in case[
            "expected_claim_results"
        ]
    }


def _citation_object(
    case: dict[str, Any],
    citation_id: str,
) -> dict[str, str] | None:
    """Resolve a benchmark citation to existing verifier shape.

    Existing citation verification expects:

        {
            "document_id": "...",
            "chunk_id": "..."
        }

    rather than a raw citation ID or document ID string.
    """

    citation_lookup = _citation_lookup(
        case
    )

    evidence = citation_lookup.get(
        citation_id
    )

    if evidence is None:
        return None

    return {
        "document_id": str(
            evidence[
                "document_id"
            ]
        ),
        "chunk_id": str(
            evidence[
                "chunk_id"
            ]
        ),
    }


def _convert_claims_for_single_source_verifier(
    case: dict[str, Any],
) -> list[dict[str, Any]]:
    """Adapt Week 26 claims to the existing single-source verifier.

    The Week 25 verifier accepts one citation object per claim.

    For a Week 26 multi-citation claim, the first listed citation is
    therefore used for the single-source baseline stage.

    Existing explicit multi-source conflict handling is applied later.
    """

    converted = []

    for claim in case[
        "candidate_claims"
    ]:
        citation_ids = list(
            claim.get(
                "citation_ids",
                [],
            )
        )

        citation = None

        if citation_ids:
            citation = _citation_object(
                case,
                citation_ids[0],
            )

        converted.append(
            {
                "claim_id": claim[
                    "claim_id"
                ],
                "claim_text": claim[
                    "text"
                ],
                "citation": citation,
            }
        )

    return converted


def _run_single_source_verification(
    case: dict[str, Any],
) -> dict[str, Any]:
    """Run existing citation verification unchanged."""

    claims = (
        _convert_claims_for_single_source_verifier(
            case
        )
    )

    evidence = (
        _convert_evidence_for_citation_verifier(
            case
        )
    )

    return verify_answer_citations(
        claims,
        evidence,
    )


def _relationship_type_for_claim(
    case: dict[str, Any],
    claim: dict[str, Any],
) -> str | None:
    """Return relationship supported by existing Week 25 logic.

    The existing Week 25 multi-source layer explicitly supported
    conflict relationship verification.

    Week 26 relationship-aware composition has not been implemented
    yet, so other relationship types deliberately remain unsupported
    in this BEFORE baseline.
    """

    if not case.get(
        "conflict_expected",
        False,
    ):
        return None

    citation_ids = list(
        claim.get(
            "citation_ids",
            [],
        )
    )

    if len(
        citation_ids
    ) < 2:
        return None

    return "CONFLICT"


def _run_existing_multi_source_logic(
    case: dict[str, Any],
    precedence_result: dict[str, Any],
    single_source_result: dict[str, Any],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    """Apply existing Week 25 multi-source conflict logic where possible."""

    claim_results = [
        dict(
            result
        )
        for result
        in single_source_result.get(
            "claim_results",
            [],
        )
    ]

    result_by_claim_id = {
        result["claim_id"]: result
        for result
        in claim_results
    }

    citation_to_evidence = (
        _citation_lookup(
            case
        )
    )

    expected_lookup = (
        _claim_expected_result_lookup(
            case
        )
    )

    multi_source_results = []

    for claim in case[
        "candidate_claims"
    ]:
        relationship_type = (
            _relationship_type_for_claim(
                case,
                claim,
            )
        )

        if relationship_type is None:
            continue

        claim_id = claim[
            "claim_id"
        ]

        expected_result = (
            expected_lookup.get(
                claim_id,
                {},
            )
        )

        required_citation_ids = list(
            expected_result.get(
                "required_citation_ids",
                [],
            )
        )

        if len(
            required_citation_ids
        ) < 2:
            required_citation_ids = list(
                claim.get(
                    "citation_ids",
                    [],
                )
            )

        relational_claim = {
            "claim_id": claim_id,
            "claim_text": claim[
                "text"
            ],
            "citation_ids": (
                required_citation_ids
            ),
        }

        joint_result = (
            verify_multi_source_relationship_claim(
                relational_claim,
                case[
                    "citation_index"
                ],
                citation_to_evidence,
                precedence_result,
                relationship_type=(
                    relationship_type
                ),
                required_citation_ids=(
                    required_citation_ids
                ),
            )
        )

        multi_source_results.append(
            joint_result
        )

        result_by_claim_id[
            claim_id
        ] = joint_result

    ordered_results = []

    for claim in case[
        "candidate_claims"
    ]:
        claim_id = claim[
            "claim_id"
        ]

        result = (
            result_by_claim_id.get(
                claim_id
            )
        )

        if result is None:
            result = {
                "claim_id": claim_id,
                "status": "UNSUPPORTED",
                "reason": (
                    "Existing assurance stack produced "
                    "no claim result."
                ),
            }

        ordered_results.append(
            result
        )

    return (
        ordered_results,
        multi_source_results,
    )


def _derive_verification_decision(
    claim_results: list[dict[str, Any]],
    single_source_result: dict[str, Any],
) -> str:
    """Derive answer-level citation verification decision."""

    if not claim_results:
        return single_source_result.get(
            "decision",
            ABSTAIN,
        )

    if all(
        result.get(
            "status"
        )
        == SUPPORTED
        for result
        in claim_results
    ):
        return PASS

    return REVIEW_REQUIRED


def _expected_claim_statuses(
    case: dict[str, Any],
) -> dict[str, str]:
    """Return Week 26 expected claim support states."""

    return {
        result[
            "claim_id"
        ]: result[
            "expected_support_status"
        ]
        for result
        in case[
            "expected_claim_results"
        ]
    }


def _actual_claim_statuses(
    claim_results: list[dict[str, Any]],
) -> dict[str, str]:
    """Return existing-stack claim support states."""

    return {
        result[
            "claim_id"
        ]: result.get(
            "status",
            "UNKNOWN",
        )
        for result
        in claim_results
    }


def _compare_claim_statuses(
    expected: dict[str, str],
    actual: dict[str, str],
) -> tuple[
    bool,
    list[str],
]:
    """Compare expected and current-stack claim states."""

    failures: list[str] = []

    if set(
        expected
    ) != set(
        actual
    ):
        missing = sorted(
            set(
                expected
            )
            - set(
                actual
            )
        )

        unexpected = sorted(
            set(
                actual
            )
            - set(
                expected
            )
        )

        if missing:
            failures.append(
                "Missing claim results: "
                f"{missing}"
            )

        if unexpected:
            failures.append(
                "Unexpected claim results: "
                f"{unexpected}"
            )

        return (
            False,
            failures,
        )

    for claim_id in expected:
        if (
            expected[
                claim_id
            ]
            != actual[
                claim_id
            ]
        ):
            failures.append(
                f"{claim_id}: expected "
                f"{expected[claim_id]}, got "
                f"{actual[claim_id]}"
            )

    return (
        not failures,
        failures,
    )


def _build_hallucination_claims(
    case: dict[str, Any],
) -> list[dict[str, Any]]:
    """Build claims for existing hallucination-resistance audit."""

    return [
        {
            "claim_id": claim[
                "claim_id"
            ],
            "claim_text": claim[
                "text"
            ],
        }
        for claim
        in case[
            "candidate_claims"
        ]
    ]


def _build_evidence_by_claim(
    case: dict[str, Any],
) -> dict[
    str,
    list[dict[str, Any]],
]:
    """Map claims to benchmark-approved evidence."""

    evidence_lookup = _evidence_by_id(
        case
    )

    expected_lookup = (
        _claim_expected_result_lookup(
            case
        )
    )

    result: dict[
        str,
        list[dict[str, Any]],
    ] = {}

    for claim in case[
        "candidate_claims"
    ]:
        claim_id = claim[
            "claim_id"
        ]

        expected_result = (
            expected_lookup.get(
                claim_id,
                {},
            )
        )

        supporting_ids = list(
            expected_result.get(
                "required_evidence_ids",
                [],
            )
        )

        evidence_items = []

        for evidence_id in supporting_ids:
            evidence = (
                evidence_lookup.get(
                    evidence_id
                )
            )

            if evidence is None:
                continue

            adapted = dict(
                evidence
            )

            adapted[
                "evidence_text"
            ] = evidence[
                "text"
            ]

            evidence_items.append(
                adapted
            )

        result[
            claim_id
        ] = evidence_items

    return result


def _run_existing_hallucination_audit(
    case: dict[str, Any],
) -> dict[str, Any]:
    """Run the existing Week 25 hallucination-resistance layer."""

    claims = (
        _build_hallucination_claims(
            case
        )
    )

    evidence_by_claim = (
        _build_evidence_by_claim(
            case
        )
    )

    return audit_answer_hallucination_resistance(
        claims,
        evidence_by_claim,
        upstream_governance_decision=(
            case[
                "expected_governance_decision"
            ]
        ),
    )


def _expected_verification_decision(
    case: dict[str, Any],
) -> str:
    """Derive citation-verification expectation from material claims."""

    governance = case[
        "expected_governance_decision"
    ]

    if governance == ABSTAIN:
        return ABSTAIN

    material_claim_ids = {
        claim[
            "claim_id"
        ]
        for claim
        in case[
            "candidate_claims"
        ]
        if claim.get(
            "material",
            True,
        )
    }

    expected_statuses = [
        result[
            "expected_support_status"
        ]
        for result
        in case[
            "expected_claim_results"
        ]
        if result[
            "claim_id"
        ]
        in material_claim_ids
    ]

    if (
        expected_statuses
        and all(
            status
            == SUPPORTED
            for status
            in expected_statuses
        )
    ):
        return PASS

    return REVIEW_REQUIRED


def _derive_current_stack_final_decision(
    case: dict[str, Any],
    verification_decision: str,
    hallucination_result: dict[str, Any],
) -> str:
    """Apply existing governance ceiling and assurance semantics."""

    governance = case[
        "expected_governance_decision"
    ]

    if governance == ABSTAIN:
        return ABSTAIN

    if governance == REVIEW_REQUIRED:
        return REVIEW_REQUIRED

    if verification_decision != PASS:
        return REVIEW_REQUIRED

    if hallucination_result.get(
        "decision"
    ) != PASS:
        return REVIEW_REQUIRED

    return PASS


def _run_case(
    case: dict[str, Any],
) -> dict[str, Any]:
    """Run one Week 26 case through pre-Week-26 assurance controls."""

    case_id = case[
        "case_id"
    ]

    precedence_input = (
        _convert_evidence_for_precedence(
            case
        )
    )

    precedence_result = (
        assess_evidence_precedence(
            precedence_input
        )
    )

    single_source_result = (
        _run_single_source_verification(
            case
        )
    )

    (
        final_claim_results,
        multi_source_results,
    ) = _run_existing_multi_source_logic(
        case,
        precedence_result,
        single_source_result,
    )

    actual_verification = (
        _derive_verification_decision(
            final_claim_results,
            single_source_result,
        )
    )

    expected_verification = (
        _expected_verification_decision(
            case
        )
    )

    expected_claim_statuses = (
        _expected_claim_statuses(
            case
        )
    )

    actual_claim_statuses = (
        _actual_claim_statuses(
            final_claim_results
        )
    )

    (
        claim_statuses_match,
        claim_failures,
    ) = _compare_claim_statuses(
        expected_claim_statuses,
        actual_claim_statuses,
    )

    hallucination_result = (
        _run_existing_hallucination_audit(
            case
        )
    )

    actual_precedence = (
        precedence_result.get(
            "decision"
        )
    )

    expected_precedence = case[
        "expected_precedence_decision"
    ]

    precedence_matches = (
        expected_precedence
        == actual_precedence
    )

    verification_matches = (
        expected_verification
        == actual_verification
    )

    expected_final_decision = case[
        "expected_final_assurance_decision"
    ]

    actual_final_decision = (
        _derive_current_stack_final_decision(
            case,
            actual_verification,
            hallucination_result,
        )
    )

    final_decision_matches = (
        expected_final_decision
        == actual_final_decision
    )

    expected_hallucination = case[
        "expected_hallucination_decision"
    ]

    actual_hallucination = (
        hallucination_result.get(
            "decision"
        )
    )

    hallucination_matches = (
        expected_hallucination
        == actual_hallucination
    )

    failure_reasons = list(
        claim_failures
    )

    if not verification_matches:
        failure_reasons.append(
            "Verification decision mismatch: "
            f"expected {expected_verification}, "
            f"got {actual_verification}"
        )

    if not precedence_matches:
        failure_reasons.append(
            "Precedence decision mismatch: "
            f"expected {expected_precedence}, "
            f"got {actual_precedence}"
        )

    if not hallucination_matches:
        failure_reasons.append(
            "Hallucination decision mismatch: "
            f"expected {expected_hallucination}, "
            f"got {actual_hallucination}"
        )

    if not final_decision_matches:
        failure_reasons.append(
            "Final assurance decision mismatch: "
            f"expected {expected_final_decision}, "
            f"got {actual_final_decision}"
        )

    baseline_match = (
        claim_statuses_match
        and verification_matches
        and precedence_matches
        and hallucination_matches
        and final_decision_matches
    )

    return {
        "case_id": case_id,
        "case_name": case[
            "case_name"
        ],
        "threat_class": case[
            "threat_class"
        ],
        "expected_claim_statuses": (
            expected_claim_statuses
        ),
        "actual_claim_statuses": (
            actual_claim_statuses
        ),
        "expected_verification_decision": (
            expected_verification
        ),
        "actual_verification_decision": (
            actual_verification
        ),
        "expected_precedence_decision": (
            expected_precedence
        ),
        "actual_precedence_decision": (
            actual_precedence
        ),
        "expected_hallucination_decision": (
            expected_hallucination
        ),
        "actual_hallucination_decision": (
            actual_hallucination
        ),
        "expected_final_assurance_decision": (
            expected_final_decision
        ),
        "actual_final_assurance_decision": (
            actual_final_decision
        ),
        "multi_source_verification_used": bool(
            multi_source_results
        ),
        "multi_source_results": (
            multi_source_results
        ),
        "hallucination_risk_count": (
            hallucination_result.get(
                "hallucination_risk_count",
                0,
            )
        ),
        "overstatement_count": (
            hallucination_result.get(
                "overstatement_audit",
                {},
            ).get(
                "overstatement_count",
                0,
            )
        ),
        "review_authority_increase_detected": (
            hallucination_result.get(
                "review_authority_increase_detected",
                False,
            )
        ),
        "abstention_violation_detected": (
            hallucination_result.get(
                "abstention_violation_detected",
                False,
            )
        ),
        "hallucination_result": (
            hallucination_result
        ),
        "baseline_match": (
            baseline_match
        ),
        "failure_reasons": (
            failure_reasons
        ),
    }


def _summarise(
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Summarise current-stack Week 26 performance."""

    matched = [
        result
        for result
        in results
        if result[
            "baseline_match"
        ]
    ]

    mismatched = [
        result
        for result
        in results
        if not result[
            "baseline_match"
        ]
    ]

    claim_mismatch_cases = [
        result[
            "case_id"
        ]
        for result
        in results
        if result[
            "expected_claim_statuses"
        ]
        != result[
            "actual_claim_statuses"
        ]
    ]

    precedence_mismatch_cases = [
        result[
            "case_id"
        ]
        for result
        in results
        if (
            result[
                "expected_precedence_decision"
            ]
            != result[
                "actual_precedence_decision"
            ]
        )
    ]

    hallucination_mismatch_cases = [
        result[
            "case_id"
        ]
        for result
        in results
        if (
            result[
                "expected_hallucination_decision"
            ]
            != result[
                "actual_hallucination_decision"
            ]
        )
    ]

    final_decision_mismatch_cases = [
        result[
            "case_id"
        ]
        for result
        in results
        if (
            result[
                "expected_final_assurance_decision"
            ]
            != result[
                "actual_final_assurance_decision"
            ]
        )
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
        "multi_source_case_count": sum(
            1
            for result
            in results
            if result[
                "multi_source_verification_used"
            ]
        ),
        "hallucination_risk_cases_detected": sum(
            1
            for result
            in results
            if result[
                "hallucination_risk_count"
            ]
            > 0
        ),
        "overstatement_cases_detected": sum(
            1
            for result
            in results
            if result[
                "overstatement_count"
            ]
            > 0
        ),
        "review_authority_increase_cases_detected": sum(
            1
            for result
            in results
            if result[
                "review_authority_increase_detected"
            ]
        ),
        "abstention_violation_cases_detected": sum(
            1
            for result
            in results
            if result[
                "abstention_violation_detected"
            ]
        ),
        "mismatched_case_ids": [
            result[
                "case_id"
            ]
            for result
            in mismatched
        ],
        "claim_status_mismatch_case_ids": (
            claim_mismatch_cases
        ),
        "precedence_mismatch_case_ids": (
            precedence_mismatch_cases
        ),
        "hallucination_mismatch_case_ids": (
            hallucination_mismatch_cases
        ),
        "final_decision_mismatch_case_ids": (
            final_decision_mismatch_cases
        ),
    }


def main() -> None:
    """Run Week 26 BEFORE baseline."""

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
        "benchmark_name": benchmark[
            "benchmark_name"
        ],
        "benchmark_version": benchmark[
            "benchmark_version"
        ],
        "evaluation_type": (
            "week26_existing_stack_before_hardening"
        ),
        "interpretation": (
            "This is a BEFORE measurement. "
            "Mismatches identify Week 26 hardening targets "
            "and are not treated as benchmark defects."
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
            output,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        "Week 26 Existing-Stack Adversarial Baseline"
    )

    print(
        "-------------------------------------------"
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
        "Existing multi-source verification used: "
        f"{summary['multi_source_case_count']}"
    )

    print(
        "Hallucination-risk cases detected: "
        f"{summary['hallucination_risk_cases_detected']}"
    )

    print(
        "Overstatement cases detected: "
        f"{summary['overstatement_cases_detected']}"
    )

    print(
        "Review-authority increases detected: "
        f"{summary['review_authority_increase_cases_detected']}"
    )

    print(
        "Abstention violations detected: "
        f"{summary['abstention_violation_cases_detected']}"
    )

    print()

    print(
        "Mismatched cases:"
    )

    if summary[
        "mismatched_case_ids"
    ]:
        for case_id in summary[
            "mismatched_case_ids"
        ]:
            print(
                f"  {case_id}"
            )
    else:
        print(
            "  none"
        )

    print()

    print(
        "Claim-status mismatch cases:"
    )

    if summary[
        "claim_status_mismatch_case_ids"
    ]:
        for case_id in summary[
            "claim_status_mismatch_case_ids"
        ]:
            print(
                f"  {case_id}"
            )
    else:
        print(
            "  none"
        )

    print()

    print(
        "Precedence mismatch cases:"
    )

    if summary[
        "precedence_mismatch_case_ids"
    ]:
        for case_id in summary[
            "precedence_mismatch_case_ids"
        ]:
            print(
                f"  {case_id}"
            )
    else:
        print(
            "  none"
        )

    print()

    print(
        "Hallucination mismatch cases:"
    )

    if summary[
        "hallucination_mismatch_case_ids"
    ]:
        for case_id in summary[
            "hallucination_mismatch_case_ids"
        ]:
            print(
                f"  {case_id}"
            )
    else:
        print(
            "  none"
        )

    print()

    print(
        "Final-decision mismatch cases:"
    )

    if summary[
        "final_decision_mismatch_case_ids"
    ]:
        for case_id in summary[
            "final_decision_mismatch_case_ids"
        ]:
            print(
                f"  {case_id}"
            )
    else:
        print(
            "  none"
        )

    print()

    print(
        f"Output: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()