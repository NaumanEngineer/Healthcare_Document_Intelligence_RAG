import pytest

from src.ingestion.chunk_metadata import (
    find_missing_chunk_fields,
    validate_chunk_metadata,
    is_chunk_retrieval_eligible,
)


def build_valid_chunk():
    return {
        "chunk_id": "DOC-001-V1.0-P003-C002",
        "document_id": "DOC-001",
        "title": "Operational Escalation Policy",
        "document_type": "Operational Policy",
        "source_type": "Synthetic",
        "version": "1.0",
        "effective_date": "2026-01-01",
        "status": "Active",
        "source_file": "DOC-001_operational_escalation_policy.pdf",
        "page": 3,
        "chunk_number": 2,
        "text": "Operational escalation guidance.",
    }


def test_valid_chunk_metadata():
    chunk = build_valid_chunk()

    validate_chunk_metadata(chunk)


def test_missing_version_is_detected():
    chunk = build_valid_chunk()
    del chunk["version"]

    missing = find_missing_chunk_fields(chunk)

    assert "version" in missing


def test_missing_required_metadata_raises_error():
    chunk = build_valid_chunk()
    del chunk["source_file"]

    with pytest.raises(ValueError):
        validate_chunk_metadata(chunk)


def test_invalid_status_raises_error():
    chunk = build_valid_chunk()
    chunk["status"] = "Unknown"

    with pytest.raises(ValueError):
        validate_chunk_metadata(chunk)


def test_page_must_be_positive():
    chunk = build_valid_chunk()
    chunk["page"] = 0

    with pytest.raises(ValueError):
        validate_chunk_metadata(chunk)


def test_active_chunk_is_retrieval_eligible():
    chunk = build_valid_chunk()

    assert is_chunk_retrieval_eligible(chunk) is True


def test_superseded_chunk_is_not_retrieval_eligible():
    chunk = build_valid_chunk()
    chunk["status"] = "Superseded"

    assert is_chunk_retrieval_eligible(chunk) is False
