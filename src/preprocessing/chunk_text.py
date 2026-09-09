from __future__ import annotations

import re


DEFAULT_TARGET_CHARS = 1000
DEFAULT_OVERLAP_CHARS = 150


def validate_chunk_parameters(
    target_chars: int,
    overlap_chars: int,
) -> None:
    """
    Validate chunking configuration.

    Rules:
    - target_chars must be a positive integer
    - overlap_chars must be zero or greater
    - overlap_chars must be smaller than target_chars
    """

    if not isinstance(target_chars, int):
        raise TypeError("target_chars must be an integer")

    if not isinstance(overlap_chars, int):
        raise TypeError("overlap_chars must be an integer")

    if target_chars <= 0:
        raise ValueError(
            "target_chars must be greater than 0"
        )

    if overlap_chars < 0:
        raise ValueError(
            "overlap_chars cannot be negative"
        )

    if overlap_chars >= target_chars:
        raise ValueError(
            "overlap_chars must be smaller than target_chars"
        )


def split_into_paragraphs(text: str) -> list[str]:
    """
    Split cleaned text into non-empty paragraphs.

    Blank lines containing spaces or tabs are also
    recognised as paragraph boundaries.
    """

    if not text or not text.strip():
        return []

    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", text)
        if paragraph.strip()
    ]

    return paragraphs


def find_word_boundary(
    text: str,
    maximum_position: int,
) -> int:
    """
    Find a suitable whitespace boundary before the requested
    maximum position.

    If no useful whitespace boundary exists, fall back to the
    maximum character position.
    """

    if len(text) <= maximum_position:
        return len(text)

    boundary = text.rfind(
        " ",
        0,
        maximum_position + 1,
    )

    if boundary <= 0:
        return maximum_position

    return boundary


def split_oversized_paragraph(
    paragraph: str,
    target_chars: int = DEFAULT_TARGET_CHARS,
) -> list[str]:
    """
    Split an oversized paragraph while preferring word boundaries.

    Character-based splitting is used only when a suitable
    whitespace boundary cannot be found.
    """

    if not paragraph or not paragraph.strip():
        return []

    if not isinstance(target_chars, int):
        raise TypeError(
            "target_chars must be an integer"
        )

    if target_chars <= 0:
        raise ValueError(
            "target_chars must be greater than 0"
        )

    paragraph = paragraph.strip()

    if len(paragraph) <= target_chars:
        return [paragraph]

    pieces = []
    remaining = paragraph

    while remaining:
        remaining = remaining.strip()

        if not remaining:
            break

        if len(remaining) <= target_chars:
            pieces.append(remaining)
            break

        split_position = find_word_boundary(
            remaining,
            target_chars,
        )

        piece = remaining[:split_position].strip()

        if piece:
            pieces.append(piece)

        remaining = remaining[split_position:].strip()

    return pieces


def get_overlap_text(
    previous_chunk: str,
    overlap_chars: int,
) -> str:
    """
    Return overlap text from the end of the previous chunk.

    The overlap prefers a word boundary so it does not normally
    begin in the middle of a word.
    """

    if overlap_chars <= 0:
        return ""

    if len(previous_chunk) <= overlap_chars:
        return previous_chunk.strip()

    candidate = previous_chunk[-overlap_chars:]

    first_space = candidate.find(" ")

    if first_space != -1:
        candidate = candidate[first_space + 1:]

    return candidate.strip()


def add_overlap(
    chunks: list[str],
    overlap_chars: int = DEFAULT_OVERLAP_CHARS,
) -> list[str]:
    """
    Add controlled overlap between adjacent chunks.

    target_chars represents the approximate pre-overlap target.
    Final chunks may therefore be approximately:

    target_chars + overlap_chars

    plus a small separator.
    """

    if not chunks:
        return []

    if overlap_chars <= 0:
        return chunks.copy()

    overlapped_chunks = [chunks[0]]

    for index in range(1, len(chunks)):
        previous_chunk = chunks[index - 1]
        current_chunk = chunks[index].strip()

        overlap = get_overlap_text(
            previous_chunk,
            overlap_chars,
        )

        if overlap:
            current_chunk = (
                f"{overlap}\n{current_chunk}"
            )

        overlapped_chunks.append(current_chunk)

    return overlapped_chunks


def chunk_page_text(
    text: str,
    target_chars: int = DEFAULT_TARGET_CHARS,
    overlap_chars: int = DEFAULT_OVERLAP_CHARS,
) -> list[str]:
    """
    Convert one cleaned page into retrieval-ready chunks.

    Strategy:
    1. validate chunking parameters
    2. preserve the page boundary
    3. split on paragraph boundaries first
    4. split oversized paragraphs at word boundaries
    5. group units up to the approximate target size
    6. add controlled word-aware overlap

    The target size applies before overlap.
    """

    validate_chunk_parameters(
        target_chars=target_chars,
        overlap_chars=overlap_chars,
    )

    if not text or not text.strip():
        return []

    paragraphs = split_into_paragraphs(text)

    if not paragraphs:
        return []

    normalized_units = []

    for paragraph in paragraphs:
        normalized_units.extend(
            split_oversized_paragraph(
                paragraph,
                target_chars=target_chars,
            )
        )

    chunks = []
    current_chunk = ""

    for unit in normalized_units:
        if not current_chunk:
            current_chunk = unit
            continue

        candidate = (
            f"{current_chunk}\n\n{unit}"
        )

        if len(candidate) <= target_chars:
            current_chunk = candidate
        else:
            chunks.append(
                current_chunk.strip()
            )
            current_chunk = unit

    if current_chunk.strip():
        chunks.append(
            current_chunk.strip()
        )

    return add_overlap(
        chunks,
        overlap_chars=overlap_chars,
    )


def chunk_page_record(
    page_record: dict,
    target_chars: int = DEFAULT_TARGET_CHARS,
    overlap_chars: int = DEFAULT_OVERLAP_CHARS,
) -> list[dict]:
    """
    Convert a page-level record into retrieval-ready chunk records
    while preserving all existing provenance and metadata.

    Required provenance:
    - document_id
    - page or page_number
    - source_file

    Existing document metadata is copied into every chunk.
    """

    validate_chunk_parameters(
        target_chars=target_chars,
        overlap_chars=overlap_chars,
    )

    document_id = page_record.get(
        "document_id"
    )

    # Temporary compatibility with both names.
    page = page_record.get("page")

    if page is None:
        page = page_record.get(
            "page_number"
        )

    source_file = page_record.get(
        "source_file"
    )

    version = page_record.get(
        "version"
    )

    if not document_id:
        raise ValueError(
            "page_record is missing document_id"
        )

    if page is None:
        raise ValueError(
            "page_record is missing page"
        )

    if not source_file:
        raise ValueError(
            "page_record is missing source_file"
        )

    text = page_record.get(
        "text",
        "",
    )

    text_chunks = chunk_page_text(
        text=text,
        target_chars=target_chars,
        overlap_chars=overlap_chars,
    )

    records = []

    for chunk_number, chunk_text in enumerate(
        text_chunks,
        start=1,
    ):
        if version:
            chunk_id = (
                f"{document_id}-"
                f"V{version}-"
                f"P{page:03d}-"
                f"C{chunk_number:03d}"
            )
        else:
            chunk_id = (
                f"{document_id}-"
                f"P{page:03d}-"
                f"C{chunk_number:03d}"
            )

        # Preserve all upstream metadata.
        chunk_record = {
            **page_record,
            "page": page,
            "chunk_id": chunk_id,
            "chunk_number": chunk_number,
            "text": chunk_text,
        }

        records.append(
            chunk_record
        )

    return records




