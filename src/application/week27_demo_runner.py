"""Week 27 Day 6 — deterministic end-to-end portfolio demo runner.

Run from the repository root with:

    python -m src.application.week27_demo_runner

The runner uses the normal Week 27 application entry-point functions and a
small synthetic, non-patient evidence corpus.

The demo document is registered only for the lifetime of the demo execution.
The canonical document register is restored afterward.

The runner does not bypass retrieval, lifecycle checks, governance, generation,
assurance, or observability.
"""

from __future__ import annotations

from pathlib import Path

from src.application.app import (
    execute_application_command,
)
from src.application.week27_demo_data import (
    DEMO_QUESTION,
)
from src.application.week27_demo_dependencies import (
    temporary_demo_document_registration,
    week27_demo_dependency_loader,
)


DEFAULT_CONFIG_PATH = (
    "config/runtime_config.example.json"
)

DEFAULT_DEMO_LOG_PATH = (
    "outputs/week27_day6_demo_observability.jsonl"
)


def run_week27_demo(
    *,
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    log_jsonl: str | Path | None = None,
) -> tuple[int, dict | None, str]:
    """Run the synthetic case through the real governed application boundary."""

    with temporary_demo_document_registration():
        return execute_application_command(
            question=DEMO_QUESTION,
            config_path=config_path,
            dependency_loader=(
                week27_demo_dependency_loader
            ),
            query_date="2026-10-20",
            log_jsonl=log_jsonl,
        )


def main() -> int:
    """Execute the deterministic Week 27 portfolio demo."""

    exit_code, _, console_text = (
        run_week27_demo()
    )

    print(
        console_text
    )

    return exit_code


if __name__ == "__main__":
    raise SystemExit(
        main()
    )