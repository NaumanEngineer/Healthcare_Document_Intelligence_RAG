import pytest

from src.preprocessing.chunk_text import (
    split_into_paragraphs,
    split_oversized_paragraph,
    chunk_page_text,
    chunk_page_record,
)


def test_split_into_paragraphs():
    text = "Paragraph one.\n\nParagraph two."

    paragraphs = split_into_paragraphs(text)

    assert paragraphs == [
        "Paragraph one.",
        "Paragraph two.",
    ]


def test_empty_text_returns_no_paragraphs():
    assert split_into_paragraphs("") == []


def test_short_paragraph_is_not_split():
    paragraph = "Short policy statement."

    result = split_oversized_paragraph(
        paragraph,
        target_chars=100,
    )

    assert result == [paragraph]


def test_oversized_paragraph_is_split():
    paragraph = "A" * 250

    result = split_oversized_paragraph(
        paragraph,
        target_chars=100,
    )

    assert len(result) == 3


def test_chunk_page_text_returns_chunks():
    text = (
        "Operational escalation guidance.\n\n"
        "Executive leadership must be notified."
    )

    chunks = chunk_page_text(
        text,
        target_chars=80,
        overlap_chars=10,
    )

    assert len(chunks) >= 1


def test_chunk_page_record_preserves_provenance():
    page_record = {
        "document_id": "DOC-001",
        "page_number": 3,
        "text": "Operational escalation guidance.",
        "source_file": "policy.pdf",
    }

    chunks = chunk_page_record(
        page_record,
        target_chars=100,
        overlap_chars=10,
    )

    assert len(chunks) == 1
    assert chunks[0]["document_id"] == "DOC-001"
    assert chunks[0]["page_number"] == 3
    assert chunks[0]["source_file"] == "policy.pdf"


def test_chunk_id_is_stable():
    page_record = {
        "document_id": "DOC-001",
        "page_number": 3,
        "text": "Operational escalation guidance.",
        "source_file": "policy.pdf",
    }

    chunks = chunk_page_record(
        page_record,
        target_chars=100,
        overlap_chars=10,
    )

    assert chunks[0]["chunk_id"] == "DOC-001-P003-C001"


def test_missing_document_id_raises_error():
    page_record = {
        "page_number": 1,
        "text": "Example text.",
        "source_file": "policy.pdf",
    }

    with pytest.raises(ValueError):
        chunk_page_record(page_record)



