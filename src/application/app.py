"""Week 27 Day 5 — reproducible application entry point.

This module provides the thin command-line and callable application boundary
for the Healthcare Document Intelligence RAG project.

Responsibilities are deliberately limited to:

- command-line parsing;
- validated runtime configuration loading;
- explicit dependency composition;
- delegation to the observed governed RAG pipeline;
- safe operational console output;
- optional safe observability JSONL export;
- process exit-code handling.

Retrieval, evidence construction, governance, generation, assurance, and
observability logic remain in their existing authoritative modules.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable, Sequence

from src.application.app_dependencies import (
    AppDependencies,
)
from src.application.observability_logging import (
    export_jsonl_log_records,
)
from src.application.observed_rag_pipeline import (
    run_observed_rag_pipeline,
)
from src.application.runtime_config import (
    CONTROLLED_PROVIDER,
    RAGRuntimeConfig,
)
from src.application.runtime_config_io import (
    load_runtime_config,
)


EXIT_SUCCESS = 0
EXIT_RUNTIME_FAILURE = 1
EXIT_INVALID_INVOCATION = 2


DependencyLoader = Callable[
    [RAGRuntimeConfig],
    AppDependencies,
]


def build_argument_parser() -> argparse.ArgumentParser:
    """Build the canonical Week 27 Day 5 command-line parser."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m "
            "src.application.app"
        ),
        description=(
            "Run the governed Healthcare "
            "Document Intelligence RAG application."
        ),
    )

    parser.add_argument(
        "--question",
        required=True,
        help=(
            "Question to submit to the "
            "governed RAG application."
        ),
    )

    parser.add_argument(
        "--config",
        default=(
            "config/"
            "runtime_config.example.json"
        ),
        help=(
            "Path to validated runtime "
            "configuration JSON."
        ),
    )

    parser.add_argument(
        "--query-date",
        default=None,
        help=(
            "Optional trusted query date "
            "using YYYY-MM-DD."
        ),
    )

    parser.add_argument(
        "--log-jsonl",
        default=None,
        help=(
            "Optional path for safe "
            "observability JSONL export."
        ),
    )

    return parser


def _require_non_empty_question(
    question,
) -> str:
    if (
        not isinstance(
            question,
            str,
        )
        or not question.strip()
    ):
        raise ValueError(
            "question must be a non-empty string."
        )

    return question.strip()


def load_application_config(
    path: str | Path,
) -> RAGRuntimeConfig:
    """Load the existing validated runtime configuration."""

    if not isinstance(
        path,
        (
            str,
            Path,
        ),
    ):
        raise ValueError(
            "config path must be a string or Path."
        )

    return load_runtime_config(
        path
    )


def validate_dependencies_for_config(
    *,
    runtime_config: RAGRuntimeConfig,
    dependencies: AppDependencies,
) -> None:
    """Validate entry-point dependency requirements."""

    if not isinstance(
        runtime_config,
        RAGRuntimeConfig,
    ):
        raise ValueError(
            "runtime_config must be "
            "a RAGRuntimeConfig."
        )

    if not isinstance(
        dependencies,
        AppDependencies,
    ):
        raise ValueError(
            "dependencies must be "
            "AppDependencies."
        )

    if (
        runtime_config.execution_mode
        == CONTROLLED_PROVIDER
        and dependencies.model_provider
        is None
    ):
        raise ValueError(
            "model_provider is required "
            "for CONTROLLED_PROVIDER mode."
        )


def run_application(
    *,
    question: str,
    runtime_config: RAGRuntimeConfig,
    dependencies: AppDependencies,
    query_date: str | None = None,
) -> dict:
    """Run the existing observed governed RAG application."""

    safe_question = (
        _require_non_empty_question(
            question
        )
    )

    validate_dependencies_for_config(
        runtime_config=runtime_config,
        dependencies=dependencies,
    )

    return run_observed_rag_pipeline(
        question=safe_question,
        chunks=dependencies.chunks,
        embedded_chunks=(
            dependencies.embedded_chunks
        ),
        embedding_model=(
            dependencies.embedding_model
        ),
        embedding_model_name=(
            dependencies.embedding_model_name
        ),
        model_provider=(
            dependencies.model_provider
        ),
        query_date=query_date,
        runtime_config=runtime_config,
    )


