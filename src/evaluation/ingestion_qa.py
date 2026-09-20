def classify_ingestion_quality(report: dict) -> str:
    """
    Classify overall ingestion quality using simple prototype rules.
    """

    counts = [report.get(key) for key in
              ("pages_processed", "successful_pages", "empty_pages")]
    if any(type(count) is not int or count < 0 for count in counts):
        raise ValueError("QA counts must be non-negative integers.")
    total, successful, empty = counts
    if successful + empty != total:
        raise ValueError("Every processed page must have a recognized status.")

    if report["pages_processed"] == 0:
        return "failed"

    if report["successful_pages"] == 0:
        return "failed"

    if report["empty_pages"] > 0:
        return "review"

    return "passed"


def build_ingestion_report(records: list[dict]) -> dict:
    """
    Build simple QA metrics for an ingestion run.
    """

    for index, record in enumerate(records):
        _validate_page_record(record, index)

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

    report = {
        "documents_processed": len(document_ids),
        "source_files_processed": len(source_files),
        "pages_processed": total_pages,
        "successful_pages": successful_pages,
        "empty_pages": empty_pages,
    }

    report["quality_status"] = classify_ingestion_quality(report)

    return report


def _validate_page_record(
    record: dict,
    index: int,
) -> None:
    """
    Reject malformed evidence before it can contribute
    to a passed ingestion report.

    Supports both:
    - page
    - page_number

    page is the canonical current field.
    page_number is accepted for backward compatibility.
    """

    if not isinstance(record, dict):
        raise ValueError(
            f"Record {index} must be a dictionary."
        )

    for field in (
        "document_id",
        "source_file",
    ):
        value = record.get(
            field
        )

        if (
            not isinstance(value, str)
            or not value.strip()
        ):
            raise ValueError(
                f"Record {index} requires a non-empty {field}."
            )

    page = record.get(
        "page"
    )

    if page is None:
        page = record.get(
            "page_number"
        )

    if (
        type(page) is not int
        or page < 1
    ):
        raise ValueError(
            f"Record {index} requires a one-based page number."
        )

    extraction_status = record.get(
        "extraction_status"
    )

    if extraction_status not in {
        "success",
        "empty_page",
    }:
        raise ValueError(
            f"Record {index} has an invalid extraction_status."
        )

    text = record.get(
        "text"
    )

    if not isinstance(
        text,
        str,
    ):
        raise ValueError(
            f"Record {index} text must be a string."
        )

    if (
        extraction_status == "success"
        and not text.strip()
    ):
        raise ValueError(
            f"Record {index} marked success but has empty text."
        )

    if (
        extraction_status == "empty_page"
        and text.strip()
    ):
        raise ValueError(
            f"Record {index} marked empty_page but contains text."
        )
