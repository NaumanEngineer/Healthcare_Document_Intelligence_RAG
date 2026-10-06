from __future__ import annotations

import json
from pathlib import Path

from src.evaluation import run_week18_benchmark as baseline


OUTPUT_FILE = (
    baseline.PROJECT_ROOT
    / "outputs"
    / "week21_day3_relationship_benchmark.json"
)


def _success(
    record: dict,
    method: str,
    field: str,
) -> bool:
    return bool(
        record[
            method
        ].get(
            field,
            False,
        )
    )


def main():
    payload = json.loads(
        OUTPUT_FILE.read_text(
            encoding="utf-8",
        )
    )

    records = payload[
        "case_results"
    ]

    expanded_cases = []

    top1_wins = []
    top1_losses = []

    topk_wins = []
    topk_losses = []

    evidence_decision_changes = []

    for record in records:
        query_id = record[
            "query_id"
        ]

        question = record[
            "question"
        ]

        audit = record.get(
            "hybrid_relationship_aware_audit"
        )

        if audit:
            expansion = audit[
                "relationship_expansion"
            ]

            if (
                expansion[
                    "expansion_count"
                ]
                > 0
            ):
                expanded_cases.append(
                    {
                        "query_id": query_id,
                        "question": question,
                        "stop_reason": (
                            expansion[
                                "stop_reason"
                            ]
                        ),
                        "relationship_records": (
                            expansion[
                                "relationship_records"
                            ]
                        ),
                        "relationship_evidence_candidate_ids": (
                            expansion[
                                "relationship_evidence_candidate_ids"
                            ]
                        ),
                        "related_candidate_ids": (
                            expansion[
                                "related_candidate_ids"
                            ]
                        ),
                        "accepted_chunk_ids": (
                            expansion[
                                "accepted_chunk_ids"
                            ]
                        ),
                    }
                )

        hybrid_top1 = _success(
            record,
            "hybrid",
            "top1_success",
        )

        relationship_top1 = _success(
            record,
            "hybrid_relationship_aware",
            "top1_success",
        )

        if (
            relationship_top1
            and not hybrid_top1
        ):
            top1_wins.append(
                query_id
            )

        if (
            hybrid_top1
            and not relationship_top1
        ):
            top1_losses.append(
                query_id
            )

        hybrid_topk = _success(
            record,
            "hybrid",
            "topk_success",
        )

        relationship_topk = _success(
            record,
            "hybrid_relationship_aware",
            "topk_success",
        )

        if (
            relationship_topk
            and not hybrid_topk
        ):
            topk_wins.append(
                query_id
            )

        if (
            hybrid_topk
            and not relationship_topk
        ):
            topk_losses.append(
                query_id
            )

        hybrid_assessment = record[
            "evidence_sufficiency"
        ][
            "hybrid"
        ]

        relationship_assessment = record[
            "evidence_sufficiency"
        ][
            "hybrid_relationship_aware"
        ]

        hybrid_decision = (
            hybrid_assessment.get(
                "decision"
            )
            if hybrid_assessment
            else None
        )

        relationship_decision = (
            relationship_assessment.get(
                "decision"
            )
            if relationship_assessment
            else None
        )

        if (
            hybrid_decision
            != relationship_decision
        ):
            evidence_decision_changes.append(
                {
                    "query_id": query_id,
                    "question": question,
                    "hybrid_decision": (
                        hybrid_decision
                    ),
                    "relationship_decision": (
                        relationship_decision
                    ),
                }
            )

    print(
        "=" * 80
    )
    print(
        "EXPANDED CASES"
    )
    print(
        "=" * 80
    )

    for item in expanded_cases:
        print()
        print(
            item[
                "query_id"
            ],
            "|",
            item[
                "question"
            ],
        )

        print(
            "  evidence candidates:",
            item[
                "relationship_evidence_candidate_ids"
            ],
        )

        print(
            "  related candidates:",
            item[
                "related_candidate_ids"
            ],
        )

        print(
            "  accepted:",
            item[
                "accepted_chunk_ids"
            ],
        )

    print()
    print(
        "=" * 80
    )
    print(
        "CASE-LEVEL RETRIEVAL CHANGES"
    )
    print(
        "=" * 80
    )

    print(
        "Top1 wins:",
        top1_wins,
    )

    print(
        "Top1 losses:",
        top1_losses,
    )

    print(
        "Top-k wins:",
        topk_wins,
    )

    print(
        "Top-k losses:",
        topk_losses,
    )

    print()
    print(
        "=" * 80
    )
    print(
        "EVIDENCE SUFFICIENCY DECISION CHANGES"
    )
    print(
        "=" * 80
    )

    if not evidence_decision_changes:
        print(
            "None"
        )

    for change in evidence_decision_changes:
        print(
            change
        )

    print()
    print(
        "Expanded case count:",
        len(
            expanded_cases
        ),
    )


if __name__ == "__main__":
    main()