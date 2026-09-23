"""Experimental, evidence-gated rescue; not the default hybrid path."""
from __future__ import annotations

from src.retrieval.evidence_sufficiency import assess_evidence_sufficiency
from src.retrieval.hybrid_search import DEFAULT_RRF_K, hybrid_search
from src.retrieval.hybrid_search_rrf_only import hybrid_search_rrf_only


def hybrid_search_evidence_rescue(
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
) -> dict:
    """Return results plus audit; callers must honour final_evidence.

    Sufficient initial results are returned unchanged. Otherwise inspect the
    full available RRF pool at the same retrieval depths and thresholds.
    Accept only strict coverage gains without losing an already covered topic.
    When full, replace the weakest replaceable result, retaining original order.
    This greedy experiment may miss combinations requiring temporary coverage loss.
    Scope checks remain the caller's responsibility; both retrieval paths retain
    their existing lifecycle filtering. No input result dictionaries are mutated.
    """
    options = dict(
        query=query, chunks=chunks, embedded_chunks=embedded_chunks,
        model=model, embedding_model=embedding_model,
        semantic_k=semantic_k, keyword_k=keyword_k,
        semantic_min_similarity=semantic_min_similarity,
        keyword_min_score=keyword_min_score, min_rrf_score=min_rrf_score,
        rrf_k=rrf_k,
    )
    initial = hybrid_search(**options, final_k=final_k)
    initial_evidence = assess_evidence_sufficiency(query, initial)
    results = initial
    final_evidence = initial_evidence
    pool = []
    attempted = not initial_evidence["sufficient"]
    if attempted:
        pool = hybrid_search_rrf_only(
            **options, final_k=max(final_k, semantic_k + keyword_k),
        )
        results = list(initial)
        for candidate in pool:
            if any(r["chunk_id"] == candidate["chunk_id"] for r in results):
                continue
            covered = set(final_evidence["matched_query_terms"])
            # Do not replace evidence with a candidate that adds no topic.
            candidate_topics = set(assess_evidence_sufficiency(
                query, [candidate],
            )["matched_query_terms"])
            if not candidate_topics - covered:
                continue
            slots = [None] if len(results) < final_k else reversed(range(len(results)))
            for slot in slots:
                proposal = list(results)
                if slot is not None:
                    proposal.pop(slot)
                proposal.append(candidate)
                assessment = assess_evidence_sufficiency(query, proposal)
                if set(assessment["matched_query_terms"]) > covered:
                    results, final_evidence = proposal, assessment
                    break
            if final_evidence["sufficient"]:
                break
        final_evidence = assess_evidence_sufficiency(query, results)

    original_ids = {r["chunk_id"] for r in initial}
    added = [r for r in results if r["chunk_id"] not in original_ids]
    return {
        "results": results,
        "audit": {
            "initial_evidence": initial_evidence,
            "rescue_attempted": attempted,
            "rescued_document_ids": list(dict.fromkeys(r["document_id"] for r in added)),
            "rescued_chunk_ids": [r["chunk_id"] for r in added],
            "final_evidence": final_evidence,
            "initial_results": initial,
            "rrf_candidates": pool,
        },
    }
