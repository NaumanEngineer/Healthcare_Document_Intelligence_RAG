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

OUTPUT_PATH = (
    ROOT
    / "outputs"
    / "week19_citation_evaluation.json"
)


def main() -> None:
    with INPUT_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        cases = json.load(file)

    results = []

    correct = 0
    false_acceptances = 0
    false_rejections = 0

    print()
    print("WEEK 19 CITATION VERIFICATION EVALUATION")
    print("=" * 60)
    print(f"Evaluation cases: {len(cases)}")
    print()

    for case in cases:
        verification = verify_answer_citations(
            case["claims"],
            case["evidence_items"],
        )

        actual = verification["decision"]
        expected = case["expected_decision"]

        passed = actual == expected

        if passed:
            correct += 1

        # Unsafe answer accepted when review was expected.
        if (
            expected != "PASS"
            and actual == "PASS"
        ):
            false_acceptances += 1

        # Grounded answer rejected when PASS was expected.
        if (
            expected == "PASS"
            and actual != "PASS"
        ):
            false_rejections += 1

        result = {
            "case_id": case["case_id"],
            "category": case["category"],
            "expected_decision": expected,
            "actual_decision": actual,
            "correct": passed,
            "verification": verification,
        }

        results.append(result)

        marker = "PASS" if passed else "FAIL"

        print(
            f"{case['case_id']} "
            f"[{case['category']}]"
        )
        print(
            f"  Expected: {expected}"
        )
        print(
            f"  Actual:   {actual}"
        )
        print(
            f"  Result:   {marker}"
        )

        for claim_result in verification[
            "claim_results"
        ]:
            print(
                "  "
                f"{claim_result['claim_id']}: "
                f"{claim_result['status']} "
                f"(support={claim_result['support_ratio']})"
            )

        print()

    total = len(cases)

    accuracy = (
        correct / total
        if total
        else 0.0
    )

    summary = {
        "total_cases": total,
        "correct_cases": correct,
        "accuracy": accuracy,
        "false_acceptances": false_acceptances,
        "false_rejections": false_rejections,
    }

    output = {
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
        )

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(
        f"Correct: {correct}/{total}"
    )
    print(
        f"Accuracy: {accuracy:.1%}"
    )
    print(
        f"False acceptances: {false_acceptances}"
    )
    print(
        f"False rejections: {false_rejections}"
    )
    print()
    print(
        f"Saved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()