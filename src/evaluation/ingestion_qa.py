def build_ingestion_report(records: list[dict]) -> dict:
    """
    Build simple QA metrics for an ingestion run.
    """

    total_pages = len(records)

    empty_pages = sum(
        1
        for record in records
        if record.get("extraction_status") == "empty_page"
    )

    successful_pages = sum(
        1
        for record in records
        if record.get("extraction_status") == "success"
    )

    document_ids = {
        record.get("document_id")
        for record in records
        if record.get("document_id")
    }

    source_files = {
        record.get("source_file")
        for record in records
        if record.get("source_file")
    }

    return {
        "documents_processed": len(document_ids),
        "source_files_processed": len(source_files),
        "pages_processed": total_pages,
        "successful_pages": successful_pages,
        "empty_pages": empty_pages,
    }


