"""Build structured evidence objects from Architecture v2 retrieval output.

Week 22 Day 1.

This module converts final retrieval results into evidence objects while
preserving the route selected by the retrieval orchestrator.

It does not make new retrieval decisions and does not change governance.
"""

from __future__ import annotations

from src.evidence.evidence_object import (
    build_evidence_objects,
)


def build_evidence_from_retrieval(
    retrieval_output: dict,
) -> list[dict]:
    """Convert Architecture v2 retrieval output into evidence objects."""

    if not isinstance(
        retrieval_output,
        dict,
    ):
        raise TypeError(
            "retrieval_output must be a dictionary"
        )

    if "results" not in retrieval_output:
        raise ValueError(
            "retrieval_output is missing results"
        )

    if "audit" not in retrieval_output:
        raise ValueError(
            "retrieval_output is missing audit"
        )

    results = retrieval_output[
        "results"
    ]

    audit = retrieval_output[
        "audit"
    ]

    if not isinstance(
        results,
        list,
    ):
        raise TypeError(
            "retrieval_output['results'] must be a list"
        )

    if not isinstance(
        audit,
        dict,
    ):
        raise TypeError(
            "retrieval_output['audit'] must be a dictionary"
        )

    route = audit.get(
        "selected_route"
    )

    if (
        not isinstance(route, str)
        or not route.strip()
    ):
        raise ValueError(
            "retrieval output is missing a valid selected_route"
        )

    final_evidence = audit.get(
        "final_evidence"
    )

    if not isinstance(
        final_evidence,
        dict,
    ):
        raise ValueError(
            "retrieval output is missing final_evidence"
        )

    if final_evidence.get(
        "sufficient"
    ) is not True:
        return []

    return build_evidence_objects(
        results,
        retrieval_route=route,
    )