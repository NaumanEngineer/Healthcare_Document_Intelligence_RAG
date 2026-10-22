"""Week 28 — three-outcome governed portfolio demo data.

This module provides deterministic synthetic evidence for demonstrating the
three application-level governance outcomes:

- ANSWER
- REVIEW_REQUIRED
- ABSTAIN

The evidence is synthetic and contains no patient data.

The outcome is never assigned by this module. Evidence conditions are passed
through the existing retrieval, evidence, governance, generation, assurance,
and final-governance path.
"""

from __future__ import annotations

import hashlib
from copy import deepcopy

import numpy as np

from src.application.local_dependencies import (
    DEFAULT_LOCAL_EMBEDDING_MODEL_NAME,
    LocalDeterministicEmbeddingModel,
)


ANSWER_CASE_ID = "W28-DEMO-ANSWER-001"
REVIEW_CASE_ID = "W28-DEMO-REVIEW-001"
ABSTAIN_CASE_ID = "W28-DEMO-ABSTAIN-001"


ANSWER_DOCUMENT_ID = "W28-DEMO-DOC-A001"

REVIEW_WORKFORCE_DOCUMENT_ID = (
    "W28-DEMO-DOC-R001"
)

REVIEW_CAPACITY_DOCUMENT_ID = (
    "W28-DEMO-DOC-R002"
)


ANSWER_QUESTION = (
    "What factors should be reviewed during "
    "operational pressure?"
)

REVIEW_QUESTION = (
    "How should workforce and bed capacity "
    "pressures be considered together?"
)

ABSTAIN_QUESTION = (
    "What operational guidance applies to "
    "temporary overnight visitor parking?"
)


ANSWER_EVIDENCE_TEXT = (
    "During operational pressure, the operational escalation "
    "guidance states that bed capacity, staffing constraints, "
    "and current service demand should be reviewed before "
    "further escalation is considered."
)


REVIEW_WORKFORCE_EVIDENCE_TEXT = (
    "During operational pressure, workforce guidance states "
    "that staffing availability, skill mix, absence pressure, "
    "and redeployment constraints should be reviewed."
)


REVIEW_CAPACITY_EVIDENCE_TEXT = (
    "During operational pressure, bed capacity guidance states "
    "that current occupancy, available beds, discharge flow, "
    "and expected demand should be reviewed."
)


def _text_hash(
    text: str,
) -> str:
    if (
        not isinstance(
            text,
            str,
        )
        or not text
    ):
        raise ValueError(
            "text must be a non-empty string."
        )

    return hashlib.sha256(
        text.encode(
            "utf-8"
        )
    ).hexdigest()


def _build_chunk(
    *,
    document_id: str,
    chunk_id: str,
    title: str,
    source_file: str,
    source_location: str,
    text: str,
) -> dict:
    return {
        "chunk_id": chunk_id,
        "document_id": document_id,
        "title": title,
        "document_type": (
            "operational_guidance"
        ),
        "source_type": (
            "synthetic_demo"
        ),
        "source_location": (
            source_location
        ),
        "source_file": (
            source_file
        ),
        "version": "1.0",
        "effective_date": (
            "2026-10-01"
        ),
        "status": "Active",
        "page": 1,
        "chunk_number": 1,
        "text": text,
        "extraction_status": (
            "SUCCESS"
        ),
        "ingestion_batch_id": (
            "W28-DAY2-DEMO-BATCH-001"
        ),
    }


def _build_embedded_chunk(
    chunk: dict,
    *,
    model: (
        LocalDeterministicEmbeddingModel
        | None
    ) = None,
) -> dict:
    active_model = (
        model
        if model is not None
        else LocalDeterministicEmbeddingModel()
    )

    encoded = (
        active_model.encode(
            chunk[
                "text"
            ]
        )
    )

    if not isinstance(
        encoded,
        np.ndarray,
    ):
        raise ValueError(
            "Demo embedding model returned "
            "an invalid vector type."
        )

    if (
        encoded.ndim != 1
        or encoded.size == 0
    ):
        raise ValueError(
            "Demo embedding model returned "
            "an invalid vector shape."
        )

    vector = (
        encoded.tolist()
    )

    return {
        **deepcopy(
            chunk
        ),
        "vector": vector,
        "embedding_model": (
            DEFAULT_LOCAL_EMBEDDING_MODEL_NAME
        ),
        "embedding_dimensions": (
            len(
                vector
            )
        ),
        "text_hash": (
            _text_hash(
                chunk[
                    "text"
                ]
            )
        ),
    }


