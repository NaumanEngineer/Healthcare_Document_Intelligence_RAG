from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from src.governance.review_decision import (
    ABSTAIN,
    AUTO_ANSWER,
    REVIEW_REQUIRED,
    decide_review_outcome,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

BENCHMARK_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "week18_retrieval_benchmark.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "week18_review_decision_audit.json"
)


def load_benchmark() -> dict:
    """
    Load the completed Week 18 retrieval benchmark.
    """

    if not BENCHMARK_FILE.exists():
        raise FileNotFoundError(
            "Benchmark file not found: "
            f"{BENCHMARK_FILE}"
        )

    with BENCHMARK_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise TypeError(
            "Benchmark output must be a JSON object."
        )

    return data


def run_review_audit() -> dict:
    """
    Apply the Day 5 human-review decision policy
    to every Week 18 benchmark case.

    Hybrid retrieval evidence is used for the audit.
    """

    benchmark = load_benchmark()

    case_results = benchmark.get(
        "case_results",
        [],
    )

    if not case_results:
        raise ValueError(
            "Benchmark contains no case results."
        )

    audited_cases: list[dict] = []

    decisions: list[str] = []

    print()
    print(
        "WEEK 18 HUMAN-REVIEW DECISION AUDIT"
    )
    print(
        "=" * 65
    )
    print()

    for case in case_results:
        query_id = case.get(
            "query_id",
            "UNKNOWN",
        )

        question = case.get(
            "question",
            "",
        )

        scope_assessment = case.get(
            "scope_assessment",
            {
                "allowed": False,
            },
        )

        raw_results = case.get(
            "raw_results",
            {},
        )

        hybrid_results = raw_results.get(
            "hybrid",
            [],
        )

        decision = decide_review_outcome(
            question=question,
            scope_assessment=scope_assessment,
            results=hybrid_results,
        )

        decision_name = decision[
            "decision"
        ]

        decisions.append(
            decision_name
        )

        audited_case = {
            "query_id": query_id,
            "question": question,
            "scope": scope_assessment.get(
                "scope"
            ),
            "decision": decision_name,
            "reason": decision.get(
                "reason"
            ),
            "requires_human_review": (
                decision.get(
                    "requires_human_review"
                )
            ),
            "may_generate_answer": (
                decision.get(
                    "may_generate_answer"
                )
            ),
            "document_ids": (
                decision.get(
                    "document_ids",
                    [],
                )
            ),
        }

        audited_cases.append(
            audited_case
        )

        print(
            f"{query_id} - {question}"
        )

        print(
            "  Scope:    "
            f"{scope_assessment.get('scope')}"
        )

        print(
            "  Decision: "
            f"{decision_name}"
        )

        print(
            "  Docs:     "
            f"{decision.get('document_ids', [])}"
        )

        print(
            "  Reason:   "
            f"{decision.get('reason')}"
        )

        print()

    counts = Counter(
        decisions
    )

    total_cases = len(
        audited_cases
    )

    summary = {
        "total_cases": total_cases,
        "auto_answer": counts.get(
            AUTO_ANSWER,
            0,
        ),
        "review_required": counts.get(
            REVIEW_REQUIRED,
            0,
        ),
        "abstain": counts.get(
            ABSTAIN,
            0,
        ),
    }

    output = {
        "experiment": (
            "week18_human_review_decision_audit"
        ),
        "retrieval_method": "hybrid",
        "summary": summary,
        "cases": audited_cases,
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
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
        "=" * 65
    )

    print(
        "DECISION SUMMARY"
    )

    print(
        "=" * 65
    )

    print(
        f"Total cases:      {total_cases}"
    )

    print(
        "AUTO_ANSWER:      "
        f"{summary['auto_answer']}"
    )

    print(
        "REVIEW_REQUIRED:  "
        f"{summary['review_required']}"
    )

    print(
        "ABSTAIN:          "
        f"{summary['abstain']}"
    )

    print()

    print(
        "Audit saved to:"
    )

    print(
        OUTPUT_FILE
    )

    return output


if __name__ == "__main__":
    run_review_audit()