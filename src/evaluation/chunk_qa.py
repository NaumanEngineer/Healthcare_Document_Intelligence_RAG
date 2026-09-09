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
        if isinstance(chunk.get("text", ""), str)
        else 0
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
                chunk.get(
                    "chunk_id",
                    "<missing_chunk_id>",
                )
            )

    return empty_chunk_ids


def find_duplicate_chunk_ids(
    chunks: list[dict],
) -> list[str]:
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
    Return chunk IDs for non-empty chunks below
    the prototype minimum-size threshold.
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
                chunk.get(
                    "chunk_id",
                    "<missing_chunk_id>",
                )
            )

    return short_chunk_ids


def find_long_chunks(
    chunks: list[dict],
    max_chars: int = DEFAULT_MAX_CHUNK_CHARS,
) -> list[str]:
    """
    Return chunk IDs above the prototype
    maximum-size QA threshold.
    """

    long_chunk_ids = []

    for chunk in chunks:
        text = chunk.get("text", "")

        if (
            isinstance(text, str)
            and len(text) > max_chars
        ):
            long_chunk_ids.append(
                chunk.get(
                    "chunk_id",
                    "<missing_chunk_id>",
                )
            )

    return long_chunk_ids


def find_missing_provenance(
    chunks: list[dict],
) -> list[str]:
    """
    Return chunk IDs for records containing missing
    or invalid core provenance.

    Required textual provenance:
    - chunk_id
    - document_id
    - version
    - status
    - source_file

    Required numeric provenance:
    - page: positive integer, excluding bool
    - chunk_number: positive integer, excluding bool
    """

    required_string_fields = {
        "chunk_id",
        "document_id",
        "version",
        "status",
        "source_file",
    }

    failed = []

    for chunk in chunks:
        invalid = False

        for field in required_string_fields:
            value = chunk.get(field)

            if (
                not isinstance(value, str)
                or not value.strip()
            ):
                invalid = True
                break

        page = chunk.get("page")
        chunk_number = chunk.get(
            "chunk_number"
        )

        if (
            not isinstance(page, int)
            or isinstance(page, bool)
            or page <= 0
        ):
            invalid = True

        if (
            not isinstance(chunk_number, int)
            or isinstance(chunk_number, bool)
            or chunk_number <= 0
        ):
            invalid = True

        if invalid:
            failed.append(
                chunk.get(
                    "chunk_id",
                    "<missing_chunk_id>",
                )
            )

    return failed


def classify_chunk_quality(
    report: dict,
) -> str:
    """
    Classify overall chunk QA status.

    failed:
    - zero chunks
    - empty chunks
    - duplicate chunk IDs
    - invalid/missing provenance

    review:
    - short chunks
    - long chunks

    passed:
    - no blocking or review findings
    """

    if report["total_chunks"] == 0:
        return "failed"

    if report["empty_chunk_count"] > 0:
        return "failed"

    if (
        report["duplicate_chunk_id_count"]
        > 0
    ):
        return "failed"

    if (
        report["missing_provenance_count"]
        > 0
    ):
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
    Build structural and heuristic QA metrics
    for retrieval-ready chunks.

    This QA layer does not replace the canonical
    chunk metadata validator.

    Canonical metadata validation checks whether
    a chunk is structurally valid.

    Chunk QA checks whether a collection of valid
    chunks appears operationally healthy.
    """

    lengths = get_chunk_lengths(
        chunks
    )

    empty_chunks = find_empty_chunks(
        chunks
    )

    duplicate_chunk_ids = (
        find_duplicate_chunk_ids(
            chunks
        )
    )

    short_chunks = find_short_chunks(
        chunks,
        min_chars=min_chars,
    )

    long_chunks = find_long_chunks(
        chunks,
        max_chars=max_chars,
    )

    missing_provenance = (
        find_missing_provenance(
            chunks
        )
    )

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

        "empty_chunk_count": (
            len(empty_chunks)
        ),

        "empty_chunk_ids": (
            empty_chunks
        ),

        "duplicate_chunk_id_count": (
            len(duplicate_chunk_ids)
        ),

        "duplicate_chunk_ids": (
            duplicate_chunk_ids
        ),

        "short_chunk_count": (
            len(short_chunks)
        ),

        "short_chunk_ids": (
            short_chunks
        ),

        "long_chunk_count": (
            len(long_chunks)
        ),

        "long_chunk_ids": (
            long_chunks
        ),

        "missing_provenance_count": (
            len(missing_provenance)
        ),

        "missing_provenance_chunk_ids": (
            missing_provenance
        ),
    }

    report["quality_status"] = (
        classify_chunk_quality(
            report
        )
    )

    return report
