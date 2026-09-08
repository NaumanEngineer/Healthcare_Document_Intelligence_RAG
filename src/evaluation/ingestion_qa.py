def classify_ingestion_quality(report: dict) -> str:
    """
    Classify overall ingestion quality using simple prototype rules.
    """

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


def test_ingestion_quality_passed():
    report = {
        "pages_processed": 5,
        "successful_pages": 5,
        "empty_pages": 0,
    }

    from src.evaluation.ingestion_qa import classify_ingestion_quality

    assert classify_ingestion_quality(report) == "passed"


def test_ingestion_quality_review():
    report = {
        "pages_processed": 5,
        "successful_pages": 4,
        "empty_pages": 1,
    }

    from src.evaluation.ingestion_qa import classify_ingestion_quality

    assert classify_ingestion_quality(report) == "review"



def test_ingestion_quality_failed():
    report = {
        "pages_processed": 2,
        "successful_pages": 0,
        "empty_pages": 2,
    }

    from src.evaluation.ingestion_qa import classify_ingestion_quality

    assert classify_ingestion_quality(report) == "failed"


pytest -q

