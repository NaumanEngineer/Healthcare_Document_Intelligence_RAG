"""Week 22 Day 1 — real evidence-flow check.

Runs one Architecture v2 retrieval case and converts the final
retrieval output into structured evidence objects.
"""

from __future__ import annotations

import json

from src.evaluation import (
    run_week18_benchmark as baseline,
)
from src.evidence.evidence_from_retrieval import (
    build_evidence_from_retrieval,
)
from src.retrieval.retrieval_orchestrator import (
    orchestrate_retrieval,
)


def main():
    query = (
        "How should severe weather pressure and ambulance "
        "handover disruption be considered together?"
    )

    chunks = baseline.build_benchmark_corpus()

    model = baseline.load_embedding_model()

    model_name = baseline.get_model_identifier(
        model
    )

    embedded = baseline.embed_chunks(
        chunks=chunks,
        model=model,
        model_name=model_name,
    )

    common = {
        "chunks": chunks,
        "embedded_chunks": embedded,
        "model": model,
        "embedding_model": model_name,
        "semantic_k": baseline.SEMANTIC_K,
        "keyword_k": baseline.KEYWORD_K,
        "final_k": baseline.FINAL_K,
        "semantic_min_similarity": (
            baseline.SEMANTIC_MIN_SIMILARITY
        ),
        "keyword_min_score": (
            baseline.KEYWORD_MIN_SCORE
        ),
        "min_rrf_score": (
            baseline.MIN_RRF_SCORE
        ),
    }

    retrieval_output = orchestrate_retrieval(
        query=query,
        **common,
    )

    evidence_objects = (
        build_evidence_from_retrieval(
            retrieval_output
        )
    )

    output = {
        "question": query,
        "selected_route": (
            retrieval_output[
                "audit"
            ].get(
                "selected_route"
            )
        ),
        "stop_reason": (
            retrieval_output[
                "audit"
            ].get(
                "stop_reason"
            )
        ),
        "final_evidence": (
            retrieval_output[
                "audit"
            ].get(
                "final_evidence"
            )
        ),
        "evidence_objects": evidence_objects,
    }

    print(
        json.dumps(
            output,
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()