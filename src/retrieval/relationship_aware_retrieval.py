"""Relationship-aware retrieval expansion.

This module expands an existing retrieval result set using explicit,
document-level relationships from the controlled relationship registry.

It does NOT:
- infer new relationships;
- treat the relationship registry as proof;
- bypass lifecycle controls;
- modify ordinary Hybrid retrieval;
- make governance decisions;
- validate that a relationship is supported by evidence.

The purpose is limited to:

1. inspect already retrieved document IDs;
2. find explicitly related Active documents;
3. identify Active relationship-evidence chunks;
4. retrieve eligible chunks from related documents;
5. add a bounded number of evidence-bearing and related chunks;
6. preserve an auditable expansion trail.

Final relationship claims must still be evaluated by the existing
governance relationship validator.
"""

from __future__ import annotations

from src.governance.evidence_set_relationship import (
    RELATIONSHIP_PATTERNS,
)
from src.ingestion.chunk_metadata import (
    is_chunk_retrieval_eligible,
    validate_chunk_metadata,
)
from src.retrieval.document_relationships import (
    get_relationships_for_document,
)


def _validate_results(
    results: list[dict],
) -> None:
    if not isinstance(results, list):
        raise TypeError(
            "results must be a list"
        )

    for result in results:
        if not isinstance(result, dict):
            raise TypeError(
                "each result must be a dictionary"
            )

        validate_chunk_metadata(result)


def _validate_chunks(
    chunks: list[dict],
) -> None:
    if not isinstance(chunks, list):
        raise TypeError(
            "chunks must be a list"
        )

    for chunk in chunks:
        if not isinstance(chunk, dict):
            raise TypeError(
                "each chunk must be a dictionary"
            )

        validate_chunk_metadata(chunk)


def _validate_max_related_chunks(
    max_related_chunks: int,
) -> None:
    if (
        not isinstance(max_related_chunks, int)
        or isinstance(max_related_chunks, bool)
    ):
        raise TypeError(
            "max_related_chunks must be an integer"
        )

    if max_related_chunks < 0:
        raise ValueError(
            "max_related_chunks must be >= 0"
        )


def _chunk_id(
    item: dict,
) -> str:
    chunk_id = item.get("chunk_id")

    if (
        not isinstance(chunk_id, str)
        or not chunk_id.strip()
    ):
        raise ValueError(
            "chunk must contain a valid chunk_id"
        )

    return chunk_id


def _document_id(
    item: dict,
) -> str:
    document_id = item.get("document_id")

    if (
        not isinstance(document_id, str)
        or not document_id.strip()
    ):
        raise ValueError(
            "chunk must contain a valid document_id"
        )

    return (
        document_id
        .strip()
        .upper()
    )


def _eligible_chunk_copy(
    chunk: dict,
) -> dict | None:
    validate_chunk_metadata(chunk)

    if not is_chunk_retrieval_eligible(
        chunk
    ):
        return None

    return dict(chunk)


def _existing_document_ids(
    results: list[dict],
) -> set[str]:
    return {
        _document_id(result)
        for result in results
    }


def _existing_chunk_ids(
    results: list[dict],
) -> set[str]:
    return {
        _chunk_id(result)
        for result in results
    }


def _collect_relationship_records(
    results: list[dict],
    *,
    relationship_type: str | None,
) -> list[dict]:
    source_document_ids = sorted(
        _existing_document_ids(
            results
        )
    )

    records: list[dict] = []

    for source_document_id in source_document_ids:
        relationships = (
            get_relationships_for_document(
                source_document_id,
                active_only=True,
            )
        )

        if relationship_type is not None:
            wanted = (
                relationship_type
                .strip()
                .upper()
            )

            relationships = [
                relationship
                for relationship in relationships
                if relationship[
                    "relationship_type"
                ] == wanted
            ]

        records.extend(
            relationships
        )

    return records


def _contains_relationship_term(
    chunk: dict,
    relationship_type: str,
) -> bool:
    text = chunk.get(
        "text",
        "",
    )

    if not isinstance(text, str):
        return False

    normalised_text = text.lower()

    patterns = RELATIONSHIP_PATTERNS.get(
        relationship_type,
        (),
    )

    return any(
        pattern.lower() in normalised_text
        for pattern in patterns
    )


def _relationship_evidence_candidates(
    chunks: list[dict],
    relationship_records: list[dict],
    *,
    excluded_chunk_ids: set[str],
) -> list[dict]:
    candidates: list[dict] = []

    seen_chunk_ids: set[str] = set()

    for relationship in relationship_records:
        evidence_document_id = relationship[
            "evidence_document_id"
        ]

        relationship_type = relationship[
            "relationship_type"
        ]

        for chunk in chunks:
            if (
                _document_id(chunk)
                != evidence_document_id
            ):
                continue

            chunk_id = _chunk_id(chunk)

            if chunk_id in excluded_chunk_ids:
                continue

            if chunk_id in seen_chunk_ids:
                continue

            copied = _eligible_chunk_copy(
                chunk
            )

            if copied is None:
                continue

            if not _contains_relationship_term(
                copied,
                relationship_type,
            ):
                continue

            candidates.append(
                copied
            )

            seen_chunk_ids.add(
                chunk_id
            )

    return candidates


