from __future__ import annotations


DEFAULT_TARGET_CHARS = 1000
DEFAULT_OVERLAP_CHARS = 150


def split_into_paragraphs(text: str) -> list[str]:
    """
    Split cleaned text into non-empty paragraphs.
    """

    if not text:
        return []

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    return paragraphs


def split_oversized_paragraph(
    paragraph: str,
    target_chars: int = DEFAULT_TARGET_CHARS,
) -> list[str]:
    """
    Split a paragraph that is too large into smaller
    character-based pieces.

    This is a fallback only.
    Natural paragraph boundaries are preferred.
    """

    if len(paragraph) <= target_chars:
        return [paragraph]

    pieces = []
    start = 0

    while start < len(paragraph):
        end = min(start + target_chars, len(paragraph))

        piece = paragraph[start:end].strip()

        if piece:
            pieces.append(piece)

        start = end

    return pieces


def add_overlap(
    chunks: list[str],
    overlap_chars: int = DEFAULT_OVERLAP_CHARS,
) -> list[str]:
    """
    Add controlled overlap between adjacent chunks.
    """

    if not chunks:
        return []

    if overlap_chars <= 0:
        return chunks

    overlapped_chunks = [chunks[0]]

    for index in range(1, len(chunks)):
        previous_chunk = chunks[index - 1]
        current_chunk = chunks[index].strip()

        overlap = previous_chunk[-overlap_chars:].strip()

        if overlap:
            current_chunk = f"{overlap}\n{current_chunk}"

        overlapped_chunks.append(current_chunk)

    return overlapped_chunks


def chunk_page_text(
    text: str,
    target_chars: int = DEFAULT_TARGET_CHARS,
    overlap_chars: int = DEFAULT_OVERLAP_CHARS,
) -> list[str]:
    """
    Convert one cleaned page into retrieval-ready text chunks.

    Strategy:
    1. preserve page boundary
    2. split by paragraph first
    3. split oversized paragraphs only when necessary
    4. group paragraphs up to target size
    5. add controlled overlap
    """

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

        candidate = f"{current_chunk}\n\n{unit}"

        if len(candidate) <= target_chars:
            current_chunk = candidate
        else:
            chunks.append(current_chunk.strip())
            current_chunk = unit

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

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
    Convert a page-level record into chunk-level records
    while preserving document provenance.

    Every chunk receives:
    - stable chunk_id
    - document_id
    - page_number
    - chunk_number
    - text
    - source_file
    """

    document_id = page_record.get("document_id")
    page_number = page_record.get("page_number")

    # Provenance validation
    if not document_id:
        raise ValueError(
            "page_record is missing document_id"
        )

    if page_number is None:
        raise ValueError(
            "page_record is missing page_number"
        )

    text = page_record.get("text", "")

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
        # Stable retrieval identifier
        # Example:
        # DOC-001-P003-C002
        chunk_id = (
            f"{document_id}-"
            f"P{page_number:03d}-"
            f"C{chunk_number:03d}"
        )

        records.append(
            {
                "chunk_id": chunk_id,
                "document_id": document_id,
                "page_number": page_number,
                "chunk_number": chunk_number,
                "text": chunk_text,
                "source_file": page_record.get(
                    "source_file"
                ),
            }
        )

    return records


