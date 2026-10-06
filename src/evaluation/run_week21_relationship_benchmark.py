"""Week 21 Day 3 relationship-aware retrieval benchmark.

This benchmark compares the existing Hybrid retrieval baseline against
the experimental relationship-aware expansion layer.

The frozen Week 18 evaluation cases, raw corpus, retrieval configuration,
and evidence-sufficiency gate are reused.

Relationship-aware expansion is applied only after ordinary Hybrid
retrieval. The relationship registry is used for navigation only;
evidence sufficiency and governance remain authoritative.
"""

from __future__ import annotations

import hashlib
import json
from time import perf_counter

from src.evaluation import run_week18_benchmark as baseline
from src.evaluation.retrieval_benchmark import (
    evaluate_retrieval_results,
    summarise_method,
)
from src.retrieval.relationship_aware_retrieval import (
    expand_results_with_relationships,
)


def _run_relationship_aware(
    query: str,
    *,
    chunks: list[dict],
    common: dict,
) -> dict:
    """Run Hybrid followed by bounded relationship expansion."""

    initial_results = baseline.hybrid_search(
        query=query,
        **common,
    )

    expansion = expand_results_with_relationships(
        initial_results,
        chunks,
        max_related_chunks=2,
    )

    final_results = expansion["results"]

    final_evidence = (
        baseline.assess_evidence_sufficiency(
            query,
            final_results,
        )
    )

    return {
        "results": final_results,
        "audit": {
            "initial_results": initial_results,
            "relationship_expansion": (
                expansion["audit"]
            ),
            "final_evidence": final_evidence,
        },
    }


def run_benchmark():
    import torch

    torch.manual_seed(0)
    torch.use_deterministic_algorithms(True)

    benchmark_start = perf_counter()

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
    # LOAD FROZEN INPUTS
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
    # TWO-METHOD CONTROLLED COMPARISON
    # --------------------------------------------------------

    methods = {
        "hybrid": (
            lambda q: baseline.hybrid_search(
                query=q,
                **common,
            )
        ),
        "hybrid_relationship_aware": (
            lambda q: _run_relationship_aware(
                q,
                chunks=chunks,
                common=common,
            )
        ),
    }

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
        }

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

                if (
                    name
                    == "hybrid_relationship_aware"
                ):
                    raw = result["results"]

                    assessment = result[
                        "audit"
                    ][
                        "final_evidence"
                    ]

                    record[
                        "hybrid_relationship_aware_audit"
                    ] = result["audit"]

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

            record[name] = (
                evaluate_retrieval_results(
                    case,
                    selected,
                    top_k=baseline.FINAL_K,
                )
            )

            record[
                "raw_results"
            ][name] = raw

            record[
                "evidence_sufficiency"
            ][name] = assessment

            record[
                "latency_seconds"
            ][name] = elapsed

        records.append(
            record
        )

        print(
            case["query_id"],
            "complete",
            flush=True,
        )

    # --------------------------------------------------------
    # VERIFY FROZEN INPUTS
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

    assert hashes == final_hashes

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
            ][name]
            for record in records
        )
        for name in methods
    }

    expansion_stop_reasons: dict[
        str,
        int,
    ] = {}

    expanded_case_count = 0

    relationship_evidence_case_count = 0

    for record in records:
        audit = record.get(
            "hybrid_relationship_aware_audit"
        )

        if not audit:
            continue

        expansion = audit[
            "relationship_expansion"
        ]

        stop_reason = expansion[
            "stop_reason"
        ]

        expansion_stop_reasons[
            stop_reason
        ] = (
            expansion_stop_reasons.get(
                stop_reason,
                0,
            )
            + 1
        )

        if (
            expansion[
                "expansion_count"
            ]
            > 0
        ):
            expanded_case_count += 1

        if expansion[
            "relationship_evidence_candidate_ids"
        ]:
            relationship_evidence_case_count += 1

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
                "relationship_max_related_chunks": 2,
            }
        ),
        "relationship_expansion_summary": {
            "expanded_case_count": (
                expanded_case_count
            ),
            "relationship_evidence_case_count": (
                relationship_evidence_case_count
            ),
            "stop_reasons": (
                expansion_stop_reasons
            ),
        },
        "method_seconds": method_seconds,
        "total_seconds": (
            perf_counter()
            - benchmark_start
        ),
    }

    # --------------------------------------------------------
    # SAVE DAY 3 OUTPUT
    # --------------------------------------------------------

    path = (
        baseline.PROJECT_ROOT
        / "outputs"
        / "week21_day3_relationship_benchmark.json"
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
                    "configuration",
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