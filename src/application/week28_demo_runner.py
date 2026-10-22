"""Week 28 — governed three-outcome portfolio demo runner.

The runner executes three synthetic, non-patient operational scenarios through
the canonical governed RAG application and then attaches the Week 28 Day 3
manager-facing presentation layer.

The presentation layer is downstream only.

It does not change retrieval, evidence, governance, assurance, or the final
application outcome.
"""

from __future__ import annotations

from copy import deepcopy

from src.application.manager_response import (
    build_manager_response,
)
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
    """Run one Week 28 demo case through the canonical application."""

    case_id = (
        case[
            "case_id"
        ]
    )

    question = (
        case[
            "question"
        ]
    )

    expected_outcome = (
        case[
            "expected_outcome"
        ]
    )

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
        result = (
            run_observed_rag_pipeline(
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
        )

    governed_snapshot = (
        deepcopy(
            result
        )
    )

    manager_response = (
        build_manager_response(
            result
        )
    )

    if result != governed_snapshot:
        raise ValueError(
            "Manager presentation changed the governed result."
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

    presentation_outcome_matches = (
        manager_response.get(
            "outcome"
        )
        == actual_outcome
    )

    authority_preserved = (
        manager_response.get(
            "authority_preserved"
        )
        is True
    )

    return {
        "case_id": case_id,
        "case_name": (
            case[
                "case_name"
            ]
        ),
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
            len(
                events
            )
        ),
        "manager_response": (
            manager_response
        ),
        "presentation_outcome_matches": (
            presentation_outcome_matches
        ),
        "authority_preserved": (
            authority_preserved
        ),
        "result": deepcopy(
            result
        ),
    }


def run_week28_three_outcome_demo(
) -> dict:
    """Execute all Week 28 governed portfolio scenarios."""

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

    presentation_match_count = sum(
        1
        for result in case_results
        if result[
            "presentation_outcome_matches"
        ]
    )

    authority_preserved_count = sum(
        1
        for result in case_results
        if result[
            "authority_preserved"
        ]
    )

    case_count = (
        len(
            case_results
        )
    )

    return {
        "demo_name": (
            "Week 28 Three-Outcome "
            "Governed RAG Demo"
        ),
        "case_count": (
            case_count
        ),
        "matched_case_count": (
            matched_count
        ),
        "presentation_match_count": (
            presentation_match_count
        ),
        "authority_preserved_count": (
            authority_preserved_count
        ),
        "all_cases_matched": (
            matched_count
            == case_count
        ),
        "all_presentations_matched": (
            presentation_match_count
            == case_count
        ),
        "all_authority_preserved": (
            authority_preserved_count
            == case_count
        ),
        "results": (
            case_results
        ),
    }


def _print_manager_response(
    manager_response: dict,
) -> None:
    """Print safe manager-facing presentation fields."""

    print()
    print(
        "Manager-facing response"
    )

    print(
        "-----------------------"
    )

    print(
        "Headline:",
        manager_response[
            "headline"
        ],
    )

    print(
        "Summary:",
        manager_response[
            "summary"
        ],
    )

    print(
        "Evidence basis:",
        manager_response[
            "evidence_basis"
        ],
    )

    print(
        "Confidence:",
        manager_response[
            "confidence_message"
        ],
    )

    print(
        "Next action:",
        manager_response[
            "next_action"
        ],
    )

    print(
        "Human review required:",
        manager_response[
            "human_review_required"
        ],
    )

    print(
        "Citation count:",
        len(
            manager_response[
                "citations"
            ]
        ),
    )

    print(
        "Authority preserved:",
        manager_response[
            "authority_preserved"
        ],
    )


def _print_case_result(
    result: dict,
) -> None:
    """Print one portfolio scenario."""

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
        "Governance verification:",
        (
            "PASS"
            if result[
                "matched"
            ]
            else "FAIL"
        ),
    )

    print(
        "Presentation verification:",
        (
            "PASS"
            if result[
                "presentation_outcome_matches"
            ]
            else "FAIL"
        ),
    )

    _print_manager_response(
        result[
            "manager_response"
        ]
    )


def main() -> int:
    """Run the complete Week 28 portfolio demonstration."""

    report = (
        run_week28_three_outcome_demo()
    )

    print(
        "Healthcare Document Intelligence RAG"
    )

    print(
        "Week 28 Governed Manager-Facing Demo"
    )

    print(
        "===================================="
    )

    for result in (
        report[
            "results"
        ]
    ):
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
        "Governance matched:",
        report[
            "matched_case_count"
        ],
    )

    print(
        "Presentation matched:",
        report[
            "presentation_match_count"
        ],
    )

    print(
        "Authority preserved:",
        report[
            "authority_preserved_count"
        ],
    )

    overall_pass = (
        report[
            "all_cases_matched"
        ]
        and report[
            "all_presentations_matched"
        ]
        and report[
            "all_authority_preserved"
        ]
    )

    print(
        "Overall verification:",
        (
            "PASS"
            if overall_pass
            else "FAIL"
        ),
    )

    return (
        0
        if overall_pass
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(
        main()
    )