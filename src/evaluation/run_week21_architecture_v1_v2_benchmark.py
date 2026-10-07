"""Week 21 Day 6 — Architecture v1 versus Architecture v2 benchmark.

Primary question:

Does Architecture v2 retrieve better evidence than Architecture v1
without increasing unsafe behaviour?

Architecture v1:
    Scope
    -> Hybrid
    -> Evidence Sufficiency
    -> Existing Pre-Generation Governance

Architecture v2:
    Scope
    -> Hybrid
    -> Evidence Sufficiency
    -> Deterministic Router
    -> At most one bounded enhancement route
    -> Final Evidence Sufficiency
    -> Retrieval/Governance Bridge
    -> Existing Pre-Generation Governance

The frozen Week 18 evaluation cases, corpus, embedding model,
retrieval depths, thresholds and shared retrieval scoring functions
are reused.

This is a controlled synthetic benchmark. It is not a production
NHS performance claim.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from time import perf_counter

from src.evaluation import (
    run_week18_benchmark as baseline,
)
from src.evaluation.retrieval_benchmark import (
    evaluate_retrieval_results,
    summarise_method,
)
from src.governance.retrieval_review_integration import (
    decide_retrieval_governance_outcome,
)
from src.governance.review_decision import (
    ABSTAIN,
    AUTO_ANSWER,
    REVIEW_REQUIRED,
    decide_review_outcome,
)
from src.retrieval.retrieval_orchestrator import (
    orchestrate_retrieval,
)


ARCHITECTURE_V1 = "architecture_v1"
ARCHITECTURE_V2 = "architecture_v2"


def _document_ids(
    results: list[dict],
) -> list[str]:
    """Return unique document IDs preserving result order."""

    ids: list[str] = []

    for result in results:
        document_id = result.get(
            "document_id"
        )

        if (
            isinstance(document_id, str)
            and document_id
            and document_id not in ids
        ):
            ids.append(
                document_id
            )

    return ids


def _chunk_ids(
    results: list[dict],
) -> list[str]:
    """Return chunk IDs without storing full result dictionaries."""

    ids: list[str] = []

    for result in results:
        chunk_id = result.get(
            "chunk_id"
        )

        if (
            isinstance(chunk_id, str)
            and chunk_id
        ):
            ids.append(
                chunk_id
            )

    return ids


def _compact_evidence(
    assessment: dict | None,
) -> dict | None:
    """Keep only benchmark-relevant evidence fields."""

    if not isinstance(
        assessment,
        dict,
    ):
        return None

    return {
        "decision": assessment.get(
            "decision"
        ),
        "sufficient": assessment.get(
            "sufficient"
        ),
        "query_topics": assessment.get(
            "query_topics"
        ),
        "matched_query_terms": assessment.get(
            "matched_query_terms"
        ),
        "unsupported_claims": assessment.get(
            "unsupported_claims"
        ),
        "result_count": assessment.get(
            "result_count"
        ),
    }


def _compact_governance(
    decision: dict,
) -> dict:
    """Keep governance outcome fields needed for comparison."""

    return {
        "decision": decision.get(
            "decision"
        ),
        "requires_human_review": decision.get(
            "requires_human_review"
        ),
        "may_generate_answer": decision.get(
            "may_generate_answer"
        ),
        "document_ids": decision.get(
            "document_ids",
            [],
        ),
        "retrieval_route": decision.get(
            "retrieval_route"
        ),
        "retrieval_stop_reason": decision.get(
            "retrieval_stop_reason"
        ),
    }


def _run_v1(
    query: str,
    scope: dict,
    *,
    common: dict,
) -> dict:
    """Run the Architecture v1 baseline."""

    if not scope[
        "allowed"
    ]:
        governance = decide_review_outcome(
            question=query,
            scope_assessment=scope,
            results=[],
        )

        return {
            "results": [],
            "evidence": None,
            "governance": governance,
            "hybrid_call_count": 0,
            "route": "STOP_OUT_OF_SCOPE",
        }

    raw_results = baseline.hybrid_search(
        query=query,
        **common,
    )

    evidence = (
        baseline.assess_evidence_sufficiency(
            query,
            raw_results,
        )
    )

    selected_results = (
        raw_results
        if evidence.get(
            "sufficient"
        )
        is True
        else []
    )

    governance = decide_review_outcome(
        question=query,
        scope_assessment=scope,
        results=selected_results,
    )

    return {
        "results": selected_results,
        "raw_results": raw_results,
        "evidence": evidence,
        "governance": governance,
        "hybrid_call_count": 1,
        "route": (
            "RETURN_INITIAL"
            if evidence.get(
                "sufficient"
            )
            is True
            else "STOP_INSUFFICIENT"
        ),
    }


def _run_v2(
    query: str,
    *,
    common: dict,
) -> dict:
    """Run the complete Architecture v2 retrieval/governance path."""

    retrieval_output = orchestrate_retrieval(
        query=query,
        **common,
    )

    governance = (
        decide_retrieval_governance_outcome(
            question=query,
            retrieval_output=retrieval_output,
        )
    )

    audit = retrieval_output[
        "audit"
    ]

    final_evidence = audit.get(
        "final_evidence"
    )

    selected_results = (
        retrieval_output[
            "results"
        ]
        if (
            isinstance(
                final_evidence,
                dict,
            )
            and final_evidence.get(
                "sufficient"
            )
            is True
        )
        else []
    )

    route_audit = audit.get(
        "route_audit"
    )

    return {
        "results": selected_results,
        "raw_results": retrieval_output[
            "results"
        ],
        "evidence": final_evidence,
        "governance": governance,
        "route": audit.get(
            "selected_route"
        ),
        "stop_reason": audit.get(
            "stop_reason"
        ),
        "hybrid_call_count": audit.get(
            "total_hybrid_retrieval_calls",
            0,
        ),
        "route_audit": route_audit,
    }


def _route_cost_details(
    v2_output: dict,
) -> dict:
    """Extract bounded route-cost indicators."""

    route = v2_output.get(
        "route"
    )

    route_audit = v2_output.get(
        "route_audit"
    )

    relationship_expansion = 0
    rrf_pool_calls = 0

    if isinstance(
        route_audit,
        dict,
    ):
        if route == "RELATIONSHIP_AWARE":
            relationship_expansion = int(
                route_audit.get(
                    "expansion_count",
                    0,
                )
                > 0
            )

        if route == "HYBRID_RESCUE":
            rrf_pool_calls = int(
                route_audit.get(
                    "additional_rrf_pool_call_count",
                    0,
                )
            )

    return {
        "relationship_expansion_used": (
            relationship_expansion
        ),
        "rrf_pool_call_count": (
            rrf_pool_calls
        ),
        "hybrid_call_count": (
            v2_output.get(
                "hybrid_call_count",
                0,
            )
        ),
    }


def _governance_is_unsafe_for_expected_abstention(
    case: dict,
    governance: dict,
) -> bool:
    """Flag automatic answering on a designated abstention case."""

    return bool(
        case.get(
            "expected_abstention",
            False,
        )
        and governance.get(
            "decision"
        )
        == AUTO_ANSWER
    )


def _unsafe_lifecycle_auto_answer(
    results: list[dict],
    governance: dict,
) -> bool:
    """Flag AUTO_ANSWER if any returned evidence is non-Active."""

    if governance.get(
        "decision"
    ) != AUTO_ANSWER:
        return False

    return any(
        result.get(
            "status"
        )
        != "Active"
        for result in results
    )


def _count_governance_outcomes(
    records: list[dict],
    architecture: str,
) -> dict:
    """Count AUTO_ANSWER / REVIEW_REQUIRED / ABSTAIN."""

    counter = Counter(
        record[
            "governance"
        ][
            architecture
        ][
            "decision"
        ]
        for record in records
    )

    return {
        AUTO_ANSWER: counter.get(
            AUTO_ANSWER,
            0,
        ),
        REVIEW_REQUIRED: counter.get(
            REVIEW_REQUIRED,
            0,
        ),
        ABSTAIN: counter.get(
            ABSTAIN,
            0,
        ),
    }


def _comparison_summary(
    records: list[dict],
) -> dict:
    """Calculate labelled-case and abstention-case wins/losses."""

    top1_wins = 0
    top1_losses = 0
    top1_neutral = 0

    topk_wins = 0
    topk_losses = 0
    topk_neutral = 0

    abstention_wins = 0
    abstention_losses = 0
    abstention_neutral = 0

    evidence_wins = 0
    evidence_losses = 0
    evidence_neutral = 0

    for record in records:
        v1 = record[
            ARCHITECTURE_V1
        ]

        v2 = record[
            ARCHITECTURE_V2
        ]

        if (
            v1[
                "top1_success"
            ]
            is not None
        ):
            if (
                v2[
                    "top1_success"
                ]
                and not v1[
                    "top1_success"
                ]
            ):
                top1_wins += 1

            elif (
                v1[
                    "top1_success"
                ]
                and not v2[
                    "top1_success"
                ]
            ):
                top1_losses += 1

            else:
                top1_neutral += 1

        if (
            v1[
                "topk_success"
            ]
            is not None
        ):
            if (
                v2[
                    "topk_success"
                ]
                and not v1[
                    "topk_success"
                ]
            ):
                topk_wins += 1

            elif (
                v1[
                    "topk_success"
                ]
                and not v2[
                    "topk_success"
                ]
            ):
                topk_losses += 1

            else:
                topk_neutral += 1

        if (
            v1[
                "abstention_success"
            ]
            is not None
        ):
            if (
                v2[
                    "abstention_success"
                ]
                and not v1[
                    "abstention_success"
                ]
            ):
                abstention_wins += 1

            elif (
                v1[
                    "abstention_success"
                ]
                and not v2[
                    "abstention_success"
                ]
            ):
                abstention_losses += 1

            else:
                abstention_neutral += 1

        v1_sufficient = bool(
            record[
                "evidence_sufficiency"
            ][
                ARCHITECTURE_V1
            ]
            and record[
                "evidence_sufficiency"
            ][
                ARCHITECTURE_V1
            ].get(
                "sufficient"
            )
        )

        v2_sufficient = bool(
            record[
                "evidence_sufficiency"
            ][
                ARCHITECTURE_V2
            ]
            and record[
                "evidence_sufficiency"
            ][
                ARCHITECTURE_V2
            ].get(
                "sufficient"
            )
        )

        if (
            v2_sufficient
            and not v1_sufficient
        ):
            evidence_wins += 1

        elif (
            v1_sufficient
            and not v2_sufficient
        ):
            evidence_losses += 1

        else:
            evidence_neutral += 1

    return {
        "top1": {
            "v2_wins": top1_wins,
            "v2_losses": top1_losses,
            "neutral": top1_neutral,
        },
        "topk": {
            "v2_wins": topk_wins,
            "v2_losses": topk_losses,
            "neutral": topk_neutral,
        },
        "abstention": {
            "v2_wins": abstention_wins,
            "v2_losses": abstention_losses,
            "neutral": abstention_neutral,
        },
        "evidence_sufficiency": {
            "v2_wins": evidence_wins,
            "v2_losses": evidence_losses,
            "neutral": evidence_neutral,
        },
    }


def run_benchmark() -> dict:
    """Run the frozen Architecture v1 versus v2 comparison."""

    import torch

    torch.manual_seed(
        0
    )

    torch.use_deterministic_algorithms(
        True
    )

    benchmark_start = perf_counter()

    print()

    print(
        "WEEK 21 DAY 6 — ARCHITECTURE V1 VS V2"
    )

    print(
        "=" * 60
    )

    # --------------------------------------------------------
    # FREEZE INPUTS
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
    # LOAD FROZEN CASES / CORPUS / MODEL
    # --------------------------------------------------------

    cases = (
        baseline.load_evaluation_cases()
    )

    chunks = (
        baseline.build_benchmark_corpus()
    )

    model = (
        baseline.load_embedding_model()
    )

    model_name = (
        baseline.get_model_identifier(
            model
        )
    )

    embedded = (
        baseline.embed_chunks(
            chunks=chunks,
            model=model,
            model_name=model_name,
        )
    )

    print(
        f"Evaluation cases: {len(cases)}"
    )

    print(
        f"Corpus chunks: {len(chunks)}"
    )

    print(
        f"Embedding model: {model_name}"
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

    records = []

    route_counts = Counter()

    route_stop_reasons = Counter()

    v1_hybrid_calls = 0
    v2_hybrid_calls = 0

    v2_relationship_expansions = 0
    v2_rrf_pool_calls = 0

    unsafe_expected_abstention = {
        ARCHITECTURE_V1: 0,
        ARCHITECTURE_V2: 0,
    }

    unsafe_lifecycle = {
        ARCHITECTURE_V1: 0,
        ARCHITECTURE_V2: 0,
    }

    # --------------------------------------------------------
    # RUN EACH FROZEN CASE
    # --------------------------------------------------------

    for case in cases:
        query = case[
            "question"
        ]

        scope = (
            baseline.assess_query_scope(
                query
            )
        )

        # ---------------- V1 ----------------

        tick = perf_counter()

        v1_output = _run_v1(
            query,
            scope,
            common=common,
        )

        v1_elapsed = (
            perf_counter()
            - tick
        )

        # ---------------- V2 ----------------

        tick = perf_counter()

        v2_output = _run_v2(
            query,
            common=common,
        )

        v2_elapsed = (
            perf_counter()
            - tick
        )

        # ----------------------------------------------------
        # SHARED RETRIEVAL SCORING
        # ----------------------------------------------------

        v1_evaluation = (
            evaluate_retrieval_results(
                case,
                v1_output[
                    "results"
                ],
                top_k=baseline.FINAL_K,
            )
        )

        v2_evaluation = (
            evaluate_retrieval_results(
                case,
                v2_output[
                    "results"
                ],
                top_k=baseline.FINAL_K,
            )
        )

        # ----------------------------------------------------
        # SAFETY
        # ----------------------------------------------------

        if (
            _governance_is_unsafe_for_expected_abstention(
                case,
                v1_output[
                    "governance"
                ],
            )
        ):
            unsafe_expected_abstention[
                ARCHITECTURE_V1
            ] += 1

        if (
            _governance_is_unsafe_for_expected_abstention(
                case,
                v2_output[
                    "governance"
                ],
            )
        ):
            unsafe_expected_abstention[
                ARCHITECTURE_V2
            ] += 1

        if (
            _unsafe_lifecycle_auto_answer(
                v1_output[
                    "results"
                ],
                v1_output[
                    "governance"
                ],
            )
        ):
            unsafe_lifecycle[
                ARCHITECTURE_V1
            ] += 1

        if (
            _unsafe_lifecycle_auto_answer(
                v2_output[
                    "results"
                ],
                v2_output[
                    "governance"
                ],
            )
        ):
            unsafe_lifecycle[
                ARCHITECTURE_V2
            ] += 1

        # ----------------------------------------------------
        # V2 ROUTE / COST AUDIT
        # ----------------------------------------------------

        route = (
            v2_output.get(
                "route"
            )
            or "UNKNOWN"
        )

        route_counts[
            route
        ] += 1

        stop_reason = (
            v2_output.get(
                "stop_reason"
            )
            or "NONE"
        )

        route_stop_reasons[
            stop_reason
        ] += 1

        cost = _route_cost_details(
            v2_output
        )

        v1_hybrid_calls += (
            v1_output.get(
                "hybrid_call_count",
                0,
            )
        )

        v2_hybrid_calls += (
            cost[
                "hybrid_call_count"
            ]
        )

        v2_relationship_expansions += (
            cost[
                "relationship_expansion_used"
            ]
        )

        v2_rrf_pool_calls += (
            cost[
                "rrf_pool_call_count"
            ]
        )

        # ----------------------------------------------------
        # COMPACT CASE RECORD
        # ----------------------------------------------------

        record = {
            "query_id": case[
                "query_id"
            ],
            "question": query,
            "expected": {
                "expected_document_id": (
                    case.get(
                        "expected_document_id"
                    )
                ),
                "expected_document_ids": (
                    case.get(
                        "expected_document_ids"
                    )
                ),
                "expected_abstention": (
                    case.get(
                        "expected_abstention",
                        False,
                    )
                ),
            },
            ARCHITECTURE_V1: (
                v1_evaluation
            ),
            ARCHITECTURE_V2: (
                v2_evaluation
            ),
            "evidence_sufficiency": {
                ARCHITECTURE_V1: (
                    _compact_evidence(
                        v1_output.get(
                            "evidence"
                        )
                    )
                ),
                ARCHITECTURE_V2: (
                    _compact_evidence(
                        v2_output.get(
                            "evidence"
                        )
                    )
                ),
            },
            "governance": {
                ARCHITECTURE_V1: (
                    _compact_governance(
                        v1_output[
                            "governance"
                        ]
                    )
                ),
                ARCHITECTURE_V2: (
                    _compact_governance(
                        v2_output[
                            "governance"
                        ]
                    )
                ),
            },
            "raw_document_ids": {
                ARCHITECTURE_V1: (
                    _document_ids(
                        v1_output.get(
                            "raw_results",
                            [],
                        )
                    )
                ),
                ARCHITECTURE_V2: (
                    _document_ids(
                        v2_output.get(
                            "raw_results",
                            [],
                        )
                    )
                ),
            },
            "raw_chunk_ids": {
                ARCHITECTURE_V1: (
                    _chunk_ids(
                        v1_output.get(
                            "raw_results",
                            [],
                        )
                    )
                ),
                ARCHITECTURE_V2: (
                    _chunk_ids(
                        v2_output.get(
                            "raw_results",
                            [],
                        )
                    )
                ),
            },
            "v2_route": route,
            "v2_stop_reason": stop_reason,
            "v2_cost": cost,
            "latency_seconds": {
                ARCHITECTURE_V1: (
                    v1_elapsed
                ),
                ARCHITECTURE_V2: (
                    v2_elapsed
                ),
            },
        }

        records.append(
            record
        )

        print(
            case["query_id"],
            "complete",
            "| v1:",
            v1_output[
                "route"
            ],
            "| v2:",
            route,
            flush=True,
        )

    # --------------------------------------------------------
    # VERIFY FROZEN INPUTS DID NOT CHANGE
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
    # SUMMARY
    # --------------------------------------------------------

    retrieval_summary = {
        ARCHITECTURE_V1: (
            summarise_method(
                records,
                ARCHITECTURE_V1,
            )
        ),
        ARCHITECTURE_V2: (
            summarise_method(
                records,
                ARCHITECTURE_V2,
            )
        ),
    }

    evidence_summary = {
        ARCHITECTURE_V1: {
            "sufficient_cases": sum(
                1
                for record in records
                if (
                    record[
                        "evidence_sufficiency"
                    ][
                        ARCHITECTURE_V1
                    ]
                    and record[
                        "evidence_sufficiency"
                    ][
                        ARCHITECTURE_V1
                    ].get(
                        "sufficient"
                    )
                    is True
                )
            ),
        },
        ARCHITECTURE_V2: {
            "sufficient_cases": sum(
                1
                for record in records
                if (
                    record[
                        "evidence_sufficiency"
                    ][
                        ARCHITECTURE_V2
                    ]
                    and record[
                        "evidence_sufficiency"
                    ][
                        ARCHITECTURE_V2
                    ].get(
                        "sufficient"
                    )
                    is True
                )
            ),
        },
    }

    governance_summary = {
        ARCHITECTURE_V1: (
            _count_governance_outcomes(
                records,
                ARCHITECTURE_V1,
            )
        ),
        ARCHITECTURE_V2: (
            _count_governance_outcomes(
                records,
                ARCHITECTURE_V2,
            )
        ),
    }

    latency_summary = {
        ARCHITECTURE_V1: sum(
            record[
                "latency_seconds"
            ][
                ARCHITECTURE_V1
            ]
            for record in records
        ),
        ARCHITECTURE_V2: sum(
            record[
                "latency_seconds"
            ][
                ARCHITECTURE_V2
            ]
            for record in records
        ),
    }

    comparison = (
        _comparison_summary(
            records
        )
    )

    safety_summary = {
        "unsafe_auto_answer_on_expected_abstention": (
            unsafe_expected_abstention
        ),
        "unsafe_lifecycle_auto_answer": (
            unsafe_lifecycle
        ),
    }

    cost_summary = {
        ARCHITECTURE_V1: {
            "total_hybrid_calls": (
                v1_hybrid_calls
            ),
        },
        ARCHITECTURE_V2: {
            "total_hybrid_calls": (
                v2_hybrid_calls
            ),
            "additional_hybrid_calls_over_v1": (
                v2_hybrid_calls
                - v1_hybrid_calls
            ),
            "relationship_expansion_cases": (
                v2_relationship_expansions
            ),
            "rrf_pool_calls": (
                v2_rrf_pool_calls
            ),
        },
    }

    output = {
        "benchmark_question": (
            "Does Architecture v2 retrieve better evidence than "
            "Architecture v1 without increasing unsafe behaviour?"
        ),
        "dataset": {
            "total_cases": len(
                cases
            ),
            "labelled_relevance_cases": sum(
                1
                for case in cases
                if (
                    case.get(
                        "expected_document_id"
                    )
                    or case.get(
                        "expected_document_ids"
                    )
                )
            ),
            "expected_abstention_cases": sum(
                1
                for case in cases
                if case.get(
                    "expected_abstention",
                    False,
                )
            ),
        },
        "retrieval_summary": (
            retrieval_summary
        ),
        "evidence_summary": (
            evidence_summary
        ),
        "governance_summary": (
            governance_summary
        ),
        "comparison": comparison,
        "safety_summary": (
            safety_summary
        ),
        "route_summary": {
            "routes": dict(
                route_counts
            ),
            "stop_reasons": dict(
                route_stop_reasons
            ),
        },
        "cost_summary": (
            cost_summary
        ),
        "latency_seconds": (
            latency_summary
        ),
        "case_results": records,
        "input_sha256": hashes,
        "configuration": {
            "semantic_k": (
                baseline.SEMANTIC_K
            ),
            "keyword_k": (
                baseline.KEYWORD_K
            ),
            "final_k": (
                baseline.FINAL_K
            ),
            "semantic_min_similarity": (
                baseline.SEMANTIC_MIN_SIMILARITY
            ),
            "keyword_min_score": (
                baseline.KEYWORD_MIN_SCORE
            ),
            "min_rrf_score": (
                baseline.MIN_RRF_SCORE
            ),
            "embedding_model": (
                model_name
            ),
            "relationship_max_related_chunks": 2,
            "architecture_v2_max_enhancement_routes": 1,
        },
        "total_benchmark_seconds": (
            perf_counter()
            - benchmark_start
        ),
        "controlled_synthetic_benchmark": True,
    }

    # --------------------------------------------------------
    # SAVE COMPACT OUTPUT
    # --------------------------------------------------------

    path = (
        baseline.PROJECT_ROOT
        / "outputs"
        / "week21_day6_architecture_v1_v2_benchmark.json"
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
        "=" * 60
    )

    print(
        "DAY 6 SUMMARY"
    )

    print(
        "=" * 60
    )

    print(
        json.dumps(
            {
                "dataset": output[
                    "dataset"
                ],
                "retrieval_summary": (
                    retrieval_summary
                ),
                "evidence_summary": (
                    evidence_summary
                ),
                "governance_summary": (
                    governance_summary
                ),
                "comparison": comparison,
                "safety_summary": (
                    safety_summary
                ),
                "route_summary": (
                    output[
                        "route_summary"
                    ]
                ),
                "cost_summary": (
                    cost_summary
                ),
                "latency_seconds": (
                    latency_summary
                ),
                "total_benchmark_seconds": (
                    output[
                        "total_benchmark_seconds"
                    ]
                ),
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