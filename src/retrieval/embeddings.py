from __future__ import annotations

import hashlib
import math
from typing import Iterable

from sentence_transformers import SentenceTransformer

from src.ingestion.chunk_metadata import validate_chunk_metadata


DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def create_text_hash(text: str) -> str:
    """
    Create a deterministic SHA-256 hash of chunk text.

    The hash helps detect stale embeddings when chunk text changes.
    """

    if not isinstance(text, str) or not text.strip():
        raise ValueError(
            "text must be a non-empty string"
        )

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def load_embedding_model(
    model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> SentenceTransformer:
    """
    Load the local sentence-transformer embedding model.
    """

    if not isinstance(model_name, str) or not model_name.strip():
        raise ValueError(
            "model_name must be a non-empty string"
        )

    return SentenceTransformer(model_name)


def validate_vector(vector: list[float]) -> None:
    """
    Validate an embedding vector.

    Rules:
    - must be a non-empty list
    - values must be numeric
    - values must be finite
    - vector must have non-zero norm
    """

    if not isinstance(vector, list) or not vector:
        raise ValueError(
            "vector must be a non-empty list"
        )

    for value in vector:
        if isinstance(value, bool):
            raise TypeError(
                "embedding vector cannot contain booleans"
            )

        if not isinstance(value, (int, float)):
            raise TypeError(
                "embedding vector must contain numeric values"
            )

        if not math.isfinite(value):
            raise ValueError(
                "embedding vector must contain only finite values"
            )

    norm = math.sqrt(
        sum(
            float(value) ** 2
            for value in vector
        )
    )

    if norm == 0:
        raise ValueError(
            "embedding vector must have non-zero norm"
        )


def embed_text(
    text: str,
    model: SentenceTransformer,
) -> list[float]:
    """
    Embed one non-empty text value using the supplied model.
    """

    if not isinstance(text, str) or not text.strip():
        raise ValueError(
            "text must be a non-empty string"
        )

    vector_array = model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=False,
    )

    vector = [
        float(value)
        for value in vector_array.tolist()
    ]

    validate_vector(vector)

    return vector


def embed_chunk(
    chunk: dict,
    model: SentenceTransformer,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> dict:
    """
    Convert one validated chunk into an embedding-ready record.

    The complete chunk record is preserved and embedding metadata
    is added.
    """

    validate_chunk_metadata(chunk)

    text = chunk["text"]

    vector = embed_text(
        text=text,
        model=model,
    )

    embedded_chunk = {
        **chunk,
        "vector": vector,
        "embedding_model": model_name,
        "embedding_dimensions": len(vector),
        "text_hash": create_text_hash(text),
    }

    return embedded_chunk


def embed_chunks(
    chunks: Iterable[dict],
    model: SentenceTransformer,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> list[dict]:
    """
    Embed multiple validated chunks.

    Failed chunks are not silently omitted.
    Any embedding failure is surfaced to the caller.
    """

    embedded_chunks = []

    for chunk in chunks:
        embedded_chunk = embed_chunk(
            chunk=chunk,
            model=model,
            model_name=model_name,
        )

        embedded_chunks.append(
            embedded_chunk
        )

    return embedded_chunks
