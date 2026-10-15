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
from src.evaluation.multi_source_claim_verification import (
    verify_multi_source_relationship_claim,
)
from src.evaluation.validate_week25_benchmark import (
    BENCHMARK_PATH,
    validate_benchmark,
)
from src.governance.citation_verification import (
    verify_answer_citations,
)


OUTPUT_PATH = (
    ROOT
    / "outputs"
    / "week25_benchmark_baseline.json"
)


SUPPORTED = "SUPPORTED"
PASS = "PASS"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
ABSTAIN = "ABSTAIN"


def _load_benchmark() -> dict[str, Any]:
    """Load and validate the Week 25 golden benchmark."""

    with Path(BENCHMARK_PATH).open(
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


def _convert_evidence_for_citation_verifier(
    evidence_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Adapt benchmark evidence to the existing single-source verifier."""

    converted = []

    for item in evidence_items:
        converted.append(
            {
                "document_id": (
                    item[
                        "document_id"
                    ]
                ),
                "chunk_id": (
                    item[
                        "chunk_id"
                    ]
                ),
                "status": (
                    item[
                        "status"
                    ]
                ),
                "title": (
                    item[
                        "title"
                    ]
                ),
                "text": (
                    item[
                        "evidence_text"
                    ]
                ),
            }
        )

    return converted


def _convert_claims_for_citation_verifier(
    claims: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Adapt benchmark claims to the existing single-source verifier."""

    converted = []

    for claim in claims:
        converted.append(
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
                "citation": (
                    claim.get(
                        "citation"
                    )
                ),
            }
        )

    return converted


def _convert_evidence_for_precedence(
    evidence_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Adapt benchmark evidence to Evidence Precedence."""

    converted = []

    for item in evidence_items:
        converted.append(
            {
                "document_id": (
                    item[
                        "document_id"
                    ]
                ),
                "status": (
                    item[
                        "status"
                    ]
                ),
                "evidence_text": (
                    item[
                        "evidence_text"
                    ]
                ),
            }
        )

    return converted


def _expected_claim_statuses(
    case: dict[str, Any],
) -> dict[str, str]:
    """Return golden claim support statuses."""

    return {
        claim[
            "claim_id"
        ]: claim[
            "expected_support_status"
        ]
        for claim
        in case[
            "expected_claims"
        ]
    }


def _actual_claim_statuses(
    claim_results: list[dict[str, Any]],
) -> dict[str, str]:
    """Return evaluated claim support statuses."""

    return {
        claim_result[
            "claim_id"
        ]: claim_result[
            "status"
        ]
        for claim_result
        in claim_results
    }


def _compare_claim_statuses(
    expected: dict[str, str],
    actual: dict[str, str],
) -> tuple[
    bool,
    list[str],
]:
    """Compare golden and actual claim statuses."""

    failures = []

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
                f"Missing claim results: "
                f"{missing}"
            )

        if unexpected:
            failures.append(
                f"Unexpected claim results: "
                f"{unexpected}"
            )

        return (
            False,
            failures,
        )

    for claim_id in expected:
        expected_status = (
            expected[
                claim_id
            ]
        )

        actual_status = (
            actual[
                claim_id
            ]
        )

        if (
            expected_status
            != actual_status
        ):
            failures.append(
                f"{claim_id}: expected "
                f"{expected_status}, got "
                f"{actual_status}"
            )

    return (
        len(
            failures
        )
        == 0,
        failures,
    )


def _build_citation_to_evidence_lookup(
    case: dict[str, Any],
) -> dict[
    str,
    dict[str, Any],
]:
    """Resolve benchmark citation IDs to their evidence objects."""

    evidence_by_id = {
        evidence[
            "evidence_id"
        ]: evidence
        for evidence
        in case[
            "evidence_items"
        ]
    }

    lookup = {}

    for citation in case[
        "citation_index"
    ]:
        citation_id = citation[
            "citation_id"
        ]

        evidence_id = citation[
            "evidence_id"
        ]

        evidence = (
            evidence_by_id.get(
                evidence_id
            )
        )

        if evidence is None:
            continue

        lookup[
            citation_id
        ] = evidence

    return lookup


def _relationship_type_for_claim(
    case: dict[str, Any],
    claim: dict[str, Any],
) -> str | None:
    """Determine whether a claim is explicitly multi-source relational.

    Week 25 currently contains one relational golden case requiring
    joint verification: conflict evidence.

    The decision is based on explicit benchmark metadata rather than
    semantic guessing.
    """

    required_citations = (
        claim.get(
            "required_citation_ids",
            [],
        )
    )

    if len(
        required_citations
    ) < 2:
        return None

    benchmark_tags = {
        str(
            tag
        ).strip().lower()
        for tag
        in case.get(
            "benchmark_tags",
            [],
        )
    }

    if (
        case.get(
            "conflict_expected"
        )
        is True
        and "conflict"
        in benchmark_tags
    ):
        return "CONFLICT"

    return None


def _run_single_source_verification(
    case: dict[str, Any],
) -> dict[str, Any]:
    """Run the existing citation verifier unchanged."""

    evidence_for_verifier = (
        _convert_evidence_for_citation_verifier(
            case[
                "evidence_items"
            ]
        )
    )

    claims_for_verifier = (
        _convert_claims_for_citation_verifier(
            case[
                "expected_claims"
            ]
        )
    )

    return verify_answer_citations(
        claims_for_verifier,
        evidence_for_verifier,
    )


def _merge_multi_source_verification(
    case: dict[str, Any],
    precedence_result: dict[str, Any],
    verification_result: dict[str, Any],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    """Replace eligible single-source results with governed joint results.

    Ordinary claims keep the existing citation-verifier result.

    Claims explicitly requiring multiple approved citations and an explicit
    benchmark relationship are evaluated jointly through the Day 3
    multi-source verifier.
    """

    claim_results = [
        dict(
            result
        )
        for result
        in verification_result.get(
            "claim_results",
            [],
        )
    ]

    result_by_claim_id = {
        result[
            "claim_id"
        ]: result
        for result
        in claim_results
    }

    citation_to_evidence = (
        _build_citation_to_evidence_lookup(
            case
        )
    )

    multi_source_results = []

    for claim in case[
        "expected_claims"
    ]:
        relationship_type = (
            _relationship_type_for_claim(
                case,
                claim,
            )
        )

        if relationship_type is None:
            continue

        required_citation_ids = list(
            claim.get(
                "required_citation_ids",
                [],
            )
        )

        relational_claim = {
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
            claim[
                "claim_id"
            ]
        ] = joint_result

    ordered_results = []

    for claim in case[
        "expected_claims"
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
            raise ValueError(
                "Verification produced no result "
                f"for claim {claim_id}"
            )

        ordered_results.append(
            result
        )

    return (
        ordered_results,
        multi_source_results,
    )


def _derive_verification_decision(
    claim_results: list[dict[str, Any]],
    upstream_result: dict[str, Any],
) -> str:
    """Derive answer-level decision after joint verification.

    This preserves the existing fail-closed semantics:

    - no claims retains upstream ABSTAIN behaviour;
    - every claim SUPPORTED => PASS;
    - any other material support status => REVIEW_REQUIRED.
    """

    if not claim_results:
        return upstream_result[
            "decision"
        ]

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


def _run_case(
    case: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate one benchmark case through Week 25 hardened logic."""

    case_id = case[
        "case_id"
    ]

    precedence_input = (
        _convert_evidence_for_precedence(
            case[
                "evidence_items"
            ]
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
    ) = _merge_multi_source_verification(
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

    expected_verification = (
        case[
            "expected_verification_decision"
        ]
    )

    verification_matches = (
        expected_verification
        == actual_verification
    )

    expected_precedence = (
        case[
            "expected_precedence_decision"
        ]
    )

    actual_precedence = (
        precedence_result[
            "decision"
        ]
    )

    precedence_matches = (
        expected_precedence
        == actual_precedence
    )

    failure_reasons = []

    if not claim_statuses_match:
        failure_reasons.extend(
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

    baseline_match = (
        claim_statuses_match
        and verification_matches
        and precedence_matches
    )

    return {
        "case_id": case_id,
        "case_name": (
            case[
                "case_name"
            ]
        ),
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
        "multi_source_verification_used": bool(
            multi_source_results
        ),
        "multi_source_results": (
            multi_source_results
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
    """Summarise benchmark performance."""

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

    multi_source_cases = [
        result
        for result
        in results
        if result[
            "multi_source_verification_used"
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
        "multi_source_case_count": len(
            multi_source_cases
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
    """Run the Week 25 hardened benchmark."""

    benchmark = _load_benchmark()

    results = []

    for case in benchmark[
        "cases"
    ]:
        result = _run_case(
            case
        )

        results.append(
            result
        )

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
            "week25_day3_hardened_baseline"
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
        "Week 25 Day 3 Hardened Baseline"
    )

    print(
        "--------------------------------"
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
        "Multi-source cases evaluated: "
        f"{summary['multi_source_case_count']}"
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
        f"Output: "
        f"{OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()