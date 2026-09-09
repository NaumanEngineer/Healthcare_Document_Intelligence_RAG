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


from src.preprocessing.build_chunks import (
    clean_page_record,
    enrich_pages_with_metadata,
    build_chunks_from_pages,
)


def test_clean_page_record_preserves_metadata():
    page = {
        "document_id": "DOC-001",
        "page": 1,
        "text": "Operational   escalation.",
        "source_file": "DOC-001_operational_escalation_policy.pdf",
    }

    result = clean_page_record(page)

    assert result["document_id"] == "DOC-001"
    assert result["page"] == 1
    assert result["source_file"] == (
        "DOC-001_operational_escalation_policy.pdf"
    )
    assert result["text"] == "Operational escalation."


def test_enrichment_adds_batch_lineage():
    pages = [
        {
            "document_id": "DOC-001",
            "page": 1,
            "text": "Example.",
            "source_file": (
                "DOC-001_operational_escalation_policy.pdf"
            ),
        }
    ]

    enriched = enrich_pages_with_metadata(
        page_records=pages,
        document_id="DOC-001",
        ingestion_batch_id="TEST-BATCH-001",
    )

    assert enriched[0]["ingestion_batch_id"] == "TEST-BATCH-001"
    assert enriched[0]["version"] == "1.0"
    assert enriched[0]["status"] == "Active"


def test_build_chunks_from_enriched_pages():
    pages = [
        {
            "document_id": "DOC-001",
            "title": "Operational Escalation Policy",
            "document_type": "Operational Policy",
            "source_type": "Synthetic",
            "version": "1.0",
            "effective_date": "2026-01-01",
            "status": "Active",
            "source_file": (
                "DOC-001_operational_escalation_policy.pdf"
            ),
            "page": 1,
            "text": (
                "Operational escalation guidance "
                "requires executive review."
            ),
            "ingestion_batch_id": "TEST-BATCH-001",
        }
    ]

    chunks = build_chunks_from_pages(
        page_records=pages,
        target_chars=100,
        overlap_chars=10,
    )

    assert len(chunks) >= 1
    assert chunks[0]["document_id"] == "DOC-001"
    assert chunks[0]["status"] == "Active"
    assert chunks[0]["ingestion_batch_id"] == "TEST-BATCH-001"
    assert chunks[0]["chunk_id"].startswith(
        "DOC-001-V1.0-P001-C"
    )
