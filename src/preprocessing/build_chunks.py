from __future__ import annotations

from src.ingestion.load_documents import (
    extract_pdf_pages,
    document_has_usable_text,
)

from src.ingestion.document_metadata import (
    get_document_metadata,
    enrich_page_record,
    create_ingestion_batch_id,
)

from src.preprocessing.clean_text import (
    clean_text,
)

from src.preprocessing.chunk_text import (
    chunk_page_record,
    DEFAULT_TARGET_CHARS,
    DEFAULT_OVERLAP_CHARS,
)

from src.ingestion.chunk_metadata import (
    validate_chunk_metadata,
)


def clean_page_record(page_record: dict) -> dict:
    """
    Clean the text field of a page-level record while
    preserving all existing provenance and metadata.
    """

    raw_text = page_record.get("text", "")

    cleaned_text = clean_text(raw_text)

    return {
        **page_record,
        "text": cleaned_text,
    }


def enrich_pages_with_metadata(
    page_records: list[dict],
    document_id: str,
    ingestion_batch_id: str,
) -> list[dict]:
    """
    Attach canonical document metadata and ingestion lineage
    to every extracted page.

    The same ingestion_batch_id is applied to all pages
    belonging to one document-processing run.
    """

    metadata = get_document_metadata(document_id)

    enriched_pages = []

    for page_record in page_records:
        enriched_page = enrich_page_record(
            page_record,
            metadata,
        )

        enriched_page = {
            **enriched_page,
            "ingestion_batch_id": ingestion_batch_id,
        }

        enriched_pages.append(enriched_page)

    return enriched_pages


def build_chunks_from_pages(
    page_records: list[dict],
    target_chars: int = DEFAULT_TARGET_CHARS,
    overlap_chars: int = DEFAULT_OVERLAP_CHARS,
) -> list[dict]:
    """
    Convert enriched page records into validated
    retrieval-ready chunks.

    Flow for each page:
    1. clean page text
    2. chunk page text
    3. preserve metadata and provenance
    4. validate canonical chunk metadata
    """

    chunks = []

    for page_record in page_records:
        cleaned_page = clean_page_record(
            page_record
        )

        page_chunks = chunk_page_record(
            cleaned_page,
            target_chars=target_chars,
            overlap_chars=overlap_chars,
        )

        for chunk in page_chunks:
            validate_chunk_metadata(chunk)

            chunks.append(chunk)

    return chunks


def build_document_chunks(
    file_path: str,
    document_id: str,
    target_chars: int = DEFAULT_TARGET_CHARS,
    overlap_chars: int = DEFAULT_OVERLAP_CHARS,
) -> list[dict]:
    """
    Complete document-to-retrieval-chunk pipeline.

    Flow:
    1. create one ingestion batch ID
    2. extract PDF pages
    3. confirm usable text exists
    4. attach document metadata
    5. attach ingestion lineage
    6. clean page text
    7. create page-level chunks
    8. validate canonical chunk metadata
    9. return retrieval-ready chunks
    """

    ingestion_batch_id = create_ingestion_batch_id()

    page_records = extract_pdf_pages(
        file_path=file_path,
        document_id=document_id,
    )

    if not document_has_usable_text(page_records):
        raise ValueError(
            f"Document '{document_id}' contains no usable extracted text."
        )

    enriched_pages = enrich_pages_with_metadata(
        page_records=page_records,
        document_id=document_id,
        ingestion_batch_id=ingestion_batch_id,
    )

    chunks = build_chunks_from_pages(
        page_records=enriched_pages,
        target_chars=target_chars,
        overlap_chars=overlap_chars,
    )

    if not chunks:
        raise ValueError(
            f"Document '{document_id}' produced no retrieval-ready chunks."
        )

    return chunks


