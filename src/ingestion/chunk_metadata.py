from __future__ import annotations


REQUIRED_CHUNK_FIELDS = {
    "chunk_id",
    "document_id",
    "title",
    "document_type",
    "source_type",
    "version",
    "effective_date",
    "status",
    "source_file",
    "page",
    "chunk_number",
    "text",
}


ALLOWED_DOCUMENT_STATUSES = {
    "Active",
    "Superseded",
    "Draft",
    "Archived",
}


def find_missing_chunk_fields(chunk: dict) -> list[str]:
    """
    Return required metadata fields that are absent or empty.
    """

    missing = []

    for field in REQUIRED_CHUNK_FIELDS:
        value = chunk.get(field)

        if value is None:
            missing.append(field)

        elif isinstance(value, str) and not value.strip():
            missing.append(field)

    return sorted(missing)


def validate_chunk_metadata(chunk: dict) -> None:
    """
    Validate the minimum metadata contract required for
    retrieval-ready chunks.
    """

    missing_fields = find_missing_chunk_fields(chunk)

    if missing_fields:
        raise ValueError(
            "Chunk is missing required metadata fields: "
            + ", ".join(missing_fields)
        )

    status = chunk["status"]

    if status not in ALLOWED_DOCUMENT_STATUSES:
        raise ValueError(
            f"Unsupported document status '{status}'"
        )

    if not isinstance(chunk["page"], int):
        raise TypeError(
            "page must be an integer"
        )

    if chunk["page"] <= 0:
        raise ValueError(
            "page must be greater than 0"
        )

    if not isinstance(chunk["chunk_number"], int):
        raise TypeError(
            "chunk_number must be an integer"
        )

    if chunk["chunk_number"] <= 0:
        raise ValueError(
            "chunk_number must be greater than 0"
        )


def is_chunk_retrieval_eligible(chunk: dict) -> bool:
    """
    Return True when a chunk belongs to an Active document.

    This is a prototype retrieval-governance rule.
    """

    return chunk.get("status") == "Active"
