"""Week 22 Day 2 — real Evidence Packet check."""

from __future__ import annotations

import json

from src.evaluation import (
    run_week18_benchmark as baseline,
)
from src.evidence.evidence_packet import (
    build_evidence_packet,
)
from src.retrieval.retrieval_orchestrator import (
    orchestrate_retrieval,
)


def main():
    question = (
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
        query=question,
        **common,
    )

    packet = build_evidence_packet(
        question,
        retrieval_output,
    )

    print(
        json.dumps(
            packet,
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()