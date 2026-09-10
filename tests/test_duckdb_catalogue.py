from __future__ import annotations

from pathlib import Path

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq


DEFAULT_PARQUET_PATH = Path(
    "data/processed/chunks.parquet"
)


PARQUET_FIELDS = [
    "chunk_id",
    "document_id",
    "title",
    "document_type",
    "source_type",
    "version",
    "effective_date",
    "status",
    "source_file",
    "source_location",
    "page",
    "chunk_number",
    "section",
    "topic",
    "ingestion_batch_id",
    "text",
    "embedding_model",
    "embedding_dimensions",
    "text_hash",
]


def validate_parquet_path(
    parquet_path: str | Path,
) -> Path:
    """
    Validate and prepare a Parquet output path.

    Rules:
    - path must end in .parquet
    - parent directory is created automatically
    """

    path = Path(parquet_path)

    if path.suffix.lower() != ".parquet":
        raise ValueError(
            "parquet_path must end with .parquet"
        )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    return path


def normalise_chunk_for_parquet(
    chunk: dict,
) -> dict:
    """
    Convert one retrieval-ready or embedded chunk into
    the canonical analytical catalogue record.

    The embedding vector is deliberately excluded from
    the first Parquet catalogue.

    Embedding metadata is preserved.
    """

    if not isinstance(chunk, dict):
        raise TypeError(
            "chunk must be a dictionary"
        )

    record = {}

    for field in PARQUET_FIELDS:
        record[field] = chunk.get(field)

    return record


def normalise_chunks_for_parquet(
    chunks: list[dict],
) -> list[dict]:
    """
    Normalise multiple chunks for Parquet persistence.
    """

    if not isinstance(chunks, list):
        raise TypeError(
            "chunks must be provided as a list"
        )

    return [
        normalise_chunk_for_parquet(
            chunk
        )
        for chunk in chunks
    ]


def write_chunks_to_parquet(
    chunks: list[dict],
    parquet_path: str | Path = DEFAULT_PARQUET_PATH,
) -> Path:
    """
    Persist chunk metadata and text to Parquet.

    The embedding vector is intentionally not written
    to this first analytical catalogue.

    Returns the final Parquet path.
    """

    if not isinstance(chunks, list):
        raise TypeError(
            "chunks must be provided as a list"
        )

    if not chunks:
        raise ValueError(
            "chunks must contain at least one record"
        )

    path = validate_parquet_path(
        parquet_path
    )

    records = normalise_chunks_for_parquet(
        chunks
    )

    table = pa.Table.from_pylist(
        records
    )

    pq.write_table(
        table,
        path,
    )

    return path


def open_duckdb_connection(
    database: str = ":memory:",
) -> duckdb.DuckDBPyConnection:
    """
    Open a DuckDB connection.

    The prototype defaults to an in-memory database.

    A persistent DuckDB database path may be supplied later.
    """

    if not isinstance(database, str):
        raise TypeError(
            "database must be a string"
        )

    if not database.strip():
        raise ValueError(
            "database must be a non-empty string"
        )

    return duckdb.connect(
        database=database
    )


def ensure_parquet_exists(
    parquet_path: str | Path,
) -> Path:
    """
    Validate that a Parquet catalogue exists before querying it.
    """

    path = Path(parquet_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Parquet catalogue not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Parquet path is not a file: {path}"
        )

    if path.suffix.lower() != ".parquet":
        raise ValueError(
            "Catalogue path must point to a .parquet file"
        )

    return path


def query_chunk_catalogue(
    parquet_path: str | Path = DEFAULT_PARQUET_PATH,
) -> list[tuple]:
    """
    Query canonical chunk catalogue records from Parquet
    using DuckDB.

    Results are ordered deterministically by:
    document_id → page → chunk_number.
    """

    path = ensure_parquet_exists(
        parquet_path
    )

    connection = open_duckdb_connection()

    try:
        result = connection.execute(
            """
            SELECT
                chunk_id,
                document_id,
                title,
                document_type,
                source_type,
                version,
                effective_date,
                status,
                source_file,
                source_location,
                page,
                chunk_number,
                section,
                topic,
                ingestion_batch_id,
                embedding_model,
                embedding_dimensions,
                text_hash,
                text
            FROM read_parquet(?)
            ORDER BY
                document_id,
                page,
                chunk_number
            """,
            [str(path)],
        ).fetchall()

    finally:
        connection.close()

    return result


