"""Bounded deterministic retrieval refinement.

This module provides a small, auditable retrieval-feedback loop.

The controller:

1. runs ordinary Hybrid retrieval;
2. assesses evidence against the ORIGINAL question;
3. stops immediately when evidence is sufficient;
4. identifies deterministic missing-topic gaps;
5. optionally creates one refined query;
6. performs at most one additional Hybrid retrieval;
7. accepts new evidence only when deterministic coverage improves;
8. reassesses all final evidence against the ORIGINAL question.

It does not:
- use a frontier LLM;
- perform open-web search;
- alter lifecycle status;
- change evidence-sufficiency rules;
- change governance thresholds;
- approve an answer;
- bypass downstream governance.

For the first prototype, max_rounds means total Hybrid retrieval calls,
including the initial search. Supported values are 1 and 2.
"""

from __future__ import annotations

from collections.abc import Callable

from src.ingestion.chunk_metadata import (
    is_chunk_retrieval_eligible,
    validate_chunk_metadata,
)
from src.retrieval.evidence_sufficiency import (
    assess_evidence_sufficiency,
    get_evidence_topic_diagnostics,
)
from src.retrieval.hybrid_search import (
    DEFAULT_RRF_K,
    hybrid_search,
)
from src.retrieval.query_refinement import (
    refine_query_for_missing_topic,
)
from src.retrieval.query_scope import (
    assess_query_scope,
)


QueryRefiner = Callable[
    [str, dict],
    str | None,
]


HARD_BLOCKED_CLAIM_TYPES = {
    "current_external_claim",
    "contradiction_or_precedence_claim",
}


def _validate_max_rounds(
    max_rounds: int,
) -> None:
    """Validate the bounded retrieval-round limit."""

    if (
        not isinstance(max_rounds, int)
        or isinstance(max_rounds, bool)
        or max_rounds not in {1, 2}
    ):
        raise ValueError(
            "max_rounds must be either 1 or 2"
        )


def _validate_query_refiner(
    query_refiner: QueryRefiner,
) -> None:
    """Validate the injected deterministic query refiner."""

    if not callable(query_refiner):
        raise TypeError(
            "query_refiner must be callable"
        )


def _active_result_copy(
    result: dict,
) -> dict | None:
    """Return a copy of an Active retrieval result.

    Metadata is revalidated here so merged evidence has its own
    lifecycle boundary rather than relying only on upstream Hybrid
    retrieval.
    """

    validate_chunk_metadata(
        result
    )

    if not is_chunk_retrieval_eligible(
        result
    ):
        return None

    return dict(
        result
    )


def _active_results(
    results: list[dict],
) -> list[dict]:
    """Revalidate lifecycle safety for a result collection."""

    if not isinstance(results, list):
        raise TypeError(
            "results must be a list"
        )

    active: list[dict] = []

    for result in results:
        if not isinstance(result, dict):
            raise TypeError(
                "each retrieval result must be a dictionary"
            )

        copied = _active_result_copy(
            result
        )

        if copied is not None:
            active.append(
                copied
            )

    return active


def _result_chunk_id(
    result: dict,
) -> str:
    """Return a validated chunk identifier."""

    chunk_id = result.get(
        "chunk_id"
    )

    if (
        not isinstance(chunk_id, str)
        or not chunk_id.strip()
    ):
        raise ValueError(
            "retrieval result must contain a valid chunk_id"
        )

    return chunk_id


def _matched_topics(
    assessment: dict,
) -> set[str]:
    """Return matched evidence topics from an assessment."""

    matched = assessment.get(
        "matched_query_terms",
        [],
    )

    if not isinstance(matched, list):
        raise TypeError(
            "matched_query_terms must be a list"
        )

    return {
        value
        for value in matched
        if isinstance(value, str)
    }


