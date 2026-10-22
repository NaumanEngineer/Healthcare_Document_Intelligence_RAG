"""Week 28 — three-outcome deterministic demo dependencies.

This module composes the synthetic Week 28 portfolio cases with the existing
application dependency contract.

It does not assign or force governance outcomes.

The synthetic documents are temporarily registered because the mature evidence
and provenance pipeline validates lifecycle metadata against the canonical
document register.

All temporary registrations are restored after each demo run.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

from src.application.app_dependencies import AppDependencies
from src.application.local_dependencies import (
    DEFAULT_LOCAL_EMBEDDING_MODEL_NAME,
    LocalDeterministicEmbeddingModel,
)
from src.application.runtime_config import (
    CONTROLLED_PROVIDER,
    DETERMINISTIC_ONLY,
    RAGRuntimeConfig,
)
from src.application.week28_demo_data import (
    ANSWER_CASE_ID,
    ABSTAIN_CASE_ID,
    REVIEW_CASE_ID,
    build_week28_demo_cases,
)
from src.ingestion.document_metadata import (
    DOCUMENT_REGISTER,
    DocumentMetadata,
    validate_document_metadata,
)


SUPPORTED_CASE_IDS = {
    ANSWER_CASE_ID,
    REVIEW_CASE_ID,
    ABSTAIN_CASE_ID,
}


def _validate_runtime_config(
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


def _get_demo_case(
    case_id: str,
) -> dict:
    if (
        not isinstance(
            case_id,
            str,
        )
        or not case_id.strip()
    ):
        raise ValueError(
            "case_id must be a non-empty string."
        )

    normalized_case_id = (
        case_id.strip()
    )

    if normalized_case_id not in SUPPORTED_CASE_IDS:
        raise ValueError(
            "Unknown Week 28 demo case."
        )

    for case in build_week28_demo_cases():
        if (
            case[
                "case_id"
            ]
            == normalized_case_id
        ):
            return case

    raise ValueError(
        "Week 28 demo case could not be loaded."
    )


def _build_document_metadata(
    chunk: dict,
) -> DocumentMetadata:
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
def temporary_week28_document_registration(
    case_id: str,
) -> Iterator[list[DocumentMetadata]]:
    """Temporarily register all documents required by one demo case.

    Existing register entries are preserved and restored.

    The ABSTAIN case contains no evidence documents, so the context manager
    simply yields an empty metadata list.

    This helper is demonstration-only. It does not change the production
    document-register design.
    """

    case = _get_demo_case(
        case_id
    )

    chunks = case[
        "chunks"
    ]

    metadata_items = []
    previous_entries = {}

    try:
        for chunk in chunks:
            metadata = (
                _build_document_metadata(
                    chunk
                )
            )

            document_id = (
                metadata.document_id
            )

            previous_entries[
                document_id
            ] = DOCUMENT_REGISTER.get(
                document_id
            )

            DOCUMENT_REGISTER[
                document_id
            ] = metadata

            metadata_items.append(
                metadata
            )

        yield metadata_items

    finally:
        for document_id in list(
            previous_entries
        ):
            previous = (
                previous_entries[
                    document_id
                ]
            )

            if previous is None:
                DOCUMENT_REGISTER.pop(
                    document_id,
                    None,
                )
            else:
                DOCUMENT_REGISTER[
                    document_id
                ] = previous


def load_week28_demo_dependencies(
    runtime_config: RAGRuntimeConfig,
    *,
    case_id: str,
    model_provider: Any = None,
) -> AppDependencies:
    """Build dependencies for one Week 28 governed demo case."""

    _validate_runtime_config(
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

    case = _get_demo_case(
        case_id
    )

    embedding_model = (
        LocalDeterministicEmbeddingModel()
    )

    return AppDependencies(
        chunks=case[
            "chunks"
        ],
        embedded_chunks=case[
            "embedded_chunks"
        ],
        embedding_model=embedding_model,
        embedding_model_name=(
            DEFAULT_LOCAL_EMBEDDING_MODEL_NAME
        ),
        model_provider=model_provider,
    )


def build_week28_dependency_loader(
    case_id: str,
):
    """Return an application-compatible dependency loader for one case."""

    _get_demo_case(
        case_id
    )

    def _loader(
        runtime_config: RAGRuntimeConfig,
    ) -> AppDependencies:
        return load_week28_demo_dependencies(
            runtime_config,
            case_id=case_id,
        )

    return _loader