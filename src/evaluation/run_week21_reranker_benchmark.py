"""Untuned seven-method comparison using the frozen Week 18 inputs and gates."""

import hashlib
import json
from time import perf_counter

from src.evaluation import run_week18_benchmark as baseline
from src.evaluation.retrieval_benchmark import (
    evaluate_retrieval_results,
    summarise_method,
)
from src.retrieval.bounded_agentic_retrieval import (
    bounded_agentic_retrieval,
)
from src.retrieval.relevance_scorers import (
    CrossEncoderScorer,
)


def run_benchmark():
    import torch

    torch.manual_seed(0)
    torch.use_deterministic_algorithms(True)

    start = perf_counter()

    # --------------------------------------------------------
    # FREEZE INPUT FILES
    # --------------------------------------------------------

    files = [
        baseline.EVALUATION_FILE,
        *baseline.get_raw_corpus_files(),
    ]

    hashes = {
        str(
            path.relative_to(
                baseline.PROJECT_ROOT
            )
        ): hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        for path in files
    }

    # --------------------------------------------------------
    # LOAD FROZEN EVALUATION INPUTS
    # --------------------------------------------------------

    cases = baseline.load_evaluation_cases()

    chunks = baseline.build_benchmark_corpus()

    model = baseline.load_embedding_model()

    model_name = (
        baseline.get_model_identifier(
            model
        )
    )

    embedded = baseline.embed_chunks(
        chunks=chunks,
        model=model,
        model_name=model_name,
    )

    # --------------------------------------------------------
    # LOAD EXPERIMENTAL CROSS-ENCODER RERANKER
    # --------------------------------------------------------

    load_start = perf_counter()

    scorer = CrossEncoderScorer()

    load_seconds = (
        perf_counter()
        - load_start
    )

    # --------------------------------------------------------
    # COMMON RETRIEVAL CONFIGURATION
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # SEVEN METHODS
    # --------------------------------------------------------

    methods = {
        "semantic": (
            lambda q: baseline.semantic_search(
                q,
                embedded,
                model,
                model_name,
                candidate_k=baseline.SEMANTIC_K,
                final_k=baseline.FINAL_K,
                min_similarity=(
                    baseline.SEMANTIC_MIN_SIMILARITY
                ),
            )
        ),

        "keyword": (
            lambda q: baseline.keyword_search(
                q,
                chunks,
                top_k=baseline.FINAL_K,
                min_score=(
                    baseline.KEYWORD_MIN_SCORE
                ),
            )
        ),

        "hybrid": (
            lambda q: baseline.hybrid_search(
                query=q,
                **common,
            )
        ),

        "rrf_only": (
            lambda q: (
                baseline.hybrid_search_rrf_only(
                    query=q,
                    **common,
                )
            )
        ),

        "hybrid_rescue": (
            lambda q: (
                baseline.hybrid_search_evidence_rescue(
                    query=q,
                    **common,
                )
            )
        ),

        "hybrid_reranker": (
            lambda q: baseline.hybrid_search(
                query=q,
                **common,
                relevance_scorer=scorer,
            )
        ),

        "hybrid_agentic": (
            lambda q: bounded_agentic_retrieval(
                query=q,
                **common,
                max_rounds=2,
            )
        ),
    }

    # --------------------------------------------------------
    # RUN BENCHMARK
    # --------------------------------------------------------

    records = []

    for case in cases:
        query = case["question"]

        scope = baseline.assess_query_scope(
            query
        )

        record = {
            "query_id": case["query_id"],
            "question": query,
            "expected": case,
            "raw_results": {},
            "evidence_sufficiency": {},
            "latency_seconds": {},
            "scorer_candidates": 0,
        }

        previous_count = (
            scorer.candidates
        )

        for name, retrieve in methods.items():
            raw = []
            assessment = None
            elapsed = 0.0

            if scope["allowed"]:
                tick = perf_counter()

                result = retrieve(
                    query
                )

                elapsed = (
                    perf_counter()
                    - tick
                )

                if name == "hybrid_rescue":
                    raw = result[
                        "results"
                    ]

                    assessment = result[
                        "audit"
                    ][
                        "final_evidence"
                    ]

                    record[
                        "hybrid_rescue_audit"
                    ] = result[
                        "audit"
                    ]

                elif name == "hybrid_agentic":
                    raw = result[
                        "results"
                    ]

                    assessment = result[
                        "audit"
                    ][
                        "final_evidence"
                    ]

                    record[
                        "hybrid_agentic_audit"
                    ] = result[
                        "audit"
                    ]

                else:
                    raw = result

                    assessment = (
                        baseline.assess_evidence_sufficiency(
                            query,
                            raw,
                        )
                    )

            selected = (
                raw
                if (
                    assessment
                    and assessment[
                        "decision"
                    ]
                    == "SUFFICIENT"
                )
                else []
            )

            record[
                name
            ] = evaluate_retrieval_results(
                case,
                selected,
                top_k=baseline.FINAL_K,
            )

            record[
                "raw_results"
            ][
                name
            ] = raw

            record[
                "evidence_sufficiency"
            ][
                name
            ] = assessment

            record[
                "latency_seconds"
            ][
                name
            ] = elapsed

        record[
            "scorer_candidates"
        ] = (
            scorer.candidates
            - previous_count
        )

        records.append(
            record
        )

        print(
            case["query_id"],
            "complete",
            flush=True,
        )

    # --------------------------------------------------------
    # CONFIRM FROZEN INPUTS DID NOT CHANGE
    # --------------------------------------------------------

    final_hashes = {
        str(
            path.relative_to(
                baseline.PROJECT_ROOT
            )
        ): hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        for path in files
    }

    assert (
        hashes
        == final_hashes
    )

    # --------------------------------------------------------
    # SUMMARISE
    # --------------------------------------------------------

    summary = {
        name: summarise_method(
            records,
            name,
        )
        for name in methods
    }

    method_seconds = {
        name: sum(
            record[
                "latency_seconds"
            ][
                name
            ]
            for record in records
        )
        for name in methods
    }

    output = {
        "summary": summary,
        "case_results": records,
        "input_sha256": hashes,
        "configuration": (
            common
            | {
                "chunks": None,
                "embedded_chunks": None,
                "model": None,
                "agentic_max_rounds": 2,
            }
        ),
        "model": scorer.model_name,
        "model_load_seconds": (
            load_seconds
        ),
        "model_revision": getattr(
            scorer.model.model.config,
            "_commit_hash",
            None,
        ),
        "scorer_calls": (
            scorer.calls
        ),
        "scorer_candidates": (
            scorer.candidates
        ),
        "scorer_seconds": (
            scorer.seconds
        ),
        "total_seconds": (
            perf_counter()
            - start
        ),
        "method_seconds": (
            method_seconds
        ),
    }

    # --------------------------------------------------------
    # SAVE DAY 2 OUTPUT
    # --------------------------------------------------------

    path = (
        baseline.PROJECT_ROOT
        / "outputs"
        / "week21_day2_agentic_benchmark.json"
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            output,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print(
        json.dumps(
            {
                key: value
                for key, value
                in output.items()
                if key not in (
                    "case_results",
                    "input_sha256",
                )
            },
            indent=2,
        )
    )

    print()
    print(
        f"Benchmark written to: {path}"
    )

    return output


if __name__ == "__main__":
    run_benchmark()