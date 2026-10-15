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
from src.governance.citation_verification import (
    verify_answer_citations,
)
from src.evaluation.validate_week25_benchmark import (
    BENCHMARK_PATH,
    validate_benchmark,
)


OUTPUT_PATH = (
    ROOT
    / "outputs"
    / "week25_benchmark_baseline.json"
)


def _load_benchmark() -> dict[str, Any]:
    with Path(BENCHMARK_PATH).open(
        "r",
        encoding="utf-8",
    ) as file:
        benchmark = json.load(file)

    validate_benchmark(
        benchmark
    )

    return benchmark


def _convert_evidence_for_citation_verifier(
    evidence_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    converted = []

    for item in evidence_items:
        converted.append(
            {
                "document_id": item["document_id"],
                "chunk_id": item["chunk_id"],
                "status": item["status"],
                "title": item["title"],
                "text": item["evidence_text"],
            }
        )

    return converted


def _convert_claims_for_citation_verifier(
    claims: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    converted = []

    for claim in claims:
        converted.append(
            {
                "claim_id": claim["claim_id"],
                "claim_text": claim["claim_text"],
                "citation": claim["citation"],
            }
        )

    return converted


def _convert_evidence_for_precedence(
    evidence_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    converted = []

    for item in evidence_items:
        converted.append(
            {
                "document_id": item["document_id"],
                "status": item["status"],
                "evidence_text": item["evidence_text"],
            }
        )

    return converted


def _expected_claim_statuses(
    case: dict[str, Any],
) -> dict[str, str]:
    return {
        claim["claim_id"]: claim[
            "expected_support_status"
        ]
        for claim in case[
            "expected_claims"
        ]
    }


def _actual_claim_statuses(
    verification_result: dict[str, Any],
) -> dict[str, str]:
    return {
        claim_result["claim_id"]: claim_result[
            "status"
        ]
        for claim_result in verification_result[
            "claim_results"
        ]
    }


def _compare_claim_statuses(
    expected: dict[str, str],
    actual: dict[str, str],
) -> tuple[bool, list[str]]:
    failures = []

    if set(expected) != set(actual):
        missing = sorted(
            set(expected)
            - set(actual)
        )

        unexpected = sorted(
            set(actual)
            - set(expected)
        )

        if missing:
            failures.append(
                f"Missing claim results: {missing}"
            )

        if unexpected:
            failures.append(
                f"Unexpected claim results: {unexpected}"
            )

        return False, failures

    for claim_id in expected:
        expected_status = expected[
            claim_id
        ]

        actual_status = actual[
            claim_id
        ]

        if expected_status != actual_status:
            failures.append(
                f"{claim_id}: expected "
                f"{expected_status}, got "
                f"{actual_status}"
            )

    return (
        len(failures) == 0,
        failures,
    )


def _run_case(
    case: dict[str, Any],
) -> dict[str, Any]:
    case_id = case["case_id"]

    evidence_for_verifier = (
        _convert_evidence_for_citation_verifier(
            case["evidence_items"]
        )
    )

    claims_for_verifier = (
        _convert_claims_for_citation_verifier(
            case["expected_claims"]
        )
    )

    verification_result = (
        verify_answer_citations(
            claims_for_verifier,
            evidence_for_verifier,
        )
    )

    precedence_input = (
        _convert_evidence_for_precedence(
            case["evidence_items"]
        )
    )

    precedence_result = (
        assess_evidence_precedence(
            precedence_input
        )
    )

    expected_claim_statuses = (
        _expected_claim_statuses(
            case
        )
    )

    actual_claim_statuses = (
        _actual_claim_statuses(
            verification_result
        )
    )

    (
        claim_statuses_match,
        claim_failures,
    ) = _compare_claim_statuses(
        expected_claim_statuses,
        actual_claim_statuses,
    )

    expected_verification = case[
        "expected_verification_decision"
    ]

    actual_verification = (
        verification_result[
            "decision"
        ]
    )

    verification_matches = (
        expected_verification
        == actual_verification
    )

    expected_precedence = case[
        "expected_precedence_decision"
    ]

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
        "case_name": case["case_name"],
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
        "baseline_match": baseline_match,
        "failure_reasons": failure_reasons,
    }


def _summarise(
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    matched = [
        result
        for result in results
        if result[
            "baseline_match"
        ]
    ]

    mismatched = [
        result
        for result in results
        if not result[
            "baseline_match"
        ]
    ]

    return {
        "case_count": len(results),
        "matched_case_count": len(matched),
        "mismatched_case_count": len(
            mismatched
        ),
        "match_rate": round(
            len(matched)
            / len(results),
            4,
        )
        if results
        else 0.0,
        "mismatched_case_ids": [
            result["case_id"]
            for result in mismatched
        ],
    }


def main() -> None:
    benchmark = _load_benchmark()

    results = []

    for case in benchmark["cases"]:
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
        "benchmark_name": benchmark[
            "benchmark_name"
        ],
        "benchmark_version": benchmark[
            "benchmark_version"
        ],
        "evaluation_type": (
            "existing_logic_baseline"
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
        "Week 25 Existing Logic Baseline"
    )
    print(
        "-------------------------------"
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