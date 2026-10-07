"""Deterministic Architecture v2 retrieval orchestrator.

The orchestrator:

1. applies the query scope gate;
2. performs one initial Hybrid retrieval;
3. assesses evidence sufficiency;
4. asks the deterministic routing layer which single enhancement
   path, if any, should run;
5. executes at most one enhancement route;
6. reassesses final evidence against the ORIGINAL question.

Supported enhancement routes:

- RELATIONSHIP_AWARE
- BOUNDED_AGENTIC
- HYBRID_RESCUE

The orchestrator does not:
- use an LLM to choose tools;
- chain multiple enhancement routes;
- approve an answer;
- bypass lifecycle controls;
- bypass downstream governance.
"""

from __future__ import annotations

from src.retrieval.bounded_agentic_retrieval import (
    continue_bounded_agentic_retrieval,
)
from src.retrieval.evidence_sufficiency import (
    assess_evidence_sufficiency,
)
from src.retrieval.hybrid_search import (
    DEFAULT_RRF_K,
    hybrid_search,
)
from src.retrieval.hybrid_search_evidence_rescue import (
    continue_hybrid_search_evidence_rescue,
)
from src.retrieval.query_refinement import (
    refine_query_for_missing_topic,
)
from src.retrieval.query_scope import (
    assess_query_scope,
)
from src.retrieval.relationship_aware_retrieval import (
    expand_results_with_relationships,
)
from src.retrieval.retrieval_routing import (
    ROUTE_BOUNDED_AGENTIC,
    ROUTE_HYBRID_RESCUE,
    ROUTE_RELATIONSHIP_AWARE,
    ROUTE_RETURN_INITIAL,
    ROUTE_STOP_INSUFFICIENT,
    diagnose_retrieval_route,
)


def orchestrate_retrieval(
    query: str,
    chunks: list[dict],
    embedded_chunks: list[dict],
    model,
    embedding_model: str,
    semantic_k: int = 10,
    keyword_k: int = 10,
    final_k: int = 3,
    semantic_min_similarity: float | None = None,
    keyword_min_score: float | None = None,
    min_rrf_score: float | None = None,
    rrf_k: int = DEFAULT_RRF_K,
    *,
    max_related_chunks: int = 2,
    query_refiner=refine_query_for_missing_topic,
) -> dict:
    """Run one bounded retrieval-orchestration decision.

    Exactly one initial Hybrid retrieval is performed for an in-scope
    query.

    After deterministic diagnosis, at most one enhancement route is
    executed.

    Final evidence is always assessed against the ORIGINAL query.
    """

    scope = assess_query_scope(
        query
    )

    if not scope[
        "allowed"
    ]:
        return {
            "results": [],
            "audit": {
                "original_query": query,
                "scope": scope,
                "initial_retrieval_call_count": 0,
                "selected_route": (
                    "STOP_OUT_OF_SCOPE"
                ),
                "routing_decision": None,
                "route_audit": None,
                "final_evidence": None,
                "total_hybrid_retrieval_calls": 0,
                "stop_reason": (
                    "ORIGINAL_QUERY_OUT_OF_SCOPE"
                ),
            },
        }

    initial_results = hybrid_search(
        query=query,
        chunks=chunks,
        embedded_chunks=embedded_chunks,
        model=model,
        embedding_model=embedding_model,
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
        relevance_scorer=None,
    )

    initial_evidence = (
        assess_evidence_sufficiency(
            query,
            initial_results,
        )
    )

    routing_decision = (
        diagnose_retrieval_route(
            query,
            initial_results,
            initial_evidence,
            query_refiner=query_refiner,
        )
    )

    route = routing_decision[
        "route"
    ]

    final_results = initial_results
    final_evidence = initial_evidence
    route_audit = None
    total_hybrid_calls = 1

    if route == ROUTE_RETURN_INITIAL:
        stop_reason = (
            "INITIAL_EVIDENCE_SUFFICIENT"
        )

    elif route == ROUTE_STOP_INSUFFICIENT:
        stop_reason = (
            "NO_SAFE_RETRIEVAL_EXPANSION"
        )

    elif route == ROUTE_RELATIONSHIP_AWARE:
        relationship_output = (
            expand_results_with_relationships(
                initial_results,
                chunks,
                max_related_chunks=(
                    max_related_chunks
                ),
            )
        )

        final_results = (
            relationship_output[
                "results"
            ]
        )

        route_audit = (
            relationship_output[
                "audit"
            ]
        )

        final_evidence = (
            assess_evidence_sufficiency(
                query,
                final_results,
            )
        )

        if final_evidence[
            "sufficient"
        ]:
            stop_reason = (
                "EVIDENCE_SUFFICIENT_AFTER_RELATIONSHIP_EXPANSION"
            )
        else:
            stop_reason = (
                "RELATIONSHIP_EXPANSION_COMPLETE"
            )

    elif route == ROUTE_BOUNDED_AGENTIC:
        agentic_output = (
            continue_bounded_agentic_retrieval(
                query=query,
                initial_results=initial_results,
                chunks=chunks,
                embedded_chunks=embedded_chunks,
                model=model,
                embedding_model=embedding_model,
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
                query_refiner=query_refiner,
            )
        )

        final_results = (
            agentic_output[
                "results"
            ]
        )

        route_audit = (
            agentic_output[
                "audit"
            ]
        )

        final_evidence = (
            route_audit[
                "final_evidence"
            ]
        )

        total_hybrid_calls += (
            route_audit.get(
                "additional_retrieval_call_count",
                0,
            )
        )

        stop_reason = (
            route_audit[
                "stop_reason"
            ]
        )

    elif route == ROUTE_HYBRID_RESCUE:
        rescue_output = (
            continue_hybrid_search_evidence_rescue(
                query=query,
                initial_results=initial_results,
                chunks=chunks,
                embedded_chunks=embedded_chunks,
                model=model,
                embedding_model=embedding_model,
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
            )
        )

        rescue_audit = (
            rescue_output[
                "audit"
            ]
        )

        final_results = (
            rescue_output[
                "results"
            ]
        )

        final_evidence = (
            rescue_audit[
                "final_evidence"
            ]
        )

        route_audit = (
            rescue_audit
        )

        total_hybrid_calls += (
            rescue_audit.get(
                "additional_hybrid_retrieval_call_count",
                0,
            )
        )

        if final_evidence[
            "sufficient"
        ]:
            stop_reason = (
                "EVIDENCE_SUFFICIENT_AFTER_RESCUE"
            )
        else:
            stop_reason = (
                "RESCUE_COMPLETE"
            )

    else:
        raise RuntimeError(
            f"Unsupported retrieval route: {route}"
        )

    return {
        "results": final_results,
        "audit": {
            "original_query": query,
            "scope": scope,
            "initial_retrieval_call_count": 1,
            "initial_evidence": (
                initial_evidence
            ),
            "selected_route": route,
            "routing_decision": (
                routing_decision
            ),
            "route_audit": (
                route_audit
            ),
            "final_evidence": (
                final_evidence
            ),
            "total_hybrid_retrieval_calls": (
                total_hybrid_calls
            ),
            "stop_reason": (
                stop_reason
            ),
        },
    }