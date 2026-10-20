"""Week 27 Day 6 — deterministic end-to-end demo data.

This module provides a tiny synthetic healthcare operational-policy corpus for
the Week 27 portfolio demonstration.

The data is deliberately:

- synthetic;
- non-patient;
- deterministic;
- provenance-complete;
- explicit about lifecycle status;
- separate from production dependencies.

It exists only to demonstrate the existing governed RAG application path.
"""

from __future__ import annotations

import hashlib
from copy import deepcopy

import numpy as np

from src.application.local_dependencies import (
    DEFAULT_LOCAL_EMBEDDING_MODEL_NAME,
    LocalDeterministicEmbeddingModel,
)


DEMO_DOCUMENT_ID = "W27-DEMO-DOC-001"
DEMO_CHUNK_ID = "W27-DEMO-DOC-001::P1::C1"

DEMO_QUESTION = (
    "What factors should be reviewed during "
    "operational pressure?"
)

DEMO_EVIDENCE_TEXT = (
    "During operational pressure, the operational escalation "
    "guidance states that bed capacity, staffing constraints, "
    "and current service demand should be reviewed before "
    "further escalation is considered."
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


def build_demo_chunk() -> dict:
    """Build one provenance-complete synthetic retrieval chunk."""

    return {
        "chunk_id": DEMO_CHUNK_ID,
        "document_id": DEMO_DOCUMENT_ID,
        "title": (
            "Synthetic Operational "
            "Escalation Guidance"
        ),
        "document_type": (
            "operational_guidance"
        ),
        "source_type": "synthetic_demo",
        "source_location": (
            "week27_day6_demo"
        ),
        "source_file": (
            "synthetic_operational_"
            "escalation_guidance.txt"
        ),
        "version": "1.0",
        "effective_date": "2026-10-01",
        "status": "Active",
        "page": 1,
        "chunk_number": 1,
        "text": DEMO_EVIDENCE_TEXT,
        "extraction_status": "SUCCESS",
        "ingestion_batch_id": (
            "W27-DAY6-DEMO-BATCH-001"
        ),
    }


def build_demo_embedded_chunk(
    *,
    model: (
        LocalDeterministicEmbeddingModel
        | None
    ) = None,
) -> dict:
    """Build the matching deterministic embedded chunk."""

    active_model = (
        model
        if model is not None
        else LocalDeterministicEmbeddingModel()
    )

    chunk = build_demo_chunk()

    encoded = active_model.encode(
        chunk[
            "text"
        ]
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

    vector = encoded.tolist()

    return {
        **deepcopy(
            chunk
        ),
        "vector": vector,
        "embedding_model": (
            DEFAULT_LOCAL_EMBEDDING_MODEL_NAME
        ),
        "embedding_dimensions": len(
            vector
        ),
        "text_hash": _text_hash(
            chunk[
                "text"
            ]
        ),
    }


def build_demo_corpus() -> tuple[
    list[dict],
    list[dict],
]:
    """Return plain and embedded demo corpora."""

    model = (
        LocalDeterministicEmbeddingModel()
    )

    chunk = build_demo_chunk()

    embedded_chunk = (
        build_demo_embedded_chunk(
            model=model
        )
    )

    return (
        [
            chunk
        ],
        [
            embedded_chunk
        ],
    )


def build_demo_case() -> dict:
    """Return the complete Week 27 deterministic demo contract."""

    chunks, embedded_chunks = (
        build_demo_corpus()
    )

    return {
        "case_id": "W27-D6-E2E-001",
        "case_name": (
            "Synthetic operational "
            "pressure guidance"
        ),
        "question": DEMO_QUESTION,
        "synthetic_data": True,
        "patient_data_present": False,
        "document_count": 1,
        "chunk_count": len(
            chunks
        ),
        "embedded_chunk_count": len(
            embedded_chunks
        ),
        "chunks": chunks,
        "embedded_chunks": (
            embedded_chunks
        ),
    }