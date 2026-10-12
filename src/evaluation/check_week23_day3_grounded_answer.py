"""Week 23 Day 3 — real grounded-response pipeline check."""

from __future__ import annotations

import json

from src.evaluation import (
    run_week18_benchmark as baseline,
)
from src.evidence.evidence_packet import (
    build_evidence_packet,
)
from src.generation.answer_contract import (
    build_answer_contract,
)
from src.generation.answer_context import (
    build_answer_context,
)
from src.generation.grounded_answer import (
    build_grounded_response,
)
from src.retrieval.retrieval_orchestrator import (
    orchestrate_retrieval,
)


def main():
    cases = baseline.load_evaluation_cases()

    target_ids = [
        "Q003",
        "Q027",
        "Q029",
    ]

    chunks = baseline.build_benchmark_corpus()

    model = baseline.load_embedding_model()

    model_name = baseline.get_model_identifier(
        model
    )

    embedded_chunks = baseline.embed_chunks(
        chunks=chunks,
        model=model,
        model_name=model_name,
    )

    common = {
        "chunks": chunks,
        "embedded_chunks": embedded_chunks,
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

    for query_id in target_ids:
        case = next(
            item
            for item in cases
            if item["query_id"] == query_id
        )

        question = case["question"]

        retrieval_output = orchestrate_retrieval(
            query=question,
            **common,
        )

        packet = build_evidence_packet(
            question,
            retrieval_output,
        )

        contract = build_answer_contract(
            packet
        )

        context = build_answer_context(
            packet,
            contract,
        )

        response = build_grounded_response(
            contract,
            context,
        )

        print("=" * 80)
        print(query_id)
        print("=" * 80)

        print(
            json.dumps(
                {
                    "question": question,
                    "governance": (
                        response[
                            "governance_decision"
                        ]
                    ),
                    "response_type": (
                        response[
                            "response_type"
                        ]
                    ),
                    "generation_status": (
                        response[
                            "generation_status"
                        ]
                    ),
                    "requires_human_review": (
                        response[
                            "requires_human_review"
                        ]
                    ),
                    "citations_used": (
                        response[
                            "citations_used"
                        ]
                    ),
                    "sections": (
                        response[
                            "sections"
                        ]
                    ),
                },
                indent=2,
                default=str,
            )
        )


if __name__ == "__main__":
    main()