def _related_document_candidates(
    chunks: list[dict],
    relationship_records: list[dict],
    *,
    excluded_document_ids: set[str],
    excluded_chunk_ids: set[str],
) -> list[dict]:
    related_document_ids = sorted(
        {
            relationship[
                "related_document_id"
            ]
            for relationship
            in relationship_records
            if relationship[
                "related_document_id"
            ]
            not in excluded_document_ids
        }
    )

    candidates: list[dict] = []

    for chunk in chunks:
        if (
            _document_id(chunk)
            not in related_document_ids
        ):
            continue

        chunk_id = _chunk_id(chunk)

        if chunk_id in excluded_chunk_ids:
            continue

        copied = _eligible_chunk_copy(
            chunk
        )

        if copied is None:
            continue

        candidates.append(
            copied
        )

    return candidates


def expand_results_with_relationships(
    results: list[dict],
    chunks: list[dict],
    *,
    relationship_type: str | None = None,
    max_related_chunks: int = 2,
) -> dict:
    """Expand results using controlled relationship metadata.

    Relationship-evidence chunks are prioritised before ordinary
    related-document chunks.

    The registry assists evidence discovery only. Downstream governance
    remains responsible for establishing whether the relationship is
    supported.
    """

    _validate_results(results)
    _validate_chunks(chunks)

    _validate_max_related_chunks(
        max_related_chunks
    )

    if (
        relationship_type is not None
        and not isinstance(
            relationship_type,
            str,
        )
    ):
        raise TypeError(
            "relationship_type must be a string or None"
        )

    initial_results: list[dict] = []

    for result in results:
        copied = _eligible_chunk_copy(
            result
        )

        if copied is not None:
            initial_results.append(
                copied
            )

    initial_chunk_ids = (
        _existing_chunk_ids(
            initial_results
        )
    )

    initial_document_ids = sorted(
        _existing_document_ids(
            initial_results
        )
    )

    if (
        not initial_results
        or max_related_chunks == 0
    ):
        return {
            "results": initial_results,
            "audit": {
                "initial_document_ids": (
                    initial_document_ids
                ),
                "relationship_type_filter": (
                    relationship_type
                ),
                "relationship_records": [],
                "relationship_evidence_candidate_ids": [],
                "related_candidate_ids": [],
                "accepted_chunk_ids": [],
                "expansion_count": 0,
                "stop_reason": (
                    "NO_EXPANSION_REQUESTED"
                    if max_related_chunks == 0
                    else "NO_INITIAL_ACTIVE_RESULTS"
                ),
            },
        }

    relationship_records = (
        _collect_relationship_records(
            initial_results,
            relationship_type=relationship_type,
        )
    )

    if not relationship_records:
        return {
            "results": initial_results,
            "audit": {
                "initial_document_ids": (
                    initial_document_ids
                ),
                "relationship_type_filter": (
                    relationship_type
                ),
                "relationship_records": [],
                "relationship_evidence_candidate_ids": [],
                "related_candidate_ids": [],
                "accepted_chunk_ids": [],
                "expansion_count": 0,
                "stop_reason": (
                    "NO_RELATED_DOCUMENTS"
                ),
            },
        }

    evidence_candidates = (
        _relationship_evidence_candidates(
            chunks,
            relationship_records,
            excluded_chunk_ids=(
                initial_chunk_ids
            ),
        )
    )

    evidence_candidate_ids = [
        _chunk_id(chunk)
        for chunk
        in evidence_candidates
    ]

    excluded_after_evidence = {
        *initial_chunk_ids,
        *evidence_candidate_ids,
    }

    related_candidates = (
        _related_document_candidates(
            chunks,
            relationship_records,
            excluded_document_ids=set(
                initial_document_ids
            ),
            excluded_chunk_ids=(
                excluded_after_evidence
            ),
        )
    )

    related_candidate_ids = [
        _chunk_id(chunk)
        for chunk
        in related_candidates
    ]

    ordered_candidates = [
        *evidence_candidates,
        *related_candidates,
    ]

    accepted = ordered_candidates[
        :max_related_chunks
    ]

    accepted_chunk_ids = [
        _chunk_id(chunk)
        for chunk
        in accepted
    ]

    combined = [
        *initial_results,
        *accepted,
    ]

    if accepted:
        stop_reason = (
            "RELATED_EVIDENCE_ADDED"
        )
    elif ordered_candidates:
        stop_reason = (
            "EXPANSION_LIMIT_PREVENTED_ADDITION"
        )
    else:
        stop_reason = (
            "NO_ELIGIBLE_RELATED_CHUNKS"
        )

    return {
        "results": combined,
        "audit": {
            "initial_document_ids": (
                initial_document_ids
            ),
            "relationship_type_filter": (
                relationship_type
            ),
            "relationship_records": (
                relationship_records
            ),
            "relationship_evidence_candidate_ids": (
                evidence_candidate_ids
            ),
            "related_candidate_ids": (
                related_candidate_ids
            ),
            "accepted_chunk_ids": (
                accepted_chunk_ids
            ),
            "expansion_count": len(
                accepted_chunk_ids
            ),
            "stop_reason": (
                stop_reason
            ),
        },
    }