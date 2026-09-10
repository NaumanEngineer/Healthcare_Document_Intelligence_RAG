import math

import pytest

from src.retrieval.embeddings import (
    create_text_hash,
    validate_vector,
    validate_embedding_dimensions,
    embed_chunks,
)


def test_text_hash_is_deterministic():
    text = "Operational escalation guidance."

    first = create_text_hash(text)
    second = create_text_hash(text)

    assert first == second


def test_text_hash_changes_when_text_changes():
    first = create_text_hash(
        "Operational escalation guidance."
    )

    second = create_text_hash(
        "Updated operational escalation guidance."
    )

    assert first != second


def test_empty_text_hash_raises_error():
    with pytest.raises(ValueError):
        create_text_hash("")


def test_valid_vector_passes():
    validate_vector(
        [0.1, 0.2, 0.3]
    )


def test_zero_vector_fails():
    with pytest.raises(ValueError):
        validate_vector(
            [0.0, 0.0, 0.0]
        )


def test_nonfinite_vector_fails():
    with pytest.raises(ValueError):
        validate_vector(
            [0.1, math.inf]
        )


def test_boolean_vector_value_fails():
    with pytest.raises(TypeError):
        validate_vector(
            [0.1, True]
        )


def test_validate_embedding_dimensions_passes():
    validate_embedding_dimensions(
        [0.1, 0.2, 0.3],
        expected_dimensions=3,
    )


def test_validate_embedding_dimensions_fails():
    with pytest.raises(ValueError):
        validate_embedding_dimensions(
            [0.1, 0.2],
            expected_dimensions=3,
        )


def test_validate_embedding_dimensions_rejects_zero():
    with pytest.raises(ValueError):
        validate_embedding_dimensions(
            [0.1, 0.2],
            expected_dimensions=0,
        )


def test_validate_embedding_dimensions_rejects_boolean():
    with pytest.raises(TypeError):
        validate_embedding_dimensions(
            [0.1, 0.2],
            expected_dimensions=True,
        )


def build_valid_chunk() -> dict:
    return {
        "chunk_id": "DOC-001-V1.0-P001-C001",
        "document_id": "DOC-001",
        "title": "Operational Escalation Policy",
        "document_type": "Operational Policy",
        "source_type": "Synthetic",
        "version": "1.0",
        "effective_date": "2026-01-01",
        "status": "Active",
        "source_file": "policy.pdf",
        "page": 1,
        "chunk_number": 1,
        "text": "Operational escalation guidance.",
    }


def test_embed_chunks_reports_failing_chunk():
    class FakeModel:
        def encode(
            self,
            text,
            convert_to_numpy=True,
            normalize_embeddings=False,
        ):
            raise RuntimeError("model failure")

    chunk = build_valid_chunk()

    with pytest.raises(
        RuntimeError,
        match="DOC-001-V1.0-P001-C001",
    ):
        embed_chunks(
            [chunk],
            model=FakeModel(),
        )


def test_embed_chunks_does_not_silently_skip_failure():
    class FakeModel:
        def encode(
            self,
            text,
            convert_to_numpy=True,
            normalize_embeddings=False,
        ):
            raise RuntimeError("embedding unavailable")

    chunks = [
        build_valid_chunk(),
    ]

    with pytest.raises(RuntimeError):
        embed_chunks(
            chunks,
            model=FakeModel(),
        )
