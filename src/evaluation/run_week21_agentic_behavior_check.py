from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter

import src.evaluation.run_week18_benchmark as baseline

from src.retrieval.bounded_agentic_retrieval import (
    bounded_agentic_retrieval,
)
from src.retrieval.query_scope import (
    assess_query_scope,
)


OUTPUT_PATH = (
    baseline.PROJECT_ROOT
    / "outputs"
    / "week21_day2_agentic_behavior_check.json"
)


def case_id(case: dict, index: int) -> str:
    """Return a stable case identifier without assuming one exact key."""

    for key in (
        "case_id",
        "id",
        "question_id",
        "evaluation_id",
    ):
        value = case.get(key)

        if isinstance(value, str) and value.strip():
            return value

    return f"CASE-{index:03d}"


def case_question(case: dict) -> str:
    """Return the case question."""

    question = case.get("question")

    if not isinstance(question, str) or not question.strip():
        raise ValueError(
            "evaluation case does not contain a valid question"
        )

    return question


def expected_document_ids(case: dict) -> list[str]:
    """Read expected document IDs defensively."""

    for key in (
        "expected_document_ids",
        "relevant_document_ids",
        "expected_documents",
    ):
        value = case.get(key)

        if isinstance(value, list):
            return [
                item
                for item in value
                if isinstance(item, str)
            ]

    expected_single = case.get(
        "expected_document_id"
    )

    if isinstance(expected_single, str):
        return [
            expected_single
        ]

    return []


def result_summary(results: list[dict]) -> list[dict]:
    """Return compact evidence information for inspection."""

    summary = []

    for result in results:
        summary.append(
            {
                "chunk_id": result.get(
                    "chunk_id"
                ),
                "document_id": result.get(
                    "document_id"
                ),
                "status": result.get(
                    "status"
                ),
                "rank": result.get(
                    "rank"
                ),
            }
        )

    return summary


def classify_refined_query(
    original_query: str,
    refined_query: str | None,
) -> str:
    """Apply a simple inspection label.

    This is descriptive only and does not affect retrieval.
    """

    if refined_query is None:
        return "not_generated"

    original = " ".join(
        original_query.lower().split()
    )

    refined = " ".join(
        refined_query.lower().split()
    )

    if refined == original:
        return "duplicate"

    if not refined.startswith(original):
        return "possible_query_drift"

    if len(refined) > (
        len(original) + 120
    ):
        return "potentially_overlong"

    return "context_preserved"


