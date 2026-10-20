"""Tests for the Week 27 Day 6 deterministic demo runner."""

from pathlib import Path
from unittest.mock import patch

from src.application.app import (
    EXIT_SUCCESS,
)
from src.application.week27_demo_data import (
    DEMO_DOCUMENT_ID,
    DEMO_QUESTION,
)
from src.application.week27_demo_runner import (
    DEFAULT_CONFIG_PATH,
    main,
    run_week27_demo,
)
from src.ingestion.document_metadata import (
    DOCUMENT_REGISTER,
)


def _result():
    return {
        "request_id": "REQ-W27-DEMO",
        "status": "COMPLETED",
        "final_outcome": "ABSTAIN",
        "observability": {
            "status": "COMPLETED",
            "event_count": 11,
            "events": [],
        },
    }


def test_demo_runner_uses_demo_question():
    with patch(
        (
            "src.application.week27_demo_runner."
            "execute_application_command"
        ),
        return_value=(
            EXIT_SUCCESS,
            _result(),
            "Safe demo summary",
        ),
    ) as executor:
        run_week27_demo()

    kwargs = (
        executor.call_args.kwargs
    )

    assert (
        kwargs[
            "question"
        ]
        == DEMO_QUESTION
    )


def test_demo_runner_uses_default_config():
    with patch(
        (
            "src.application.week27_demo_runner."
            "execute_application_command"
        ),
        return_value=(
            EXIT_SUCCESS,
            _result(),
            "Safe demo summary",
        ),
    ) as executor:
        run_week27_demo()

    kwargs = (
        executor.call_args.kwargs
    )

    assert (
        kwargs[
            "config_path"
        ]
        == DEFAULT_CONFIG_PATH
    )


def test_demo_runner_uses_trusted_demo_date():
    with patch(
        (
            "src.application.week27_demo_runner."
            "execute_application_command"
        ),
        return_value=(
            EXIT_SUCCESS,
            _result(),
            "Safe demo summary",
        ),
    ) as executor:
        run_week27_demo()

    kwargs = (
        executor.call_args.kwargs
    )

    assert (
        kwargs[
            "query_date"
        ]
        == "2026-10-20"
    )


def test_demo_runner_forwards_log_path():
    with patch(
        (
            "src.application.week27_demo_runner."
            "execute_application_command"
        ),
        return_value=(
            EXIT_SUCCESS,
            _result(),
            "Safe demo summary",
        ),
    ) as executor:
        run_week27_demo(
            log_jsonl=Path(
                "outputs/demo.jsonl"
            )
        )

    kwargs = (
        executor.call_args.kwargs
    )

    assert (
        kwargs[
            "log_jsonl"
        ]
        == Path(
            "outputs/demo.jsonl"
        )
    )


def test_demo_registration_exists_during_execution_and_is_removed_after():
    assert (
        DEMO_DOCUMENT_ID
        not in DOCUMENT_REGISTER
    )

    def fake_execute_application_command(
        **kwargs,
    ):
        assert (
            DEMO_DOCUMENT_ID
            in DOCUMENT_REGISTER
        )

        return (
            EXIT_SUCCESS,
            _result(),
            "Safe demo summary",
        )

    with patch(
        (
            "src.application.week27_demo_runner."
            "execute_application_command"
        ),
        side_effect=(
            fake_execute_application_command
        ),
    ):
        run_week27_demo()

    assert (
        DEMO_DOCUMENT_ID
        not in DOCUMENT_REGISTER
    )


def test_demo_main_prints_safe_summary(
    capsys,
):
    with patch(
        (
            "src.application.week27_demo_runner."
            "run_week27_demo"
        ),
        return_value=(
            EXIT_SUCCESS,
            _result(),
            "Safe demo summary",
        ),
    ):
        exit_code = main()

    captured = (
        capsys.readouterr()
    )

    assert (
        exit_code
        == EXIT_SUCCESS
    )

    assert (
        "Safe demo summary"
        in captured.out
    )