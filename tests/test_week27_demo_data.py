"""Tests for the Week 27 Day 6 deterministic demo corpus."""

from src.application.local_dependencies import (
    DEFAULT_LOCAL_EMBEDDING_MODEL_NAME,
    LocalDeterministicEmbeddingModel,
)
from src.application.week27_demo_data import (
    DEMO_CHUNK_ID,
    DEMO_DOCUMENT_ID,
    DEMO_EVIDENCE_TEXT,
    DEMO_QUESTION,
    build_demo_case,
    build_demo_chunk,
    build_demo_corpus,
    build_demo_embedded_chunk,
)
from src.evidence.evidence_object import (
    build_evidence_object,
)
from src.ingestion.chunk_metadata import (
    validate_chunk_metadata,
)


def test_demo_question_is_non_empty():
    assert isinstance(
        DEMO_QUESTION,
        str,
    )

    assert (
        DEMO_QUESTION.strip()
    )


def test_demo_evidence_is_non_empty():
    assert isinstance(
        DEMO_EVIDENCE_TEXT,
        str,
    )

    assert (
        DEMO_EVIDENCE_TEXT.strip()
    )


def test_demo_chunk_has_expected_identity():
    chunk = build_demo_chunk()

    assert (
        chunk[
            "document_id"
        ]
        == DEMO_DOCUMENT_ID
    )

    assert (
        chunk[
            "chunk_id"
        ]
        == DEMO_CHUNK_ID
    )

    assert (
        chunk[
            "status"
        ]
        == "Active"
    )


def test_demo_chunk_passes_retrieval_metadata_contract():
    chunk = build_demo_chunk()

    validate_chunk_metadata(
        chunk
    )


def test_demo_chunk_passes_evidence_object_contract():
    chunk = build_demo_chunk()

    evidence = (
        build_evidence_object(
            chunk,
            retrieval_route=(
                "RETURN_INITIAL"
            ),
        )
    )

    assert (
        evidence[
            "document_id"
        ]
        == DEMO_DOCUMENT_ID
    )

    assert (
        evidence[
            "chunk_id"
        ]
        == DEMO_CHUNK_ID
    )

    assert (
        evidence[
            "evidence_text"
        ]
        == DEMO_EVIDENCE_TEXT
    )


def test_demo_embedding_is_deterministic():
    model = (
        LocalDeterministicEmbeddingModel()
    )

    first = (
        build_demo_embedded_chunk(
            model=model
        )
    )

    second = (
        build_demo_embedded_chunk(
            model=model
        )
    )

    assert (
        first[
            "vector"
        ]
        == second[
            "vector"
        ]
    )


def test_demo_embedded_chunk_preserves_identity():
    embedded = (
        build_demo_embedded_chunk()
    )

    assert (
        embedded[
            "document_id"
        ]
        == DEMO_DOCUMENT_ID
    )

    assert (
        embedded[
            "chunk_id"
        ]
        == DEMO_CHUNK_ID
    )

    assert (
        embedded[
            "embedding_model"
        ]
        == DEFAULT_LOCAL_EMBEDDING_MODEL_NAME
    )


def test_demo_embedding_dimensions_match_vector():
    embedded = (
        build_demo_embedded_chunk()
    )

    assert (
        embedded[
            "embedding_dimensions"
        ]
        == len(
            embedded[
                "vector"
            ]
        )
    )

    assert (
        embedded[
            "embedding_dimensions"
        ]
        > 0
    )


def test_demo_text_hash_is_present():
    embedded = (
        build_demo_embedded_chunk()
    )

    assert isinstance(
        embedded[
            "text_hash"
        ],
        str,
    )

    assert len(
        embedded[
            "text_hash"
        ]
    ) == 64


def test_demo_corpus_contains_matching_plain_and_embedded_chunk():
    chunks, embedded_chunks = (
        build_demo_corpus()
    )

    assert len(
        chunks
    ) == 1

    assert len(
        embedded_chunks
    ) == 1

    assert (
        chunks[
            0
        ][
            "chunk_id"
        ]
        == embedded_chunks[
            0
        ][
            "chunk_id"
        ]
    )

    assert (
        chunks[
            0
        ][
            "text"
        ]
        == embedded_chunks[
            0
        ][
            "text"
        ]
    )


def test_demo_case_declares_synthetic_non_patient_data():
    case = (
        build_demo_case()
    )

    assert (
        case[
            "synthetic_data"
        ]
        is True
    )

    assert (
        case[
            "patient_data_present"
        ]
        is False
    )


def test_demo_case_counts_match_payload():
    case = (
        build_demo_case()
    )

    assert (
        case[
            "document_count"
        ]
        == 1
    )

    assert (
        case[
            "chunk_count"
        ]
        == len(
            case[
                "chunks"
            ]
        )
    )

    assert (
        case[
            "embedded_chunk_count"
        ]
        == len(
            case[
                "embedded_chunks"
            ]
        )
    )