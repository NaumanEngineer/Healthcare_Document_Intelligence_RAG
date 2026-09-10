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
    Validate the output Parquet path.

    The parent directory is created when needed.
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
    Convert one embedded or retrieval-ready chunk into
    the canonical analytical catalogue record.

    The vector itself is intentionally excluded from
    the first Parquet catalogue.

    Embedding metadata is retained.
    """

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

    return [
        normalise_chunk_for_parquet(chunk)
        for chunk in chunks
    ]


def write_chunks_to_parquet(
    chunks: list[dict],
    parquet_path: str | Path = DEFAULT_PARQUET_PATH,
) -> Path:
    """
    Persist chunk catalogue records to Parquet.

    This stores chunk metadata and text for analytical use.

    The embedding vector is intentionally excluded from
    this first catalogue implementation.
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


def query_chunk_catalogue(
    parquet_path: str | Path = DEFAULT_PARQUET_PATH,
) -> list[tuple]:
    """
    Query all chunk catalogue records from Parquet using DuckDB.
    """

    path = Path(parquet_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Parquet catalogue not found: {path}"
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
    Return document lifecycle counts from the Parquet catalogue.
    """

    path = Path(parquet_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Parquet catalogue not found: {path}"
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
    Return only chunks belonging to Active documents.
    """

    path = Path(parquet_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Parquet catalogue not found: {path}"
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
                page,
                chunk_number,
                source_file,
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
