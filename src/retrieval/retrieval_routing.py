"""Deterministic routing diagnosis for Architecture v2 retrieval.

This module decides which retrieval capability should be used after
initial Hybrid retrieval and evidence assessment.

It does not:
- perform retrieval;
- generate answers;
- make governance approval decisions;
- alter document lifecycle;
- bypass evidence sufficiency;
- invoke an LLM.

The router is intentionally deterministic and auditable.
"""

from __future__ import annotations

from collections.abc import Callable

from src.retrieval.document_relationships import (
    get_relationships_for_document,
)
from src.retrieval.evidence_sufficiency import (
    get_evidence_topic_diagnostics,
)
from src.retrieval.query_refinement import (
    refine_query_for_missing_topic,
)


ROUTE_RETURN_INITIAL = "RETURN_INITIAL"
ROUTE_RELATIONSHIP_AWARE = "RELATIONSHIP_AWARE"
ROUTE_BOUNDED_AGENTIC = "BOUNDED_AGENTIC"
ROUTE_HYBRID_RESCUE = "HYBRID_RESCUE"
ROUTE_STOP_INSUFFICIENT = "STOP_INSUFFICIENT"


SUPPORTED_ROUTES = {
    ROUTE_RETURN_INITIAL,
    ROUTE_RELATIONSHIP_AWARE,
    ROUTE_BOUNDED_AGENTIC,
    ROUTE_HYBRID_RESCUE,
    ROUTE_STOP_INSUFFICIENT,
}


HARD_BLOCKED_CLAIM_TYPES = {
    "current_external_claim",
    "contradiction_or_precedence_claim",
}


RELATIONSHIP_CLAIM_TYPE = "relationship_claim"


QueryRefiner = Callable[
    [str, dict],
    str | None,
]


def _validate_query(
    query: str,
) -> str:
    """Return a normalised non-empty query."""

    if not isinstance(query, str):
        raise TypeError(
            "query must be a string"
        )

    normalised = " ".join(
        query.split()
    )

    if not normalised:
        raise ValueError(
            "query must not be empty"
        )

    return normalised


def _validate_initial_results(
    initial_results: list[dict],
) -> None:
    """Validate the initial retrieval result collection."""

    if not isinstance(initial_results, list):
        raise TypeError(
            "initial_results must be a list"
        )

    for result in initial_results:
        if not isinstance(result, dict):
            raise TypeError(
                "each initial retrieval result must be a dictionary"
            )


def _validate_assessment(
    assessment: dict,
) -> None:
    """Validate the evidence assessment container."""

    if not isinstance(assessment, dict):
        raise TypeError(
            "assessment must be a dictionary"
        )

    if "sufficient" not in assessment:
        raise ValueError(
            "assessment must contain 'sufficient'"
        )

    if not isinstance(
        assessment["sufficient"],
        bool,
    ):
        raise TypeError(
            "assessment['sufficient'] must be a boolean"
        )


def _unsupported_claims(
    assessment: dict,
) -> list[dict]:
    """Return well-formed unsupported claim dictionaries."""

    unsupported = assessment.get(
        "unsupported_claims",
        [],
    )

    if unsupported is None:
        return []

    if not isinstance(unsupported, list):
        raise TypeError(
            "unsupported_claims must be a list"
        )

    return [
        claim
        for claim in unsupported
        if isinstance(claim, dict)
    ]


def _unsupported_claim_types(
    assessment: dict,
) -> list[str]:
    """Return unique unsupported claim types in stable order."""

    claim_types: list[str] = []

    for claim in _unsupported_claims(
        assessment
    ):
        claim_type = claim.get(
            "type"
        )

        if (
            isinstance(claim_type, str)
            and claim_type
            and claim_type not in claim_types
        ):
            claim_types.append(
                claim_type
            )

    return claim_types


def _has_hard_blocked_claim(
    assessment: dict,
) -> bool:
    """Return True when a known hard-block claim is unsupported."""

    return any(
        claim_type in HARD_BLOCKED_CLAIM_TYPES
        for claim_type in _unsupported_claim_types(
            assessment
        )
    )


def _has_unsupported_relationship_claim(
    assessment: dict,
) -> bool:
    """Return True when relationship evidence is still unsupported."""

    return (
        RELATIONSHIP_CLAIM_TYPE
        in _unsupported_claim_types(
            assessment
        )
    )


def _document_ids(
    initial_results: list[dict],
) -> list[str]:
    """Return unique document IDs from initial results."""

    document_ids: list[str] = []

    for result in initial_results:
        document_id = result.get(
            "document_id"
        )

        if (
            isinstance(document_id, str)
            and document_id.strip()
        ):
            normalised = (
                document_id.strip().upper()
            )

            if normalised not in document_ids:
                document_ids.append(
                    normalised
                )

    return document_ids


