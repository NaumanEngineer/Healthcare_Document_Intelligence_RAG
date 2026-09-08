from src.ingestion.load_documents import validate_pdf_path


def test_rejects_non_pdf_file(tmp_path):
    test_file = tmp_path / "example.txt"
    test_file.write_text("test")

    try:
        validate_pdf_path(test_file)
        assert False, "Expected ValueError"
    except ValueError:
        assert True


from src.preprocessing.clean_text import clean_text


def test_clean_text_reduces_extra_spaces():
    raw = "Operational   escalation   requires review."
    cleaned = clean_text(raw)

    assert cleaned == "Operational escalation requires review."


def test_clean_text_reduces_excess_blank_lines():
    raw = "Section one\n\n\n\nSection two"
    cleaned = clean_text(raw)

    assert cleaned == "Section one\n\nSection two"


def test_clean_text_handles_empty_string():
    assert clean_text("") == ""

def test_clean_text_preserves_policy_meaning():
    raw = "OPEL 4 requires executive review."
    cleaned = clean_text(raw)

    assert "OPEL 4" in cleaned
    assert "executive review" in cleaned



from src.ingestion.document_metadata import (
    get_document_metadata,
    enrich_page_record,
)


def test_get_document_metadata():
    metadata = get_document_metadata("DOC-001")

    assert metadata.document_id == "DOC-001"
    assert metadata.title == "Operational Escalation Policy"
    assert metadata.status == "Active"


def test_missing_document_metadata_raises_error():
    try:
        get_document_metadata("DOC-999")
        assert False, "Expected KeyError"
    except KeyError:
        assert True


def test_enrich_page_record():
    metadata = get_document_metadata("DOC-001")

    page = {
        "document_id": "DOC-001",
        "page_number": 1,
        "text": "Example policy text.",
        "source_file": "DOC-001_operational_escalation_policy.pdf",
        "extraction_status": "success",
    }

    enriched = enrich_page_record(page, metadata)

    assert enriched["title"] == "Operational Escalation Policy"
    assert enriched["version"] == "1.0"
    assert enriched["page_number"] == 1



from uuid import uuid4


from pathlib import Path

import pytest

from src.ingestion.load_documents import (
    validate_pdf_path,
    document_has_usable_text,
)

from src.ingestion.document_metadata import (
    get_document_metadata,
)

def test_missing_file_raises_file_not_found():
    missing_file = Path("data/raw/does_not_exist.pdf")

    with pytest.raises(FileNotFoundError):
        validate_pdf_path(missing_file)


def test_rejects_unsupported_file_type(tmp_path):
    test_file = tmp_path / "example.txt"
    test_file.write_text("Not a PDF")

    with pytest.raises(ValueError):
        validate_pdf_path(test_file)


def test_document_with_no_usable_text_returns_false():
    records = [
        {
            "document_id": "DOC-001",
            "page_number": 1,
            "text": "",
            "source_file": "example.pdf",
            "extraction_status": "empty_page",
        },
        {
            "document_id": "DOC-001",
            "page_number": 2,
            "text": "",
            "source_file": "example.pdf",
            "extraction_status": "empty_page",
        },
    ]

    assert document_has_usable_text(records) is False


def test_document_with_usable_text_returns_true():
    records = [
        {
            "document_id": "DOC-001",
            "page_number": 1,
            "text": "",
            "source_file": "example.pdf",
            "extraction_status": "empty_page",
        },
        {
            "document_id": "DOC-001",
            "page_number": 2,
            "text": "Operational escalation guidance.",
            "source_file": "example.pdf",
            "extraction_status": "success",
        },
    ]

    assert document_has_usable_text(records) is True


def test_unknown_document_id_raises_key_error():
    with pytest.raises(KeyError):
        get_document_metadata("DOC-999")

def test_page_numbers_are_one_based():
    records = [
        {
            "document_id": "DOC-001",
            "page_number": 1,
            "text": "Page one",
            "source_file": "example.pdf",
            "extraction_status": "success",
        },
        {
            "document_id": "DOC-001",
            "page_number": 2,
            "text": "Page two",
            "source_file": "example.pdf",
            "extraction_status": "success",
        },
    ]

    assert records[0]["page_number"] == 1
    assert records[1]["page_number"] == 2


