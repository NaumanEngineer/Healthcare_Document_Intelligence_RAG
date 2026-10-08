"""Structured evidence object construction.

Week 22 Day 1.

This module converts retrieval-result chunks into deterministic,
traceable evidence objects.

Important design rule:

The evidence object preserves source evidence and provenance.
It does not generate new claims, summaries, recommendations,
or confidence values.
"""

from __future__ import annotations


REQUIRED_EVIDENCE_FIELDS = (
    "document_id",
    "chunk_id",
    "title",
    "document_type",
    "source_type",
    "source_location",
    "source_file",
    "version",
    "effective_date",
    "status",
    "page",
    "chunk_number",
    "text",
    "extraction_status",
    "ingestion_batch_id",
)


SUPPORTED_EVIDENCE_ROLES = {
    "supporting",
    "relationship_evidence",
    "context",
}


OPTIONAL_RETRIEVAL_SCORE_FIELDS = (
    "similarity_score",
    "keyword_score",
    "rrf_score",
    "reranker_score",
)


def _require_non_empty_string(
    value,
    field_name: str,
) -> str:
    """Validate a required non-empty string field."""

    if (
        not isinstance(value, str)
        or not value.strip()
    ):
        raise ValueError(
            f"{field_name} must be a non-empty string"
        )

    return value.strip()


def _require_positive_integer(
    value,
    field_name: str,
) -> int:
    """Validate a required positive integer field."""

    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value <= 0
    ):
        raise ValueError(
            f"{field_name} must be a positive integer"
        )

    return value


def _validate_required_fields(
    chunk: dict,
) -> None:
    """Fail closed if required provenance is missing."""

    missing = [
        field
        for field in REQUIRED_EVIDENCE_FIELDS
        if field not in chunk
    ]

    if missing:
        raise ValueError(
            "Cannot create evidence object. "
            "Missing required fields: "
            + ", ".join(missing)
        )


def _extract_retrieval_scores(
    chunk: dict,
) -> dict:
    """Preserve retrieval scores only when they actually exist."""

    scores = {}

    for field in OPTIONAL_RETRIEVAL_SCORE_FIELDS:
        value = chunk.get(field)

        if isinstance(
            value,
            (int, float),
        ) and not isinstance(
            value,
            bool,
        ):
            scores[field] = value

    return scores


def build_evidence_object(
    chunk: dict,
    *,
    retrieval_route: str,
    evidence_role: str = "supporting",
) -> dict:
    """Create one deterministic evidence object.

    Parameters
    ----------
    chunk:
        Retrieval-result chunk containing canonical document
        metadata and provenance.

    retrieval_route:
        Architecture v2 route that produced or retained this
        evidence, for example RETURN_INITIAL, BOUNDED_AGENTIC,
        HYBRID_RESCUE, or RELATIONSHIP_AWARE.

    evidence_role:
        Functional role of the evidence in the evidence set.

    Returns
    -------
    dict
        Structured evidence object suitable for later evidence
        packet construction and governance.
    """

    if not isinstance(
        chunk,
        dict,
    ):
        raise TypeError(
            "chunk must be a dictionary"
        )

    _validate_required_fields(
        chunk
    )

    retrieval_route = (
        _require_non_empty_string(
            retrieval_route,
            "retrieval_route",
        )
    )

    if evidence_role not in SUPPORTED_EVIDENCE_ROLES:
        raise ValueError(
            "Unsupported evidence_role: "
            f"{evidence_role}"
        )

    document_id = (
        _require_non_empty_string(
            chunk["document_id"],
            "document_id",
        )
    )

    chunk_id = (
        _require_non_empty_string(
            chunk["chunk_id"],
            "chunk_id",
        )
    )

    evidence_text = (
        _require_non_empty_string(
            chunk["text"],
            "text",
        )
    )

    page = (
        _require_positive_integer(
            chunk["page"],
            "page",
        )
    )

    chunk_number = (
        _require_positive_integer(
            chunk["chunk_number"],
            "chunk_number",
        )
    )

    evidence_object = {
        "evidence_id": (
            f"EVIDENCE::{chunk_id}"
        ),
        "document_id": document_id,
        "chunk_id": chunk_id,
        "title": _require_non_empty_string(
            chunk["title"],
            "title",
        ),
        "document_type": (
            _require_non_empty_string(
                chunk["document_type"],
                "document_type",
            )
        ),
        "source_type": (
            _require_non_empty_string(
                chunk["source_type"],
                "source_type",
            )
        ),
        "source_location": (
            _require_non_empty_string(
                chunk["source_location"],
                "source_location",
            )
        ),
        "source_file": (
            _require_non_empty_string(
                chunk["source_file"],
                "source_file",
            )
        ),
        "version": (
            _require_non_empty_string(
                chunk["version"],
                "version",
            )
        ),
        "effective_date": (
            _require_non_empty_string(
                chunk["effective_date"],
                "effective_date",
            )
        ),
        "status": (
            _require_non_empty_string(
                chunk["status"],
                "status",
            )
        ),
        "page": page,
        "chunk_number": chunk_number,
        "evidence_text": evidence_text,
        "extraction_status": (
            _require_non_empty_string(
                chunk["extraction_status"],
                "extraction_status",
            )
        ),
        "ingestion_batch_id": (
            _require_non_empty_string(
                chunk["ingestion_batch_id"],
                "ingestion_batch_id",
            )
        ),
        "retrieval_route": retrieval_route,
        "evidence_role": evidence_role,
        "retrieval_scores": (
            _extract_retrieval_scores(
                chunk
            )
        ),
    }

    return evidence_object


def build_evidence_objects(
    chunks: list[dict],
    *,
    retrieval_route: str,
    evidence_role: str = "supporting",
) -> list[dict]:
    """Convert a retrieval result set into evidence objects."""

    if not isinstance(
        chunks,
        list,
    ):
        raise TypeError(
            "chunks must be a list"
        )

    return [
        build_evidence_object(
            chunk,
            retrieval_route=retrieval_route,
            evidence_role=evidence_role,
        )
        for chunk in chunks
    ]