def _relationship_available(
    initial_results: list[dict],
) -> bool:
    """Return True when retrieved documents have an Active relationship.

    The relationship registry is used only as a navigation signal.
    It is not treated as proof that the relationship claim is true.
    """

    for document_id in _document_ids(
        initial_results
    ):
        relationships = (
            get_relationships_for_document(
                document_id,
                active_only=True,
            )
        )

        if relationships:
            return True

    return False


def _recoverable_refinement_available(
    query: str,
    diagnostics: dict,
    query_refiner: QueryRefiner,
) -> bool:
    """Return True when deterministic query refinement is available."""

    if not callable(query_refiner):
        raise TypeError(
            "query_refiner must be callable"
        )

    missing_topics = diagnostics.get(
        "missing_topics",
        [],
    )

    if not isinstance(missing_topics, list):
        raise TypeError(
            "diagnostics['missing_topics'] must be a list"
        )

    if not missing_topics:
        return False

    refined_query = query_refiner(
        query,
        diagnostics,
    )

    if (
        refined_query is None
        or not isinstance(
            refined_query,
            str,
        )
        or not refined_query.strip()
    ):
        return False

    refined_normalised = " ".join(
        refined_query.split()
    )

    return (
        refined_normalised.lower()
        != query.lower()
    )


def diagnose_retrieval_route(
    query: str,
    initial_results: list[dict],
    assessment: dict,
    *,
    query_refiner: QueryRefiner = (
        refine_query_for_missing_topic
    ),
) -> dict:
    """Choose one deterministic retrieval route.

    Routing priority:

    1. sufficient evidence -> RETURN_INITIAL
    2. hard-blocked unsupported claim -> STOP_INSUFFICIENT
    3. unsupported relationship claim with registry navigation
       -> RELATIONSHIP_AWARE
    4. recoverable deterministic missing-topic gap
       -> BOUNDED_AGENTIC
    5. otherwise, if retrieval produced evidence
       -> HYBRID_RESCUE
    6. no evidence / no recoverable path
       -> STOP_INSUFFICIENT

    This function diagnoses only. It performs no retrieval.
    """

    query = _validate_query(
        query
    )

    _validate_initial_results(
        initial_results
    )

    _validate_assessment(
        assessment
    )

    unsupported_types = (
        _unsupported_claim_types(
            assessment
        )
    )

    diagnostics = (
        get_evidence_topic_diagnostics(
            query,
            initial_results,
        )
    )

    missing_topics = diagnostics.get(
        "missing_topics",
        [],
    )

    if assessment["sufficient"]:
        route = ROUTE_RETURN_INITIAL
        reason = (
            "Initial Hybrid evidence is sufficient; "
            "no retrieval expansion is required."
        )

    elif _has_hard_blocked_claim(
        assessment
    ):
        route = ROUTE_STOP_INSUFFICIENT
        reason = (
            "Evidence contains an unsupported hard-blocked "
            "claim requirement that local retrieval refinement "
            "must not attempt to repair."
        )

    elif (
        _has_unsupported_relationship_claim(
            assessment
        )
        and _relationship_available(
            initial_results
        )
    ):
        route = ROUTE_RELATIONSHIP_AWARE
        reason = (
            "A relationship claim is unsupported and an "
            "Active registered document relationship is "
            "available for bounded evidence navigation."
        )

    elif _recoverable_refinement_available(
        query,
        diagnostics,
        query_refiner,
    ):
        route = ROUTE_BOUNDED_AGENTIC
        reason = (
            "Evidence is insufficient and a deterministic "
            "refined query can target a missing evidence topic."
        )

    elif initial_results:
        route = ROUTE_HYBRID_RESCUE
        reason = (
            "Evidence remains insufficient, but no relationship "
            "or deterministic refined-query route applies; "
            "same-query deeper evidence rescue may be attempted."
        )

    else:
        route = ROUTE_STOP_INSUFFICIENT
        reason = (
            "No initial evidence and no recoverable deterministic "
            "retrieval route are available."
        )

    return {
        "route": route,
        "reason": reason,
        "initial_evidence_sufficient": (
            assessment["sufficient"]
        ),
        "missing_topics": list(
            missing_topics
        ),
        "unsupported_claim_types": (
            unsupported_types
        ),
        "relationship_claim_unsupported": (
            _has_unsupported_relationship_claim(
                assessment
            )
        ),
        "relationship_available": (
            _relationship_available(
                initial_results
            )
        ),
    }