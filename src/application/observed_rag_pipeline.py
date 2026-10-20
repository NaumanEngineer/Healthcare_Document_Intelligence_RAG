"""Week 27 Day 4 — observed canonical RAG application boundary.

This module adds safe structured observability around the existing canonical
Week 27 RAG pipeline without changing retrieval, generation, assurance,
governance, or final answer authority.

Observability is deliberately downstream of the governed application result.

If observability construction fails, the original governed result is preserved.
The failure is represented only as a non-sensitive observability status.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from src.application.observability_adapter import (
    build_pipeline_observability,
)
from src.application.rag_pipeline import (
    run_rag_pipeline,
)
from src.application.runtime_config import (
    DETERMINISTIC_ONLY,
    RAGRuntimeConfig,
)


OBSERVABILITY_COMPLETED = "COMPLETED"
OBSERVABILITY_FAILED = "FAILED"


def _build_observability_envelope(
    result: dict,
) -> dict:
    """Build observability without changing the governed pipeline result."""

    try:
        events = build_pipeline_observability(
            result
        )

        return {
            "status": (
                OBSERVABILITY_COMPLETED
            ),
            "event_count": len(
                events
            ),
            "events": events,
        }

    except Exception as exc:
        return {
            "status": (
                OBSERVABILITY_FAILED
            ),
            "event_count": 0,
            "events": [],
            "error_type": (
                type(
                    exc
                ).__name__
            ),
        }


def attach_observability(
    result: dict,
) -> dict:
    """Return a copy of one governed result with safe observability attached.

    The supplied result is never mutated.
    """

    if not isinstance(
        result,
        dict,
    ):
        raise ValueError(
            "result must be a dictionary."
        )

    output = deepcopy(
        result
    )

    output[
        "observability"
    ] = _build_observability_envelope(
        output
    )

    return output


def run_observed_rag_pipeline(
    *,
    question: str,
    chunks: list,
    embedded_chunks: list,
    embedding_model: Any,
    embedding_model_name: str,
    semantic_k: int = 10,
    keyword_k: int = 10,
    final_k: int = 3,
    semantic_min_similarity: float | None = None,
    keyword_min_score: float | None = None,
    min_rrf_score: float | None = None,
    rrf_k: int = 60,
    max_related_chunks: int = 2,
    execution_mode: str = DETERMINISTIC_ONLY,
    model_provider: Any = None,
    query_date: str | None = None,
    runtime_config: RAGRuntimeConfig | None = None,
) -> dict:
    """Run the canonical pipeline and attach safe structured observability.

    All application arguments are forwarded directly to run_rag_pipeline.

    Observability is downstream only and cannot alter the governed result.
    """

    result = run_rag_pipeline(
        question=question,
        chunks=chunks,
        embedded_chunks=embedded_chunks,
        embedding_model=embedding_model,
        embedding_model_name=embedding_model_name,
        semantic_k=semantic_k,
        keyword_k=keyword_k,
        final_k=final_k,
        semantic_min_similarity=(
            semantic_min_similarity
        ),
        keyword_min_score=(
            keyword_min_score
        ),
        min_rrf_score=(
            min_rrf_score
        ),
        rrf_k=rrf_k,
        max_related_chunks=(
            max_related_chunks
        ),
        execution_mode=execution_mode,
        model_provider=model_provider,
        query_date=query_date,
        runtime_config=runtime_config,
    )

    return attach_observability(
        result
    )