def build_safe_console_summary(
    result: dict,
    *,
    log_path: str | Path | None = None,
) -> dict:
    """Build a content-minimised operational summary."""

    if not isinstance(
        result,
        dict,
    ):
        raise ValueError(
            "result must be a dictionary."
        )

    observability = result.get(
        "observability",
        {},
    )

    if not isinstance(
        observability,
        dict,
    ):
        observability = {}

    return {
        "request_id": (
            result.get(
                "request_id"
            )
        ),
        "status": (
            result.get(
                "status"
            )
        ),
        "final_outcome": (
            result.get(
                "final_outcome"
            )
        ),
        "observability_status": (
            observability.get(
                "status"
            )
        ),
        "observability_event_count": (
            observability.get(
                "event_count"
            )
        ),
        "log_path": (
            str(
                log_path
            )
            if log_path is not None
            else None
        ),
    }


def format_safe_console_summary(
    summary: dict,
) -> str:
    """Format safe operational output."""

    if not isinstance(
        summary,
        dict,
    ):
        raise ValueError(
            "summary must be a dictionary."
        )

    lines = [
        "Healthcare Document Intelligence RAG",
        "------------------------------------",
        (
            "Request ID: "
            f"{summary.get('request_id')}"
        ),
        (
            "Application status: "
            f"{summary.get('status')}"
        ),
        (
            "Final outcome: "
            f"{summary.get('final_outcome')}"
        ),
        (
            "Observability: "
            f"{summary.get('observability_status')}"
        ),
        (
            "Observed events: "
            f"{summary.get('observability_event_count')}"
        ),
    ]

    log_path = summary.get(
        "log_path"
    )

    if log_path:
        lines.append(
            "Observability log: "
            f"{log_path}"
        )

    return "\n".join(
        lines
    )


def _export_observability_if_requested(
    *,
    result: dict,
    log_jsonl: str | Path | None,
) -> Path | None:
    if log_jsonl is None:
        return None

    return export_jsonl_log_records(
        result,
        log_jsonl,
    )


def execute_application_command(
    *,
    question: str,
    config_path: str | Path,
    dependency_loader: DependencyLoader,
    query_date: str | None = None,
    log_jsonl: str | Path | None = None,
) -> tuple[int, dict | None, str]:
    """Execute one complete application command."""

    try:
        if not callable(
            dependency_loader
        ):
            raise ValueError(
                "dependency_loader must be callable."
            )

        runtime_config = (
            load_application_config(
                config_path
            )
        )

        dependencies = (
            dependency_loader(
                runtime_config
            )
        )

        if not isinstance(
            dependencies,
            AppDependencies,
        ):
            raise ValueError(
                "dependency_loader must return "
                "AppDependencies."
            )

        result = run_application(
            question=question,
            runtime_config=runtime_config,
            dependencies=dependencies,
            query_date=query_date,
        )

    except (
        ValueError,
        FileNotFoundError,
        OSError,
    ) as exc:
        return (
            EXIT_INVALID_INVOCATION,
            None,
            (
                "Application could not start "
                "safely.\n"
                "Error type: "
                f"{type(exc).__name__}"
            ),
        )

    except Exception as exc:
        return (
            EXIT_RUNTIME_FAILURE,
            None,
            (
                "Application execution failed "
                "safely.\n"
                "Error type: "
                f"{type(exc).__name__}"
            ),
        )

    try:
        exported_path = (
            _export_observability_if_requested(
                result=result,
                log_jsonl=log_jsonl,
            )
        )

    except Exception as exc:
        summary = (
            build_safe_console_summary(
                result
            )
        )

        return (
            EXIT_RUNTIME_FAILURE,
            result,
            (
                format_safe_console_summary(
                    summary
                )
                + "\n"
                + "Observability export failed "
                + "safely.\n"
                + "Error type: "
                + type(
                    exc
                ).__name__
            ),
        )

    summary = build_safe_console_summary(
        result,
        log_path=exported_path,
    )

    return (
        EXIT_SUCCESS,
        result,
        format_safe_console_summary(
            summary
        ),
    )


def _load_default_dependency_loader() -> DependencyLoader:
    """Load the default local dependency adapter lazily."""

    from src.application.local_dependencies import (
        default_local_dependency_loader,
    )

    return default_local_dependency_loader


def main(
    argv: Sequence[str] | None = None,
    *,
    dependency_loader: (
        DependencyLoader | None
    ) = None,
) -> int:
    """Canonical command-line entry point."""

    parser = build_argument_parser()

    args = parser.parse_args(
        argv
    )

    active_dependency_loader = (
        dependency_loader
        if dependency_loader is not None
        else _load_default_dependency_loader()
    )

    exit_code, _, console_text = (
        execute_application_command(
            question=args.question,
            config_path=args.config,
            dependency_loader=(
                active_dependency_loader
            ),
            query_date=args.query_date,
            log_jsonl=args.log_jsonl,
        )
    )

    print(
        console_text
    )

    return exit_code


if __name__ == "__main__":
    raise SystemExit(
        main()
    )