def run_behavior_check() -> dict:
    print(
        "Loading frozen evaluation cases..."
    )

    cases = baseline.load_evaluation_cases()

    print(
        f"Evaluation cases: {len(cases)}"
    )

    print(
        "Building benchmark corpus..."
    )

    chunks = baseline.build_benchmark_corpus()

    print(
        f"Corpus chunks: {len(chunks)}"
    )

    print(
        "Loading embedding model..."
    )

    model = baseline.load_embedding_model()

    model_identifier = (
        baseline.get_model_identifier(
            model
        )
    )

    print(
        f"Embedding model: {model_identifier}"
    )

    print(
        "Embedding corpus..."
    )

    embedded_chunks = baseline.embed_chunks(
        chunks=chunks,
        model=model,
        model_name=model_identifier,
    )

    print(
        f"Embedded chunks: {len(embedded_chunks)}"
    )

    semantic_k = getattr(
        baseline,
        "SEMANTIC_K",
        10,
    )

    keyword_k = getattr(
        baseline,
        "KEYWORD_K",
        10,
    )

    final_k = getattr(
        baseline,
        "FINAL_K",
        3,
    )

    semantic_min_similarity = getattr(
        baseline,
        "SEMANTIC_MIN_SIMILARITY",
        None,
    )

    keyword_min_score = getattr(
        baseline,
        "KEYWORD_MIN_SCORE",
        None,
    )

    min_rrf_score = getattr(
        baseline,
        "MIN_RRF_SCORE",
        None,
    )

    rrf_k = getattr(
        baseline,
        "RRF_K",
        60,
    )

    records = []

    one_round_times = []
    two_round_times = []

    print()
    print(
        "Running bounded agentic retrieval..."
    )

    for index, case in enumerate(
        cases,
        start=1,
    ):
        question = case_question(
            case
        )

        identifier = case_id(
            case,
            index,
        )

        scope = assess_query_scope(
            question
        )

        started = perf_counter()

        result = bounded_agentic_retrieval(
            query=question,
            chunks=chunks,
            embedded_chunks=embedded_chunks,
            model=model,
            embedding_model=model_identifier,
            semantic_k=semantic_k,
            keyword_k=keyword_k,
            final_k=final_k,
            semantic_min_similarity=(
                semantic_min_similarity
            ),
            keyword_min_score=(
                keyword_min_score
            ),
            min_rrf_score=min_rrf_score,
            rrf_k=rrf_k,
            max_rounds=2,
        )

        elapsed = (
            perf_counter()
            - started
        )

        audit = result[
            "audit"
        ]

        rounds = audit.get(
            "rounds",
            [],
        )

        retrieval_call_count = (
            audit.get(
                "retrieval_call_count",
                0,
            )
        )

        if retrieval_call_count == 1:
            one_round_times.append(
                elapsed
            )

        elif retrieval_call_count == 2:
            two_round_times.append(
                elapsed
            )

        refined_query = None

        if len(rounds) >= 2:
            refined_query = (
                rounds[1].get(
                    "query"
                )
            )

        final_results = result.get(
            "results",
            [],
        )

        record = {
            "case_id": identifier,
            "question": question,
            "scope": scope,
            "expected_document_ids": (
                expected_document_ids(
                    case
                )
            ),
            "result_summary": (
                result_summary(
                    final_results
                )
            ),
            "all_final_active": all(
                item.get("status")
                == "Active"
                for item in final_results
            ),
            "final_result_count": len(
                final_results
            ),
            "final_k": final_k,
            "retrieval_call_count": (
                retrieval_call_count
            ),
            "stop_reason": audit.get(
                "stop_reason"
            ),
            "initial_evidence": audit.get(
                "initial_evidence"
            ),
            "final_evidence": audit.get(
                "final_evidence"
            ),
            "rounds": rounds,
            "refined_query": (
                refined_query
            ),
            "refined_query_classification": (
                classify_refined_query(
                    question,
                    refined_query,
                )
            ),
            "elapsed_seconds": elapsed,
        }

        records.append(
            record
        )

        print(
            f"{identifier}: "
            f"calls={retrieval_call_count}, "
            f"stop={audit.get('stop_reason')}, "
            f"time={elapsed:.3f}s"
        )

    stop_reason_counts = {}

    for record in records:
        reason = record[
            "stop_reason"
        ]

        stop_reason_counts[
            reason
        ] = (
            stop_reason_counts.get(
                reason,
                0,
            )
            + 1
        )

    refined_records = [
        record
        for record in records
        if record[
            "retrieval_call_count"
        ] == 2
    ]

    improved_records = [
        record
        for record in refined_records
        if (
            record.get(
                "initial_evidence"
            )
            and record.get(
                "final_evidence"
            )
            and len(
                record[
                    "final_evidence"
                ].get(
                    "matched_query_terms",
                    [],
                )
            )
            >
            len(
                record[
                    "initial_evidence"
                ].get(
                    "matched_query_terms",
                    [],
                )
            )
        )
    ]

    sufficient_after_refinement = [
        record
        for record in records
        if record[
            "stop_reason"
        ]
        == (
            "EVIDENCE_SUFFICIENT_AFTER_REFINEMENT"
        )
    ]

    hard_blocked = [
        record
        for record in records
        if record[
            "stop_reason"
        ] == "NO_RECOVERABLE_GAP"
    ]

    no_improvement = [
        record
        for record in records
        if record[
            "stop_reason"
        ] == "NO_COVERAGE_IMPROVEMENT"
    ]

    multi_document = [
        record
        for record in records
        if len(
            record[
                "expected_document_ids"
            ]
        ) > 1
    ]

    unsafe_lifecycle = [
        record
        for record in records
        if not record[
            "all_final_active"
        ]
    ]

    oversized = [
        record
        for record in records
        if record[
            "final_result_count"
        ] > final_k
    ]

    query_drift = [
        record
        for record in records
        if record[
            "refined_query_classification"
        ] == "possible_query_drift"
    ]

    def average(
        values: list[float],
    ) -> float | None:
        if not values:
            return None

        return sum(
            values
        ) / len(
            values
        )

    output = {
        "case_count": len(
            records
        ),
        "configuration": {
            "semantic_k": semantic_k,
            "keyword_k": keyword_k,
            "final_k": final_k,
            "semantic_min_similarity": (
                semantic_min_similarity
            ),
            "keyword_min_score": (
                keyword_min_score
            ),
            "min_rrf_score": (
                min_rrf_score
            ),
            "rrf_k": rrf_k,
            "max_rounds": 2,
            "embedding_model": (
                model_identifier
            ),
        },
        "summary": {
            "stop_reason_counts": (
                stop_reason_counts
            ),
            "two_round_case_count": len(
                refined_records
            ),
            "coverage_improved_case_count": len(
                improved_records
            ),
            "sufficient_after_refinement_count": len(
                sufficient_after_refinement
            ),
            "no_recoverable_gap_count": len(
                hard_blocked
            ),
            "no_coverage_improvement_count": len(
                no_improvement
            ),
            "multi_document_case_count": len(
                multi_document
            ),
            "unsafe_lifecycle_count": len(
                unsafe_lifecycle
            ),
            "oversized_final_set_count": len(
                oversized
            ),
            "possible_query_drift_count": len(
                query_drift
            ),
            "mean_one_round_seconds": average(
                one_round_times
            ),
            "mean_two_round_seconds": average(
                two_round_times
            ),
        },
        "representative_cases": {
            "initial_sufficient": (
                next(
                    (
                        record
                        for record in records
                        if record[
                            "stop_reason"
                        ]
                        == (
                            "INITIAL_EVIDENCE_SUFFICIENT"
                        )
                    ),
                    None,
                )
            ),
            "sufficient_after_refinement": (
                sufficient_after_refinement[
                    0
                ]
                if sufficient_after_refinement
                else None
            ),
            "coverage_improved": (
                improved_records[0]
                if improved_records
                else None
            ),
            "no_recoverable_gap": (
                hard_blocked[0]
                if hard_blocked
                else None
            ),
            "no_coverage_improvement": (
                no_improvement[0]
                if no_improvement
                else None
            ),
            "multi_document": (
                multi_document[0]
                if multi_document
                else None
            ),
        },
        "case_results": records,
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            output,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print(
        "===================================="
    )
    print(
        "BEHAVIOURAL VALIDATION SUMMARY"
    )
    print(
        "===================================="
    )

    print(
        json.dumps(
            output[
                "summary"
            ],
            indent=2,
        )
    )

    print()
    print(
        f"Output written to: {OUTPUT_PATH}"
    )

    return output


if __name__ == "__main__":
    run_behavior_check()