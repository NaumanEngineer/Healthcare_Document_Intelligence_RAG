"""Week 27 Day 5 — shared application dependency contract.

This module owns the dependency object used by both the application entry
point and local dependency composition.

Keeping this contract outside app.py prevents class-identity duplication when
the application is launched with:

    python -m src.application.app
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AppDependencies:
    """Explicit dependencies required by the governed RAG application."""

    chunks: list
    embedded_chunks: list
    embedding_model: Any
    embedding_model_name: str
    model_provider: Any = None

    def __post_init__(self) -> None:
        if not isinstance(
            self.chunks,
            list,
        ):
            raise ValueError(
                "chunks must be a list."
            )

        if not isinstance(
            self.embedded_chunks,
            list,
        ):
            raise ValueError(
                "embedded_chunks must be a list."
            )

        if self.embedding_model is None:
            raise ValueError(
                "embedding_model is required."
            )

        if (
            not isinstance(
                self.embedding_model_name,
                str,
            )
            or not self.embedding_model_name.strip()
        ):
            raise ValueError(
                "embedding_model_name must be "
                "a non-empty string."
            )