def count_chunks_by_status(
    parquet_path: str | Path = DEFAULT_PARQUET_PATH,
) -> list[tuple]:
    """
    Return chunk counts grouped by document lifecycle status.
    """

    path = ensure_parquet_exists(
        parquet_path
    )

    connection = open_duckdb_connection()

    try:
        result = connection.execute(
            """
            SELECT
                status,
                COUNT(*) AS chunk_count
            FROM read_parquet(?)
            GROUP BY status
            ORDER BY status
            """,
            [str(path)],
        ).fetchall()

    finally:
        connection.close()

    return result


def get_active_chunks(
    parquet_path: str | Path = DEFAULT_PARQUET_PATH,
) -> list[tuple]:
    """
    Return chunks belonging only to Active documents.

    This mirrors the prototype retrieval-governance rule
    that only Active content is eligible by default.
    """

    path = ensure_parquet_exists(
        parquet_path
    )

    connection = open_duckdb_connection()

    try:
        result = connection.execute(
            """
            SELECT
                chunk_id,
                document_id,
                title,
                version,
                status,
                page,
                chunk_number,
                source_file,
                source_location,
                ingestion_batch_id,
                text
            FROM read_parquet(?)
            WHERE status = 'Active'
            ORDER BY
                document_id,
                page,
                chunk_number
            """,
            [str(path)],
        ).fetchall()

    finally:
        connection.close()

    return result


def get_chunk_count(
    parquet_path: str | Path = DEFAULT_PARQUET_PATH,
) -> int:
    """
    Return the total number of chunks in the catalogue.
    """

    path = ensure_parquet_exists(
        parquet_path
    )

    connection = open_duckdb_connection()

    try:
        result = connection.execute(
            """
            SELECT COUNT(*)
            FROM read_parquet(?)
            """,
            [str(path)],
        ).fetchone()

    finally:
        connection.close()

    if result is None:
        return 0

    return int(result[0])


def get_document_chunk_counts(
    parquet_path: str | Path = DEFAULT_PARQUET_PATH,
) -> list[tuple]:
    """
    Return chunk counts grouped by source document.

    Useful for QA and future DuckDB/Fabric monitoring.
    """

    path = ensure_parquet_exists(
        parquet_path
    )

    connection = open_duckdb_connection()

    try:
        result = connection.execute(
            """
            SELECT
                document_id,
                COUNT(*) AS chunk_count
            FROM read_parquet(?)
            GROUP BY document_id
            ORDER BY document_id
            """,
            [str(path)],
        ).fetchall()

    finally:
        connection.close()

    return result


def get_average_chunk_length(
    parquet_path: str | Path = DEFAULT_PARQUET_PATH,
) -> float:
    """
    Return the average chunk text length in characters.
    """

    path = ensure_parquet_exists(
        parquet_path
    )

    connection = open_duckdb_connection()

    try:
        result = connection.execute(
            """
            SELECT AVG(LENGTH(text))
            FROM read_parquet(?)
            """,
            [str(path)],
        ).fetchone()

    finally:
        connection.close()

    if result is None or result[0] is None:
        return 0.0

    return float(result[0])


def get_catalogue_summary(
    parquet_path: str | Path = DEFAULT_PARQUET_PATH,
) -> dict:
    """
    Build a simple analytical summary of the Parquet
    knowledge catalogue using DuckDB.

    This is intended for local QA and future monitoring.
    """

    return {
        "total_chunks": get_chunk_count(
            parquet_path
        ),
        "chunks_by_document": (
            get_document_chunk_counts(
                parquet_path
            )
        ),
        "chunks_by_status": (
            count_chunks_by_status(
                parquet_path
            )
        ),
        "average_chunk_length": (
            get_average_chunk_length(
                parquet_path
            )
        ),
    }
