"""Week 27 Day 6 — deterministic demo dependency composition.

This module composes the synthetic Week 27 Day 6 evidence corpus with the
existing application dependency contract.

The demo document uses a scoped temporary registration because the mature
retrieval layer requires document-level lifecycle metadata to be present in
the canonical document register.

The registration is restored after the demo run and does not permanently
alter the project's canonical corpus.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

from src.application.app_dependencies import (
    AppDependencies,
)
from src.application.local_dependencies import (
    DEFAULT_LOCAL_EMBEDDING_MODEL_NAME,
    LocalDeterministicEmbeddingModel,
)
from src.application.runtime_config import (
    CONTROLLED_PROVIDER,
    DETERMINISTIC_ONLY,
    RAGRuntimeConfig,
)
from src.application.week27_demo_data import (
    DEMO_DOCUMENT_ID,
    build_demo_chunk,
    build_demo_corpus,
)
from src.ingestion.document_metadata import (
    DOCUMENT_REGISTER,
    DocumentMetadata,
    validate_document_metadata,
)


def _validate_demo_runtime_config(
    runtime_config: RAGRuntimeConfig,
) -> None:
    if not isinstance(
        runtime_config,
        RAGRuntimeConfig,
    ):
        raise ValueError(
            "runtime_config must be a RAGRuntimeConfig."
        )

    if runtime_config.execution_mode not in {
        DETERMINISTIC_ONLY,
        CONTROLLED_PROVIDER,
    }:
        raise ValueError(
            "Unsupported execution mode."
        )


def build_demo_document_metadata() -> DocumentMetadata:
    """Build canonical document metadata for the synthetic demo document."""

    chunk = build_demo_chunk()

    metadata = DocumentMetadata(
        document_id=chunk[
            "document_id"
        ],
        title=chunk[
            "title"
        ],
        document_type=chunk[
            "document_type"
        ],
        source_type=chunk[
            "source_type"
        ],
        source_location=chunk[
            "source_location"
        ],
        source_file=chunk[
            "source_file"
        ],
        version=chunk[
            "version"
        ],
        effective_date=chunk[
            "effective_date"
        ],
        status=chunk[
            "status"
        ],
    )

    validate_document_metadata(
        metadata
    )

    return metadata


@contextmanager
def temporary_demo_document_registration(
) -> Iterator[DocumentMetadata]:
    """Temporarily register the Week 27 demo document.

    Any pre-existing entry with the same ID is preserved and restored.

    The global register is always restored in the finally block, including
    when retrieval or later application stages raise.
    """

    metadata = (
        build_demo_document_metadata()
    )

    previous = DOCUMENT_REGISTER.get(
        DEMO_DOCUMENT_ID
    )

    DOCUMENT_REGISTER[
        DEMO_DOCUMENT_ID
    ] = metadata

    try:
        yield metadata

    finally:
        if previous is None:
            DOCUMENT_REGISTER.pop(
                DEMO_DOCUMENT_ID,
                None,
            )
        else:
            DOCUMENT_REGISTER[
                DEMO_DOCUMENT_ID
            ] = previous


def load_week27_demo_dependencies(
    runtime_config: RAGRuntimeConfig,
    *,
    model_provider: Any = None,
) -> AppDependencies:
    """Build dependencies for the Week 27 deterministic portfolio demo."""

    _validate_demo_runtime_config(
        runtime_config
    )

    if (
        runtime_config.execution_mode
        == CONTROLLED_PROVIDER
        and model_provider is None
    ):
        raise ValueError(
            "model_provider must be supplied "
            "for CONTROLLED_PROVIDER mode."
        )

    chunks, embedded_chunks = (
        build_demo_corpus()
    )

    embedding_model = (
        LocalDeterministicEmbeddingModel()
    )

    return AppDependencies(
        chunks=chunks,
        embedded_chunks=embedded_chunks,
        embedding_model=embedding_model,
        embedding_model_name=(
            DEFAULT_LOCAL_EMBEDDING_MODEL_NAME
        ),
        model_provider=model_provider,
    )


def week27_demo_dependency_loader(
    runtime_config: RAGRuntimeConfig,
) -> AppDependencies:
    """Canonical deterministic demo dependency loader."""

    return load_week27_demo_dependencies(
        runtime_config
    )