def _supported_claim_ids(
    assessment: dict,
) -> set[str]:
    """Return claim IDs currently supported by the evidence set."""

    claims = assessment.get(
        "claim_requirements",
        [],
    )

    if claims is None:
        return set()

    if not isinstance(claims, list):
        raise TypeError(
            "claim_requirements must be a list"
        )

    supported: set[str] = set()

    for claim in claims:
        if not isinstance(claim, dict):
            continue

        claim_id = claim.get(
            "claim_id"
        )

        if (
            claim.get("supported") is True
            and isinstance(claim_id, str)
        ):
            supported.add(
                claim_id
            )

    return supported


def _has_hard_blocked_claim(
    assessment: dict,
) -> bool:
    """Return True when retrieval cannot repair a known hard block."""

    unsupported = assessment.get(
        "unsupported_claims",
        [],
    )

    if not isinstance(unsupported, list):
        return False

    for claim in unsupported:
        if not isinstance(claim, dict):
            continue

        if claim.get(
            "type"
        ) in HARD_BLOCKED_CLAIM_TYPES:
            return True

    return False


def _coverage_strictly_improves(
    before: dict,
    after: dict,
) -> bool:
    """Check whether a proposal adds topic coverage safely.

    A proposal is accepted only when:

    - matched topic coverage is a strict superset; and
    - every claim previously supported remains supported.
    """

    before_topics = _matched_topics(
        before
    )

    after_topics = _matched_topics(
        after
    )

    if not (
        after_topics > before_topics
    ):
        return False

    before_supported_claims = (
        _supported_claim_ids(
            before
        )
    )

    after_supported_claims = (
        _supported_claim_ids(
            after
        )
    )

    if not (
        before_supported_claims
        <= after_supported_claims
    ):
        return False

    return True


def _assign_final_ranks(
    results: list[dict],
) -> list[dict]:
    """Return copied results with final evidence-list ranks."""

    return [
        {
            **result,
            "rank": index,
        }
        for index, result in enumerate(
            results,
            start=1,
        )
    ]


def _build_improved_evidence_set(
    *,
    original_query: str,
    current_results: list[dict],
    refined_results: list[dict],
    final_k: int,
) -> tuple[
    list[dict],
    list[str],
    list[str],
    dict,
]:
    """Merge refined-query evidence without comparing cross-query scores.

    Candidates from the second retrieval round are considered in their
    own retrieval order.

    Semantic, keyword and RRF scores from different queries are never
    directly compared.

    A candidate is accepted only when the complete proposed evidence
    set gives a strict deterministic topic-coverage improvement against
    the ORIGINAL question while preserving previously supported claims.
    """

    working = _active_results(
        current_results
    )

    current_assessment = (
        assess_evidence_sufficiency(
            original_query,
            working,
        )
    )

    existing_chunk_ids = {
        _result_chunk_id(result)
        for result in working
    }

    accepted_chunk_ids: list[str] = []
    replaced_chunk_ids: list[str] = []

    for raw_candidate in refined_results:
        candidate = _active_result_copy(
            raw_candidate
        )

        if candidate is None:
            continue

        candidate_id = _result_chunk_id(
            candidate
        )

        if candidate_id in existing_chunk_ids:
            continue

        if len(working) < final_k:
            proposal = [
                *working,
                candidate,
            ]

            replaced_id = None

        else:
            proposal = None
            replaced_id = None

            # Do not compare ranking scores from different queries.
            # Try deterministic replacement from the end of the
            # existing evidence set toward the beginning.
            for position in range(
                len(working) - 1,
                -1,
                -1,
            ):
                candidate_proposal = [
                    dict(result)
                    for result in working
                ]

                candidate_proposal[
                    position
                ] = candidate

                candidate_proposal = (
                    _active_results(
                        candidate_proposal
                    )
                )

                proposal_assessment = (
                    assess_evidence_sufficiency(
                        original_query,
                        candidate_proposal,
                    )
                )

                if _coverage_strictly_improves(
                    current_assessment,
                    proposal_assessment,
                ):
                    proposal = (
                        candidate_proposal
                    )

                    replaced_id = (
                        _result_chunk_id(
                            working[
                                position
                            ]
                        )
                    )

                    break

        if proposal is None:
            continue

        proposal = _active_results(
            proposal
        )

        proposal_assessment = (
            assess_evidence_sufficiency(
                original_query,
                proposal,
            )
        )

        if not _coverage_strictly_improves(
            current_assessment,
            proposal_assessment,
        ):
            continue

        working = proposal
        current_assessment = (
            proposal_assessment
        )

        existing_chunk_ids = {
            _result_chunk_id(result)
            for result in working
        }

        accepted_chunk_ids.append(
            candidate_id
        )

        if replaced_id is not None:
            replaced_chunk_ids.append(
                replaced_id
            )

        if current_assessment.get(
            "sufficient"
        ) is True:
            break

    working = _active_results(
        working
    )

    if len(working) > final_k:
        working = working[
            :final_k
        ]

    working = _assign_final_ranks(
        working
    )

    final_assessment = (
        assess_evidence_sufficiency(
            original_query,
            working,
        )
    )

    return (
        working,
        accepted_chunk_ids,
        replaced_chunk_ids,
        final_assessment,
    )


