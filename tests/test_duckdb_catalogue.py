import pytest

from src.storage.duckdb_catalogue import (
    normalise_chunk_for_parquet,
    write_chunks_to_parquet,
    query_chunk_catalogue,
    count_chunks_by_status,
    get_active_chunks,
)


def build_sample_chunk(
    status: str = "Active",
) -> dict:
    return {
        "chunk_id": "DOC-001-V1.0-P001-C001",
        "document_id": "DOC-001",
        "title": "Operational Escalation Policy",
        "document_type": "Operational Policy",
        "source_type": "Synthetic",
        "version": "1.0",
        "effective_date": "2026-01-01",
        "status": status,
        "source_file": "policy.pdf",
        "source_location": None,
        "page": 1,
        "chunk_number": 1,
        "section": None,
        "topic": None,
        "ingestion_batch_id": "BATCH-001",
        "text": "Operational escalation guidance.",
        "embedding_model": (
            "sentence-transformers/"
            "all-MiniLM-L6-v2"
        ),
        "embedding_dimensions": 384,
        "text_hash": "abc123",
        "vector": [0.1, 0.2, 0.3],
    }


def test_normalise_chunk_excludes_vector():
    chunk = build_sample_chunk()

    record = normalise_chunk_for_parquet(
        chunk
    )

    assert "vector" not in record
    assert record["chunk_id"] == (
        "DOC-001-V1.0-P001-C001"
    )


def test_write_chunks_to_parquet(tmp_path):
    chunks = [
        build_sample_chunk()
    ]

    path = tmp_path / "chunks.parquet"

    result = write_chunks_to_parquet(
        chunks,
        parquet_path=path,
    )

    assert result.exists()


def test_query_chunk_catalogue(tmp_path):
    chunks = [
        build_sample_chunk()
    ]

    path = tmp_path / "chunks.parquet"

    write_chunks_to_parquet(
        chunks,
        parquet_path=path,
    )

    rows = query_chunk_catalogue(
        parquet_path=path,
    )

    assert len(rows) == 1
    assert rows[0][0] == (
        "DOC-001-V1.0-P001-C001"
    )


def test_count_chunks_by_status(tmp_path):
    active = build_sample_chunk(
        status="Active"
    )

    superseded = {
        **build_sample_chunk(
            status="Superseded"
        ),
        "chunk_id": (
            "DOC-002-V1.0-P001-C001"
        ),
        "document_id": "DOC-002",
    }

    path = tmp_path / "chunks.parquet"

    write_chunks_to_parquet(
        [active, superseded],
        parquet_path=path,
    )

    rows = count_chunks_by_status(
        parquet_path=path,
    )

    statuses = dict(rows)

    assert statuses["Active"] == 1
    assert statuses["Superseded"] == 1


def test_get_active_chunks_excludes_superseded(
    tmp_path,
):
    active = build_sample_chunk(
        status="Active"
    )

    superseded = {
        **build_sample_chunk(
            status="Superseded"
        ),
        "chunk_id": (
            "DOC-002-V1.0-P001-C001"
        ),
        "document_id": "DOC-002",
    }

    path = tmp_path / "chunks.parquet"

    write_chunks_to_parquet(
        [active, superseded],
        parquet_path=path,
    )

    rows = get_active_chunks(
        parquet_path=path,
    )

    assert len(rows) == 1
    assert rows[0][0] == (
        "DOC-001-V1.0-P001-C001"
    )


def test_empty_chunk_list_fails(tmp_path):
    path = tmp_path / "chunks.parquet"

    with pytest.raises(ValueError):
        write_chunks_to_parquet(
            [],
            parquet_path=path,
        )
