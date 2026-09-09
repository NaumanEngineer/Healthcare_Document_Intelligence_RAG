from __future__ import annotations

from statistics import mean


DEFAULT_MIN_CHUNK_CHARS = 100
DEFAULT_MAX_CHUNK_CHARS = 1300


def get_chunk_lengths(chunks: list[dict]) -> list[int]:
    """
    Return the character length of each chunk's text.
    """

    return [
        len(chunk.get("text", ""))
        for chunk in chunks
    ]


def find_empty_chunks(chunks: list[dict]) -> list[str]:
    """
    Return chunk IDs for chunks containing no usable text.
    """

    empty_chunk_ids = []

    for chunk in chunks:
        text = chunk.get("text", "")

        if not isinstance(text, str) or not text.strip():
            empty_chunk_ids.append(
                chunk.get("chunk_id", "<missing_chunk_id>")
            )

    return empty_chunk_ids


def find_duplicate_chunk_ids(chunks: list[dict]) -> list[str]:
    """
    Return duplicate chunk IDs.
    """

    seen = set()
    duplicates = set()

    for chunk in chunks:
        chunk_id = chunk.get("chunk_id")

        if not chunk_id:
            continue

        if chunk_id in seen:
            duplicates.add(chunk_id)
        else:
            seen.add(chunk_id)

    return sorted(duplicates)


def find_short_chunks(
    chunks: list[dict],
    min_chars: int = DEFAULT_MIN_CHUNK_CHARS,
) -> list[str]:
    """
    Return chunk IDs for non-empty chunks below the minimum size.
    """

    short_chunk_ids = []

    for chunk in chunks:
        text = chunk.get("text", "")

        if (
            isinstance(text, str)
            and text.strip()
            and len(text) < min_chars
        ):
            short_chunk_ids.append(
                chunk.get("chunk_id", "<missing_chunk_id>")
            )

    return short_chunk_ids


def find_long_chunks(
    chunks: list[dict],
    max_chars: int = DEFAULT_MAX_CHUNK_CHARS,
) -> list[str]:
    """
    Return chunk IDs for chunks above the maximum QA threshold.
    """

    long_chunk_ids = []

    for chunk in chunks:
        text = chunk.get("text", "")

        if isinstance(text, str) and len(text) > max_chars:
            long_chunk_ids.append(
                chunk.get("chunk_id", "<missing_chunk_id>")
            )

    return long_chunk_ids


def find_missing_provenance(chunks: list[dict]) -> list[str]:
    """
    Return chunk IDs for records missing core provenance fields.
    """

    required_fields = {
        "chunk_id",
        "document_id",
        "version",
        "status",
        "source_file",
        "page",
        "chunk_number",
    }

    failed = []

    for chunk in chunks:
        missing = [
            field
            for field in required_fields
            if chunk.get(field) in (None, "")
        ]

        if missing:
            failed.append(
                chunk.get("chunk_id", "<missing_chunk_id>")
            )

    return failed


def classify_chunk_quality(report: dict) -> str:
    """
    Classify overall chunk QA status.

    failed:
    - zero chunks
    - empty chunks
    - duplicate chunk IDs
    - missing provenance

    review:
    - short or long chunks exist

    passed:
    - no blocking or review findings
    """

    if report["total_chunks"] == 0:
        return "failed"

    if report["empty_chunk_count"] > 0:
        return "failed"

    if report["duplicate_chunk_id_count"] > 0:
        return "failed"

    if report["missing_provenance_count"] > 0:
        return "failed"

    if report["short_chunk_count"] > 0:
        return "review"

    if report["long_chunk_count"] > 0:
        return "review"

    return "passed"


def build_chunk_qa_report(
    chunks: list[dict],
    min_chars: int = DEFAULT_MIN_CHUNK_CHARS,
    max_chars: int = DEFAULT_MAX_CHUNK_CHARS,
) -> dict:
    """
    Build QA metrics for retrieval-ready chunks.
    """

    lengths = get_chunk_lengths(chunks)

    empty_chunks = find_empty_chunks(chunks)

    duplicate_chunk_ids = find_duplicate_chunk_ids(chunks)

    short_chunks = find_short_chunks(
        chunks,
        min_chars=min_chars,
    )

    long_chunks = find_long_chunks(
        chunks,
        max_chars=max_chars,
    )

    missing_provenance = find_missing_provenance(chunks)

    report = {
        "total_chunks": len(chunks),
        "average_chunk_length": (
            mean(lengths)
            if lengths
            else 0
        ),
        "minimum_chunk_length": (
            min(lengths)
            if lengths
            else 0
        ),
        "maximum_chunk_length": (
            max(lengths)
            if lengths
            else 0
        ),
        "empty_chunk_count": len(empty_chunks),
        "empty_chunk_ids": empty_chunks,
        "duplicate_chunk_id_count": len(duplicate_chunk_ids),
        "duplicate_chunk_ids": duplicate_chunk_ids,
        "short_chunk_count": len(short_chunks),
        "short_chunk_ids": short_chunks,
        "long_chunk_count": len(long_chunks),
        "long_chunk_ids": long_chunks,
        "missing_provenance_count": len(missing_provenance),
        "missing_provenance_chunk_ids": missing_provenance,
    }

    report["quality_status"] = classify_chunk_quality(report)

    return report
