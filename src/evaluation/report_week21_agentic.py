"""Case-level comparison for Week 21 Day 2 bounded agentic retrieval."""

from __future__ import annotations

import json
from pathlib import Path

from src.evaluation import run_week18_benchmark as baseline


BENCHMARK_PATH = (
    baseline.PROJECT_ROOT
    / "outputs"
    / "week21_day2_agentic_benchmark.json"
)


def success(record: dict, method: str, metric: str) -> bool:
    return bool(
        record.get(
            method,
            {},
        ).get(
            metric,
            False,
        )
    )


def differing_cases(
    records: list[dict],
    left: str,
    right: str,
    metric: str,
) -> tuple[list[str], list[str]]:
    """Return cases where left wins and where right wins."""

    left_wins = []
    right_wins = []

    for record in records:
        left_success = success(
            record,
            left,
            metric,
        )

        right_success = success(
            record,
            right,
            metric,
        )

        if left_success and not right_success:
            left_wins.append(
                record["query_id"]
            )

        elif right_success and not left_success:
            right_wins.append(
                record["query_id"]
            )

    return (
        left_wins,
        right_wins,
    )


def main():
    data = json.loads(
        BENCHMARK_PATH.read_text(
            encoding="utf-8",
        )
    )

    records = data[
        "case_results"
    ]

    comparisons = [
        (
            "hybrid_agentic",
            "hybrid",
        ),
        (
            "hybrid_agentic",
            "hybrid_rescue",
        ),
        (
            "hybrid_agentic",
            "hybrid_reranker",
        ),
    ]

    print(
        "=" * 80
    )
    print(
        "WEEK 21 DAY 2 AGENTIC CASE ANALYSIS"
    )
    print(
        "=" * 80
    )

    for left, right in comparisons:
        print()
        print(
            f"{left} vs {right}"
        )

        for metric in (
            "top1_success",
            "topk_success",
        ):
            left_wins, right_wins = (
                differing_cases(
                    records,
                    left,
                    right,
                    metric,
                )
            )

            print(
                f"  {metric}"
            )

            print(
                f"    {left} wins:",
                left_wins,
            )

            print(
                f"    {right} wins:",
                right_wins,
            )

    print()
    print(
        "AGENTIC RETRIEVAL AUDIT CASES"
    )

    for record in records:
        audit = record.get(
            "hybrid_agentic_audit"
        )

        if not audit:
            continue

        calls = audit.get(
            "retrieval_call_count",
            0,
        )

        if calls == 2:
            print()
            print(
                record["query_id"]
            )
            print(
                "  stop:",
                audit.get(
                    "stop_reason"
                ),
            )
            print(
                "  calls:",
                calls,
            )

            rounds = audit.get(
                "rounds",
                [],
            )

            if len(rounds) >= 2:
                print(
                    "  refined query:",
                    rounds[1].get(
                        "query"
                    ),
                )
                print(
                    "  accepted:",
                    rounds[1].get(
                        "accepted_chunk_ids"
                    ),
                )
                print(
                    "  replaced:",
                    rounds[1].get(
                        "replaced_chunk_ids"
                    ),
                )


if __name__ == "__main__":
    main()