def bounded_agentic_retrieval(
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
    query_refiner: QueryRefiner = (
        refine_query_for_missing_topic
    ),
    max_rounds: int = 2,
) -> dict:
    """Perform bounded deterministic retrieval refinement.

    max_rounds is the TOTAL number of Hybrid retrieval calls,
    including the initial search.

    The first prototype supports one or two rounds only.

    All evidence-sufficiency assessments are made against the ORIGINAL
    question, including evidence retrieved by a refined query.
    """

    _validate_max_rounds(
        max_rounds
    )

    _validate_query_refiner(
        query_refiner
    )

    original_scope = assess_query_scope(
        query
    )

    if not original_scope[
        "allowed"
    ]:
        return {
            "results": [],
            "audit": {
                "original_query": query,
                "original_scope": (
                    original_scope
                ),
                "initial_evidence": None,
                "rounds": [],
                "retrieval_call_count": 0,
                "stop_reason": (
                    "ORIGINAL_QUERY_OUT_OF_SCOPE"
                ),
                "final_evidence": None,
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

    initial_results = _active_results(
        initial_results
    )

    initial_results = _assign_final_ranks(
        initial_results
    )

    initial_evidence = (
        assess_evidence_sufficiency(
            query,
            initial_results,
        )
    )

    initial_diagnostics = (
        get_evidence_topic_diagnostics(
            query,
            initial_results,
        )
    )

    rounds = [
        {
            "round": 1,
            "query": query,
            "missing_topics": (
                initial_diagnostics[
                    "missing_topics"
                ]
            ),
            "retrieved_chunk_ids": [
                _result_chunk_id(result)
                for result in initial_results
            ],
            "accepted_chunk_ids": [
                _result_chunk_id(result)
                for result in initial_results
            ],
            "replaced_chunk_ids": [],
            "assessment": initial_evidence,
        }
    ]

    if initial_evidence[
        "sufficient"
    ]:
        return {
            "results": initial_results,
            "audit": {
                "original_query": query,
                "original_scope": (
                    original_scope
                ),
                "initial_evidence": (
                    initial_evidence
                ),
                "rounds": rounds,
                "retrieval_call_count": 1,
                "stop_reason": (
                    "INITIAL_EVIDENCE_SUFFICIENT"
                ),
                "final_evidence": (
                    initial_evidence
                ),
            },
        }

    if max_rounds == 1:
        return {
            "results": initial_results,
            "audit": {
                "original_query": query,
                "original_scope": (
                    original_scope
                ),
                "initial_evidence": (
                    initial_evidence
                ),
                "rounds": rounds,
                "retrieval_call_count": 1,
                "stop_reason": (
                    "MAX_ROUNDS_REACHED"
                ),
                "final_evidence": (
                    initial_evidence
                ),
            },
        }

    if _has_hard_blocked_claim(
        initial_evidence
    ):
        return {
            "results": initial_results,
            "audit": {
                "original_query": query,
                "original_scope": (
                    original_scope
                ),
                "initial_evidence": (
                    initial_evidence
                ),
                "rounds": rounds,
                "retrieval_call_count": 1,
                "stop_reason": (
                    "NO_RECOVERABLE_GAP"
                ),
                "final_evidence": (
                    initial_evidence
                ),
            },
        }

    missing_topics = (
        initial_diagnostics.get(
            "missing_topics",
            [],
        )
    )

    if not missing_topics:
        return {
            "results": initial_results,
            "audit": {
                "original_query": query,
                "original_scope": (
                    original_scope
                ),
                "initial_evidence": (
                    initial_evidence
                ),
                "rounds": rounds,
                "retrieval_call_count": 1,
                "stop_reason": (
                    "NO_RECOVERABLE_GAP"
                ),
                "final_evidence": (
                    initial_evidence
                ),
            },
        }

    try:
        refined_query = query_refiner(
            query,
            initial_diagnostics,
        )
    except Exception as exc:
        raise RuntimeError(
            "query refiner failed"
        ) from exc

    if (
        refined_query is None
        or not isinstance(
            refined_query,
            str,
        )
        or not refined_query.strip()
    ):
        return {
            "results": initial_results,
            "audit": {
                "original_query": query,
                "original_scope": (
                    original_scope
                ),
                "initial_evidence": (
                    initial_evidence
                ),
                "rounds": rounds,
                "retrieval_call_count": 1,
                "stop_reason": (
                    "REFINED_QUERY_INVALID"
                ),
                "final_evidence": (
                    initial_evidence
                ),
            },
        }

    refined_query = " ".join(
        refined_query.split()
    )

    if (
        refined_query.lower()
        == " ".join(
            query.split()
        ).lower()
    ):
        return {
            "results": initial_results,
            "audit": {
                "original_query": query,
                "original_scope": (
                    original_scope
                ),
                "initial_evidence": (
                    initial_evidence
                ),
                "rounds": rounds,
                "retrieval_call_count": 1,
                "stop_reason": (
                    "REFINED_QUERY_INVALID"
                ),
                "final_evidence": (
                    initial_evidence
                ),
            },
        }

    refined_scope = assess_query_scope(
        refined_query
    )

    if not refined_scope[
        "allowed"
    ]:
        return {
            "results": initial_results,
            "audit": {
                "original_query": query,
                "original_scope": (
                    original_scope
                ),
                "initial_evidence": (
                    initial_evidence
                ),
                "rounds": rounds,
                "retrieval_call_count": 1,
                "stop_reason": (
                    "REFINED_QUERY_OUT_OF_SCOPE"
                ),
                "final_evidence": (
                    initial_evidence
                ),
            },
        }

    try:
        refined_results = hybrid_search(
            query=refined_query,
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
    except Exception as exc:
        raise RuntimeError(
            "refined retrieval failed"
        ) from exc

    refined_results = _active_results(
        refined_results
    )

    (
        final_results,
        accepted_chunk_ids,
        replaced_chunk_ids,
        final_evidence,
    ) = _build_improved_evidence_set(
        original_query=query,
        current_results=initial_results,
        refined_results=refined_results,
        final_k=final_k,
    )

    rounds.append(
        {
            "round": 2,
            "query": refined_query,
            "missing_topics": (
                get_evidence_topic_diagnostics(
                    query,
                    final_results,
                )[
                    "missing_topics"
                ]
            ),
            "retrieved_chunk_ids": [
                _result_chunk_id(result)
                for result in refined_results
            ],
            "accepted_chunk_ids": (
                accepted_chunk_ids
            ),
            "replaced_chunk_ids": (
                replaced_chunk_ids
            ),
            "assessment": final_evidence,
        }
    )

    if final_evidence[
        "sufficient"
    ]:
        stop_reason = (
            "EVIDENCE_SUFFICIENT_AFTER_REFINEMENT"
        )

    elif accepted_chunk_ids:
        stop_reason = (
            "MAX_ROUNDS_REACHED"
        )

    else:
        stop_reason = (
            "NO_COVERAGE_IMPROVEMENT"
        )

    return {
        "results": final_results,
        "audit": {
            "original_query": query,
            "original_scope": (
                original_scope
            ),
            "initial_evidence": (
                initial_evidence
            ),
            "rounds": rounds,
            "retrieval_call_count": 2,
            "stop_reason": stop_reason,
            "final_evidence": (
                final_evidence
            ),
        },
    }
def continue_bounded_agentic_retrieval(
    query: str,
    initial_results: list[dict],
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
    query_refiner: QueryRefiner = (
        refine_query_for_missing_topic
    ),
) -> dict:
    """Continue bounded Agentic retrieval from existing Hybrid results.

    This function is intended for a higher-level retrieval orchestrator
    that has already:

    1. passed the original query through the scope gate; and
    2. performed the initial Hybrid retrieval.

    It therefore does NOT repeat the initial Hybrid search.

    At most one additional Hybrid retrieval is performed using a
    deterministic refined query.

    All final evidence is reassessed against the ORIGINAL question.
    """

    _validate_query_refiner(
        query_refiner
    )

    original_scope = assess_query_scope(
        query
    )

    if not original_scope[
        "allowed"
    ]:
        return {
            "results": [],
            "audit": {
                "original_query": query,
                "original_scope": original_scope,
                "initial_retrieval_reused": True,
                "initial_evidence": None,
                "rounds": [],
                "additional_retrieval_call_count": 0,
                "stop_reason": (
                    "ORIGINAL_QUERY_OUT_OF_SCOPE"
                ),
                "final_evidence": None,
            },
        }

    initial_results = _active_results(
        initial_results
    )

    initial_results = _assign_final_ranks(
        initial_results
    )

    initial_evidence = (
        assess_evidence_sufficiency(
            query,
            initial_results,
        )
    )

    initial_diagnostics = (
        get_evidence_topic_diagnostics(
            query,
            initial_results,
        )
    )

    rounds = [
        {
            "round": 1,
            "query": query,
            "missing_topics": (
                initial_diagnostics[
                    "missing_topics"
                ]
            ),
            "retrieved_chunk_ids": [
                _result_chunk_id(result)
                for result in initial_results
            ],
            "accepted_chunk_ids": [
                _result_chunk_id(result)
                for result in initial_results
            ],
            "replaced_chunk_ids": [],
            "assessment": initial_evidence,
        }
    ]

    if initial_evidence[
        "sufficient"
    ]:
        return {
            "results": initial_results,
            "audit": {
                "original_query": query,
                "original_scope": original_scope,
                "initial_retrieval_reused": True,
                "initial_evidence": (
                    initial_evidence
                ),
                "rounds": rounds,
                "additional_retrieval_call_count": 0,
                "stop_reason": (
                    "INITIAL_EVIDENCE_SUFFICIENT"
                ),
                "final_evidence": (
                    initial_evidence
                ),
            },
        }

    if _has_hard_blocked_claim(
        initial_evidence
    ):
        return {
            "results": initial_results,
            "audit": {
                "original_query": query,
                "original_scope": original_scope,
                "initial_retrieval_reused": True,
                "initial_evidence": (
                    initial_evidence
                ),
                "rounds": rounds,
                "additional_retrieval_call_count": 0,
                "stop_reason": (
                    "NO_RECOVERABLE_GAP"
                ),
                "final_evidence": (
                    initial_evidence
                ),
            },
        }

    missing_topics = (
        initial_diagnostics.get(
            "missing_topics",
            [],
        )
    )

    if not missing_topics:
        return {
            "results": initial_results,
            "audit": {
                "original_query": query,
                "original_scope": original_scope,
                "initial_retrieval_reused": True,
                "initial_evidence": (
                    initial_evidence
                ),
                "rounds": rounds,
                "additional_retrieval_call_count": 0,
                "stop_reason": (
                    "NO_RECOVERABLE_GAP"
                ),
                "final_evidence": (
                    initial_evidence
                ),
            },
        }

    try:
        refined_query = query_refiner(
            query,
            initial_diagnostics,
        )
    except Exception as exc:
        raise RuntimeError(
            "query refiner failed"
        ) from exc

    if (
        refined_query is None
        or not isinstance(
            refined_query,
            str,
        )
        or not refined_query.strip()
    ):
        return {
            "results": initial_results,
            "audit": {
                "original_query": query,
                "original_scope": original_scope,
                "initial_retrieval_reused": True,
                "initial_evidence": (
                    initial_evidence
                ),
                "rounds": rounds,
                "additional_retrieval_call_count": 0,
                "stop_reason": (
                    "REFINED_QUERY_INVALID"
                ),
                "final_evidence": (
                    initial_evidence
                ),
            },
        }

    refined_query = " ".join(
        refined_query.split()
    )

    if (
        refined_query.lower()
        == " ".join(
            query.split()
        ).lower()
    ):
        return {
            "results": initial_results,
            "audit": {
                "original_query": query,
                "original_scope": original_scope,
                "initial_retrieval_reused": True,
                "initial_evidence": (
                    initial_evidence
                ),
                "rounds": rounds,
                "additional_retrieval_call_count": 0,
                "stop_reason": (
                    "REFINED_QUERY_INVALID"
                ),
                "final_evidence": (
                    initial_evidence
                ),
            },
        }

    refined_scope = assess_query_scope(
        refined_query
    )

    if not refined_scope[
        "allowed"
    ]:
        return {
            "results": initial_results,
            "audit": {
                "original_query": query,
                "original_scope": original_scope,
                "initial_retrieval_reused": True,
                "initial_evidence": (
                    initial_evidence
                ),
                "rounds": rounds,
                "additional_retrieval_call_count": 0,
                "stop_reason": (
                    "REFINED_QUERY_OUT_OF_SCOPE"
                ),
                "final_evidence": (
                    initial_evidence
                ),
            },
        }

    try:
        refined_results = hybrid_search(
            query=refined_query,
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
    except Exception as exc:
        raise RuntimeError(
            "refined retrieval failed"
        ) from exc

    refined_results = _active_results(
        refined_results
    )

    (
        final_results,
        accepted_chunk_ids,
        replaced_chunk_ids,
        final_evidence,
    ) = _build_improved_evidence_set(
        original_query=query,
        current_results=initial_results,
        refined_results=refined_results,
        final_k=final_k,
    )

    rounds.append(
        {
            "round": 2,
            "query": refined_query,
            "missing_topics": (
                get_evidence_topic_diagnostics(
                    query,
                    final_results,
                )[
                    "missing_topics"
                ]
            ),
            "retrieved_chunk_ids": [
                _result_chunk_id(result)
                for result in refined_results
            ],
            "accepted_chunk_ids": (
                accepted_chunk_ids
            ),
            "replaced_chunk_ids": (
                replaced_chunk_ids
            ),
            "assessment": final_evidence,
        }
    )

    if final_evidence[
        "sufficient"
    ]:
        stop_reason = (
            "EVIDENCE_SUFFICIENT_AFTER_REFINEMENT"
        )

    elif accepted_chunk_ids:
        stop_reason = (
            "MAX_ROUNDS_REACHED"
        )

    else:
        stop_reason = (
            "NO_COVERAGE_IMPROVEMENT"
        )

    return {
        "results": final_results,
        "audit": {
            "original_query": query,
            "original_scope": original_scope,
            "initial_retrieval_reused": True,
            "initial_evidence": (
                initial_evidence
            ),
            "rounds": rounds,
            "additional_retrieval_call_count": 1,
            "stop_reason": stop_reason,
            "final_evidence": (
                final_evidence
            ),
        },
    }











