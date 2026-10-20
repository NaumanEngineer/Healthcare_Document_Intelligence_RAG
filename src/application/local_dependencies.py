"""Week 27 Day 5 — reproducible local dependency composition.

This module provides a deterministic local dependency loader for the
Healthcare Document Intelligence RAG application entry point.

It is intentionally a development/local composition boundary. It does not
claim to be a production dependency container.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from src.application.app_dependencies import (
    AppDependencies,
)
from src.application.runtime_config import (
    CONTROLLED_PROVIDER,
    DETERMINISTIC_ONLY,
    RAGRuntimeConfig,
)


DEFAULT_LOCAL_EMBEDDING_MODEL_NAME = (
    "local-deterministic-embedding"
)


@dataclass(frozen=True)
class LocalDependencySettings:
    """Configuration for reproducible local dependency composition."""

    project_root: Path

    def __post_init__(self) -> None:
        if not isinstance(
            self.project_root,
            Path,
        ):
            raise ValueError(
                "project_root must be a Path."
            )

        if not self.project_root.exists():
            raise ValueError(
                "project_root must exist."
            )

        if not self.project_root.is_dir():
            raise ValueError(
                "project_root must be a directory."
            )


class LocalDeterministicEmbeddingModel:
    """Minimal deterministic embedding adapter for local execution.

    The adapter intentionally mirrors the part of the SentenceTransformer
    interface used by the existing retrieval layer.

    In particular, encode() returns a NumPy array so downstream code may call
    .tolist() exactly as it does with the production embedding model.
    """

    model_name = (
        DEFAULT_LOCAL_EMBEDDING_MODEL_NAME
    )

    def _encode_one(
        self,
        text: str,
    ) -> list[float]:
        if not isinstance(
            text,
            str,
        ):
            raise ValueError(
                "embedding input must be a string."
            )

        length = float(
            len(
                text
            )
        )

        checksum = float(
            sum(
                ord(
                    character
                )
                for character
                in text
            )
            % 1000
        )

        word_count = float(
            len(
                text.split()
            )
        )

        return [
            length,
            checksum,
            word_count,
        ]

    def encode(
        self,
        texts: Any,
        **_: Any,
    ) -> np.ndarray:
        if isinstance(
            texts,
            str,
        ):
            return np.asarray(
                self._encode_one(
                    texts
                ),
                dtype=float,
            )

        if isinstance(
            texts,
            list,
        ):
            vectors = [
                self._encode_one(
                    text
                )
                for text in texts
            ]

            return np.asarray(
                vectors,
                dtype=float,
            )

        raise ValueError(
            "texts must be a string or list."
        )


def _validate_runtime_config(
    runtime_config: RAGRuntimeConfig,
) -> None:
    if not isinstance(
        runtime_config,
        RAGRuntimeConfig,
    ):
        raise ValueError(
            "runtime_config must be "
            "a RAGRuntimeConfig."
        )

    if runtime_config.execution_mode not in {
        DETERMINISTIC_ONLY,
        CONTROLLED_PROVIDER,
    }:
        raise ValueError(
            "Unsupported execution mode."
        )


def _build_local_chunks() -> list:
    """Return the explicit local Day 5 corpus.

    Day 5 intentionally performs no hidden document ingestion.
    """

    return []


def _build_local_embedded_chunks() -> list:
    """Return the explicit local Day 5 embedded corpus."""

    return []


def load_local_dependencies(
    runtime_config: RAGRuntimeConfig,
    *,
    project_root: str | Path | None = None,
    model_provider: Any = None,
) -> AppDependencies:
    """Build reproducible local dependencies."""

    _validate_runtime_config(
        runtime_config
    )

    root = (
        Path.cwd()
        if project_root is None
        else Path(
            project_root
        )
    )

    LocalDependencySettings(
        project_root=root
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

    embedding_model = (
        LocalDeterministicEmbeddingModel()
    )

    return AppDependencies(
        chunks=_build_local_chunks(),
        embedded_chunks=(
            _build_local_embedded_chunks()
        ),
        embedding_model=embedding_model,
        embedding_model_name=(
            DEFAULT_LOCAL_EMBEDDING_MODEL_NAME
        ),
        model_provider=model_provider,
    )


def default_local_dependency_loader(
    runtime_config: RAGRuntimeConfig,
) -> AppDependencies:
    """Default dependency loader used by the local CLI."""

    return load_local_dependencies(
        runtime_config
    )