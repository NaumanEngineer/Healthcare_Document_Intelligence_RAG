"""Week 28 — three-outcome governed end-to-end demo runner.

This runner demonstrates the existing governed Healthcare Document
Intelligence RAG application across three naturally occurring outcomes:

- ANSWER
- REVIEW_REQUIRED
- ABSTAIN

Expected outcomes are verification targets only.

They do not alter, override, or inject governance decisions.
"""

from __future__ import annotations

from copy import deepcopy

from src.application.observed_rag_pipeline import (
    run_observed_rag_pipeline,
)
from src.application.runtime_config import (
    RAGRuntimeConfig,
)
from src.application.week28_demo_data import (
    build_week28_demo_cases,
)
from src.application.week28_demo_dependencies import (
    load_week28_demo_dependencies,
    temporary_week28_document_registration,
)


QUERY_DATE = "2026-10-22"


def _run_case(
    case: dict,
) -> dict:
    """Run one synthetic Week 28 case through the canonical application."""

    case_id = case[
        "case_id"
    ]

    question = case[
        "question"
    ]

    expected_outcome = case[
        "expected_outcome"
    ]

    runtime_config = (
        RAGRuntimeConfig()
    )

    dependencies = (
        load_week28_demo_dependencies(
            runtime_config,
            case_id=case_id,
        )
    )

    with temporary_week28_document_registration(
        case_id
    ):
        result = run_observed_rag_pipeline(
            question=question,
            chunks=dependencies.chunks,
            embedded_chunks=(
                dependencies.embedded_chunks
            ),
            embedding_model=(
                dependencies.embedding_model
            ),
            embedding_model_name=(
                dependencies.embedding_model_name
            ),
            model_provider=(
                dependencies.model_provider
            ),
            query_date=QUERY_DATE,
            runtime_config=runtime_config,
        )

    actual_outcome = (
        result.get(
            "final_outcome"
        )
    )

    application_status = (
        result.get(
            "status"
        )
    )

    observability = (
        result.get(
            "observability",
            {},
        )
    )

    observability_status = (
        observability.get(
            "status"
        )
        if isinstance(
            observability,
            dict,
        )
        else None
    )

    events = (
        observability.get(
            "events",
            []
        )
        if isinstance(
            observability,
            dict,
        )
        else []
    )

    matched = (
        actual_outcome
        == expected_outcome
    )

    return {
        "case_id": case_id,
        "case_name": case[
            "case_name"
        ],
        "question": question,
        "expected_outcome": (
            expected_outcome
        ),
        "actual_outcome": (
            actual_outcome
        ),
        "matched": matched,
        "application_status": (
            application_status
        ),
        "observability_status": (
            observability_status
        ),
        "observed_event_count": (
            len(events)
        ),
        "result": deepcopy(
            result
        ),
    }


def run_week28_three_outcome_demo(
) -> dict:
    """Execute all Week 28 portfolio cases."""

    case_results = []

    for case in (
        build_week28_demo_cases()
    ):
        case_results.append(
            _run_case(
                case
            )
        )

    matched_count = sum(
        1
        for result in case_results
        if result[
            "matched"
        ]
    )

    return {
        "demo_name": (
            "Week 28 Three-Outcome "
            "Governed RAG Demo"
        ),
        "case_count": (
            len(case_results)
        ),
        "matched_case_count": (
            matched_count
        ),
        "all_cases_matched": (
            matched_count
            == len(case_results)
        ),
        "results": (
            case_results
        ),
    }


def _print_case_result(
    result: dict,
) -> None:
    print()
    print(
        result[
            "case_id"
        ]
    )

    print(
        "-" * len(
            result[
                "case_id"
            ]
        )
    )

    print(
        "Case:",
        result[
            "case_name"
        ],
    )

    print(
        "Question:",
        result[
            "question"
        ],
    )

    print(
        "Expected outcome:",
        result[
            "expected_outcome"
        ],
    )

    print(
        "Actual outcome:",
        result[
            "actual_outcome"
        ],
    )

    print(
        "Application status:",
        result[
            "application_status"
        ],
    )

    print(
        "Observability:",
        result[
            "observability_status"
        ],
    )

    print(
        "Observed events:",
        result[
            "observed_event_count"
        ],
    )

    print(
        "Verification:",
        (
            "PASS"
            if result[
                "matched"
            ]
            else "FAIL"
        ),
    )


def main() -> int:
    report = (
        run_week28_three_outcome_demo()
    )

    print(
        "Healthcare Document Intelligence RAG"
    )

    print(
        "Week 28 Three-Outcome Governed Demo"
    )

    print(
        "====================================="
    )

    for result in report[
        "results"
    ]:
        _print_case_result(
            result
        )

    print()
    print(
        "Summary"
    )

    print(
        "-------"
    )

    print(
        "Cases:",
        report[
            "case_count"
        ],
    )

    print(
        "Matched:",
        report[
            "matched_case_count"
        ],
    )

    print(
        "Overall verification:",
        (
            "PASS"
            if report[
                "all_cases_matched"
            ]
            else "FAIL"
        ),
    )

    return (
        0
        if report[
            "all_cases_matched"
        ]
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(
        main()
    )