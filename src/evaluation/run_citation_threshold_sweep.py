from __future__ import annotations

import json
from pathlib import Path

from src.governance.citation_verification import verify_answer_citations


ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    ROOT
    / "data"
    / "synthetic"
    / "citation_evaluation_cases.json"
)


THRESHOLDS = [
    0.40,
    0.45,
    0.50,
    0.55,
    0.60,
    0.65,
    0.70,
    0.75,
    0.80,
]


def evaluate_threshold(
    cases: list[dict],
    threshold: float,
) -> dict:
    correct = 0
    false_acceptances = 0
    false_rejections = 0

    failed_cases = []

    for case in cases:
        result = verify_answer_citations(
            case["claims"],
            case["evidence_items"],
            support_threshold=threshold,
        )

        actual = result["decision"]
        expected = case["expected_decision"]

        is_correct = actual == expected

        if is_correct:
            correct += 1
        else:
            failed_cases.append(
                {
                    "case_id": case["case_id"],
                    "category": case["category"],
                    "expected": expected,
                    "actual": actual,
                }
            )

        if (
            expected != "PASS"
            and actual == "PASS"
        ):
            false_acceptances += 1

        if (
            expected == "PASS"
            and actual != "PASS"
        ):
            false_rejections += 1

    total = len(cases)

    return {
        "threshold": threshold,
        "correct": correct,
        "total": total,
        "accuracy": correct / total if total else 0.0,
        "false_acceptances": false_acceptances,
        "false_rejections": false_rejections,
        "failed_cases": failed_cases,
    }


def main() -> None:
    with INPUT_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        cases = json.load(file)

    print()
    print("WEEK 19 CITATION THRESHOLD SWEEP")
    print("=" * 72)
    print(
        "Threshold | Correct | Accuracy | False Accept | False Reject"
    )
    print("-" * 72)

    all_results = []

    for threshold in THRESHOLDS:
        result = evaluate_threshold(
            cases,
            threshold,
        )

        all_results.append(result)

        print(
            f"{threshold:>9.2f} | "
            f"{result['correct']:>7}/{result['total']:<2} | "
            f"{result['accuracy']:>7.1%} | "
            f"{result['false_acceptances']:>12} | "
            f"{result['false_rejections']:>12}"
        )

    print()
    print("=" * 72)
    print("FAILURE DETAILS")
    print("=" * 72)

    for result in all_results:
        print()
        print(
            f"Threshold {result['threshold']:.2f}"
        )

        if not result["failed_cases"]:
            print("  No failures.")
            continue

        for failure in result["failed_cases"]:
            print(
                f"  {failure['case_id']} "
                f"[{failure['category']}] "
                f"expected={failure['expected']} "
                f"actual={failure['actual']}"
            )


if __name__ == "__main__":
    main()