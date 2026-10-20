"""Week 27 Day 3 — canonical runtime configuration contract."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


DETERMINISTIC_ONLY = "DETERMINISTIC_ONLY"
CONTROLLED_PROVIDER = "CONTROLLED_PROVIDER"

VALID_EXECUTION_MODES = {
    DETERMINISTIC_ONLY,
    CONTROLLED_PROVIDER,
}


def _require_positive_int(
    value: Any,
    name: str,
) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value <= 0
    ):
        raise ValueError(
            f"{name} must be a positive integer."
        )

    return value


def _require_optional_non_negative_float(
    value: Any,
    name: str,
) -> float | None:
    if value is None:
        return None

    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or value < 0
    ):
        raise ValueError(
            f"{name} must be a non-negative number or None."
        )

    return float(value)


def _require_non_empty_string(
    value: Any,
    name: str,
) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
    ):
        raise ValueError(
            f"{name} must be a non-empty string."
        )

    return value.strip()


def _require_execution_mode(
    value: Any,
) -> str:
    if (
        not isinstance(value, str)
        or value not in VALID_EXECUTION_MODES
    ):
        raise ValueError(
            "execution_mode must be one of: "
            + ", ".join(
                sorted(
                    VALID_EXECUTION_MODES
                )
            )
        )

    return value


@dataclass(frozen=True)
class RetrievalConfig:
    """Canonical retrieval configuration."""

    semantic_k: int = 10
    keyword_k: int = 10
    final_k: int = 3
    semantic_min_similarity: float | None = None
    keyword_min_score: float | None = None
    min_rrf_score: float | None = None
    rrf_k: int = 60
    max_related_chunks: int = 2

    def __post_init__(self) -> None:
        _require_positive_int(
            self.semantic_k,
            "semantic_k",
        )

        _require_positive_int(
            self.keyword_k,
            "keyword_k",
        )

        _require_positive_int(
            self.final_k,
            "final_k",
        )

        _require_optional_non_negative_float(
            self.semantic_min_similarity,
            "semantic_min_similarity",
        )

        _require_optional_non_negative_float(
            self.keyword_min_score,
            "keyword_min_score",
        )

        _require_optional_non_negative_float(
            self.min_rrf_score,
            "min_rrf_score",
        )

        _require_positive_int(
            self.rrf_k,
            "rrf_k",
        )

        _require_positive_int(
            self.max_related_chunks,
            "max_related_chunks",
        )

    def to_dict(self) -> dict:
        return {
            "semantic_k": self.semantic_k,
            "keyword_k": self.keyword_k,
            "final_k": self.final_k,
            "semantic_min_similarity": (
                self.semantic_min_similarity
            ),
            "keyword_min_score": (
                self.keyword_min_score
            ),
            "min_rrf_score": (
                self.min_rrf_score
            ),
            "rrf_k": self.rrf_k,
            "max_related_chunks": (
                self.max_related_chunks
            ),
        }


@dataclass(frozen=True)
class AssurancePolicy:
    """Application-level required assurance policy."""

    require_citation_assurance: bool = True
    require_faithfulness_assurance: bool = True
    require_system_safety: bool = True
    require_prompt_injection_check: bool = True

    def __post_init__(self) -> None:
        fields = {
            "require_citation_assurance": (
                self.require_citation_assurance
            ),
            "require_faithfulness_assurance": (
                self.require_faithfulness_assurance
            ),
            "require_system_safety": (
                self.require_system_safety
            ),
            "require_prompt_injection_check": (
                self.require_prompt_injection_check
            ),
        }

        for name, value in fields.items():
            if not isinstance(value, bool):
                raise ValueError(
                    f"{name} must be a boolean."
                )

    def to_dict(self) -> dict:
        return {
            "require_citation_assurance": (
                self.require_citation_assurance
            ),
            "require_faithfulness_assurance": (
                self.require_faithfulness_assurance
            ),
            "require_system_safety": (
                self.require_system_safety
            ),
            "require_prompt_injection_check": (
                self.require_prompt_injection_check
            ),
        }


@dataclass(frozen=True)
class RuntimeMetadata:
    """Non-sensitive application runtime metadata."""

    environment: str = "development"
    application_name: str = (
        "Healthcare Document Intelligence RAG"
    )
    runtime_version: str = "week27"

    def __post_init__(self) -> None:
        _require_non_empty_string(
            self.environment,
            "environment",
        )

        _require_non_empty_string(
            self.application_name,
            "application_name",
        )

        _require_non_empty_string(
            self.runtime_version,
            "runtime_version",
        )

    def to_dict(self) -> dict:
        return {
            "environment": self.environment,
            "application_name": (
                self.application_name
            ),
            "runtime_version": (
                self.runtime_version
            ),
        }


@dataclass(frozen=True)
class RAGRuntimeConfig:
    """Top-level canonical Week 27 runtime configuration."""

    retrieval: RetrievalConfig = field(
        default_factory=RetrievalConfig
    )

    assurance: AssurancePolicy = field(
        default_factory=AssurancePolicy
    )

    metadata: RuntimeMetadata = field(
        default_factory=RuntimeMetadata
    )

    execution_mode: str = DETERMINISTIC_ONLY

    def __post_init__(self) -> None:
        _require_execution_mode(
            self.execution_mode
        )

        if not isinstance(
            self.retrieval,
            RetrievalConfig,
        ):
            raise ValueError(
                "retrieval must be a RetrievalConfig."
            )

        if not isinstance(
            self.assurance,
            AssurancePolicy,
        ):
            raise ValueError(
                "assurance must be an AssurancePolicy."
            )

        if not isinstance(
            self.metadata,
            RuntimeMetadata,
        ):
            raise ValueError(
                "metadata must be a RuntimeMetadata."
            )

    def to_dict(self) -> dict:
        return {
            "execution_mode": self.execution_mode,
            "retrieval": (
                self.retrieval.to_dict()
            ),
            "assurance": (
                self.assurance.to_dict()
            ),
            "metadata": (
                self.metadata.to_dict()
            ),
        }


def build_default_runtime_config() -> RAGRuntimeConfig:
    """Return the canonical safe default configuration."""

    return RAGRuntimeConfig()