def build_answer_chunks() -> list[dict]:
    return [
        _build_chunk(
            document_id=(
                ANSWER_DOCUMENT_ID
            ),
            chunk_id=(
                f"{ANSWER_DOCUMENT_ID}"
                "::P1::C1"
            ),
            title=(
                "Synthetic Operational "
                "Escalation Guidance"
            ),
            source_file=(
                "synthetic_operational_"
                "escalation_guidance.txt"
            ),
            source_location=(
                "week28_answer_demo"
            ),
            text=(
                ANSWER_EVIDENCE_TEXT
            ),
        )
    ]


def build_review_chunks() -> list[dict]:
    return [
        _build_chunk(
            document_id=(
                REVIEW_WORKFORCE_DOCUMENT_ID
            ),
            chunk_id=(
                f"{REVIEW_WORKFORCE_DOCUMENT_ID}"
                "::P1::C1"
            ),
            title=(
                "Synthetic Workforce "
                "Pressure Guidance"
            ),
            source_file=(
                "synthetic_workforce_"
                "pressure_guidance.txt"
            ),
            source_location=(
                "week28_review_demo"
            ),
            text=(
                REVIEW_WORKFORCE_EVIDENCE_TEXT
            ),
        ),
        _build_chunk(
            document_id=(
                REVIEW_CAPACITY_DOCUMENT_ID
            ),
            chunk_id=(
                f"{REVIEW_CAPACITY_DOCUMENT_ID}"
                "::P1::C1"
            ),
            title=(
                "Synthetic Bed Capacity "
                "Pressure Guidance"
            ),
            source_file=(
                "synthetic_bed_capacity_"
                "pressure_guidance.txt"
            ),
            source_location=(
                "week28_review_demo"
            ),
            text=(
                REVIEW_CAPACITY_EVIDENCE_TEXT
            ),
        ),
    ]


def build_embedded_corpus(
    chunks: list[dict],
) -> list[dict]:
    model = (
        LocalDeterministicEmbeddingModel()
    )

    return [
        _build_embedded_chunk(
            chunk,
            model=model,
        )
        for chunk in chunks
    ]


def build_answer_corpus() -> tuple[
    list[dict],
    list[dict],
]:
    chunks = (
        build_answer_chunks()
    )

    return (
        chunks,
        build_embedded_corpus(
            chunks
        ),
    )


def build_review_corpus() -> tuple[
    list[dict],
    list[dict],
]:
    chunks = (
        build_review_chunks()
    )

    return (
        chunks,
        build_embedded_corpus(
            chunks
        ),
    )


def build_abstain_corpus() -> tuple[
    list[dict],
    list[dict],
]:
    """Return an intentionally empty evidence corpus.

    The question remains valid and operationally phrased.

    The absence of sufficient approved evidence should therefore be handled by
    the existing retrieval/governance path as ABSTAIN rather than by a runtime
    failure.
    """

    return (
        [],
        [],
    )


def build_week28_demo_cases() -> list[dict]:
    answer_chunks, answer_embedded = (
        build_answer_corpus()
    )

    review_chunks, review_embedded = (
        build_review_corpus()
    )

    abstain_chunks, abstain_embedded = (
        build_abstain_corpus()
    )

    return [
        {
            "case_id": (
                ANSWER_CASE_ID
            ),
            "case_name": (
                "Strong single-source "
                "operational guidance"
            ),
            "question": (
                ANSWER_QUESTION
            ),
            "expected_outcome": (
                "ANSWER"
            ),
            "synthetic_data": True,
            "patient_data_present": (
                False
            ),
            "chunks": answer_chunks,
            "embedded_chunks": (
                answer_embedded
            ),
        },
        {
            "case_id": (
                REVIEW_CASE_ID
            ),
            "case_name": (
                "Cross-document workforce "
                "and capacity review"
            ),
            "question": (
                REVIEW_QUESTION
            ),
            "expected_outcome": (
                "REVIEW_REQUIRED"
            ),
            "synthetic_data": True,
            "patient_data_present": (
                False
            ),
            "chunks": review_chunks,
            "embedded_chunks": (
                review_embedded
            ),
        },
        {
            "case_id": (
                ABSTAIN_CASE_ID
            ),
            "case_name": (
                "Insufficient evidence"
            ),
            "question": (
                ABSTAIN_QUESTION
            ),
            "expected_outcome": (
                "ABSTAIN"
            ),
            "synthetic_data": True,
            "patient_data_present": (
                False
            ),
            "chunks": abstain_chunks,
            "embedded_chunks": (
                abstain_embedded
            ),
        },
    ]