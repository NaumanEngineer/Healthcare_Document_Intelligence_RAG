from pathlib import Path
import fitz


def validate_pdf_path(file_path):
    """
    Validate that the supplied path exists and points to a PDF file.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(
            f"Unsupported file type: {path.suffix}. "
            "Only PDF files are supported."
        )

    return path


def extract_pdf_pages(file_path, document_id):
    """
    Extract page-level text from a PDF while preserving source traceability.

    Returns:
        list[dict]: One structured record per PDF page.
    """

    path = validate_pdf_path(file_path)

    records = []

    try:
        document = fitz.open(path)

        for page_index, page in enumerate(document):
            text = page.get_text("text").strip()

            extraction_status = (
                "success"
                if text
                else "empty_page"
            )

            records.append(
                {
                    "document_id": document_id,
                    "page_number": page_index + 1,
                    "text": text,
                    "source_file": path.name,
                    "extraction_status": extraction_status,
                }
            )

        document.close()

    except Exception as exc:
        raise RuntimeError(
            f"Failed to extract PDF '{path.name}': {exc}"
        ) from exc

    return records


def document_has_usable_text(records):
    """
    Return True when at least one extracted page contains usable text.
    """

    return any(
        record["extraction_status"] == "success"
        for record in records
    )
