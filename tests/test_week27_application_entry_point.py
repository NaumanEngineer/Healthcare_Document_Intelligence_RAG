from pathlib import Path
from unittest.mock import patch

import pytest

from src.application.app import (
    EXIT_INVALID_INVOCATION,
    EXIT_RUNTIME_FAILURE,
    EXIT_SUCCESS,
    AppDependencies,
    build_argument_parser,
    build_safe_console_summary,
    execute_application_command,
    format_safe_console_summary,
    main,
    run_application,
    validate_dependencies_for_config,
)
from src.application.runtime_config import (
    CONTROLLED_PROVIDER,
    DETERMINISTIC_ONLY,
    RAGRuntimeConfig,
)


def _dependencies(
    *,
    model_provider=None,
):
    return AppDependencies(
        chunks=[],
        embedded_chunks=[],
        embedding_model=object(),
        embedding_model_name=(
            "test-embedding-model"
        ),
        model_provider=model_provider,
    )


def _observed_result():
    return {
        "request_id": "REQ-APP-001",
        "status": "COMPLETED",
        "final_outcome": (
            "REVIEW_REQUIRED"
        ),
        "observability": {
            "status": "COMPLETED",
            "event_count": 11,
            "events": [],
        },
        "question": (
            "Sensitive question text"
        ),
        "evidence": {
            "evidence_text": (
                "Sensitive evidence text"
            ),
        },
    }


def test_argument_parser_reads_required_question():
    parser = build_argument_parser()

    args = parser.parse_args(
        [
            "--question",
            "What is the policy?",
        ]
    )

    assert (
        args.question
        == "What is the policy?"
    )

    assert (
        args.config
        == (
            "config/"
            "runtime_config.example.json"
        )
    )


def test_argument_parser_reads_optional_values():
    parser = build_argument_parser()

    args = parser.parse_args(
        [
            "--question",
            "Test question",
            "--config",
            "config/test.json",
            "--query-date",
            "2026-10-20",
            "--log-jsonl",
            "outputs/log.jsonl",
        ]
    )

    assert (
        args.config
        == "config/test.json"
    )

    assert (
        args.query_date
        == "2026-10-20"
    )

    assert (
        args.log_jsonl
        == "outputs/log.jsonl"
    )


def test_empty_dependency_lists_are_valid():
    dependencies = AppDependencies(
        chunks=[],
        embedded_chunks=[],
        embedding_model=object(),
        embedding_model_name="model",
    )

    assert (
        dependencies.chunks
        == []
    )

    assert (
        dependencies.embedded_chunks
        == []
    )


@pytest.mark.parametrize(
    "value",
    [
        None,
        {},
        1,
        True,
        "invalid",
    ],
)
def test_invalid_dependency_chunks_are_rejected(
    value,
):
    with pytest.raises(
        ValueError,
        match="chunks must be a list",
    ):
        AppDependencies(
            chunks=value,
            embedded_chunks=[],
            embedding_model=object(),
            embedding_model_name="model",
        )


@pytest.mark.parametrize(
    "value",
    [
        None,
        {},
        1,
        True,
        "invalid",
    ],
)
def test_invalid_embedded_chunks_are_rejected(
    value,
):
    with pytest.raises(
        ValueError,
        match=(
            "embedded_chunks must be a list"
        ),
    ):
        AppDependencies(
            chunks=[],
            embedded_chunks=value,
            embedding_model=object(),
            embedding_model_name="model",
        )


@pytest.mark.parametrize(
    "name",
    [
        "",
        "   ",
        None,
        [],
        {},
        1,
        True,
    ],
)
def test_invalid_embedding_model_name_is_rejected(
    name,
):
    with pytest.raises(
        ValueError,
        match=(
            "embedding_model_name must be "
            "a non-empty string"
        ),
    ):
        AppDependencies(
            chunks=[],
            embedded_chunks=[],
            embedding_model=object(),
            embedding_model_name=name,
        )


def test_missing_embedding_model_is_rejected():
    with pytest.raises(
        ValueError,
        match="embedding_model is required",
    ):
        AppDependencies(
            chunks=[],
            embedded_chunks=[],
            embedding_model=None,
            embedding_model_name="model",
        )


def test_deterministic_mode_does_not_require_provider():
    config = RAGRuntimeConfig(
        execution_mode=(
            DETERMINISTIC_ONLY
        )
    )

    validate_dependencies_for_config(
        runtime_config=config,
        dependencies=_dependencies(),
    )


def test_controlled_provider_mode_requires_provider():
    config = RAGRuntimeConfig(
        execution_mode=(
            CONTROLLED_PROVIDER
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "model_provider is required"
        ),
    ):
        validate_dependencies_for_config(
            runtime_config=config,
            dependencies=_dependencies(),
        )


def test_run_application_delegates_to_observed_pipeline():
    config = RAGRuntimeConfig(
        execution_mode=(
            DETERMINISTIC_ONLY
        )
    )

    expected = _observed_result()

    with patch(
        (
            "src.application.app."
            "run_observed_rag_pipeline"
        ),
        return_value=expected,
    ) as runner:
        result = run_application(
            question="  Test question  ",
            runtime_config=config,
            dependencies=_dependencies(),
            query_date="2026-10-20",
        )

    assert result == expected

    kwargs = runner.call_args.kwargs

    assert (
        kwargs[
            "question"
        ]
        == "Test question"
    )

    assert (
        kwargs[
            "runtime_config"
        ]
        is config
    )

    assert (
        kwargs[
            "query_date"
        ]
        == "2026-10-20"
    )


def test_safe_console_summary_excludes_payload_content():
    summary = (
        build_safe_console_summary(
            _observed_result()
        )
    )

    serialized = str(
        summary
    )

    assert (
        "Sensitive question text"
        not in serialized
    )

    assert (
        "Sensitive evidence text"
        not in serialized
    )

    assert (
        summary[
            "final_outcome"
        ]
        == "REVIEW_REQUIRED"
    )


def test_safe_console_summary_can_include_log_path():
    summary = (
        build_safe_console_summary(
            _observed_result(),
            log_path=(
                "outputs/"
                "observability.jsonl"
            ),
        )
    )

    assert (
        summary[
            "log_path"
        ]
        == (
            "outputs/"
            "observability.jsonl"
        )
    )


def test_formatted_console_summary_is_operational_only():
    text = format_safe_console_summary(
        build_safe_console_summary(
            _observed_result()
        )
    )

    assert (
        "REQ-APP-001"
        in text
    )

    assert (
        "REVIEW_REQUIRED"
        in text
    )

    assert (
        "Sensitive question text"
        not in text
    )

    assert (
        "Sensitive evidence text"
        not in text
    )


def test_execute_application_command_success():
    expected = _observed_result()

    with patch(
        (
            "src.application.app."
            "load_application_config"
        ),
        return_value=RAGRuntimeConfig(),
    ), patch(
        (
            "src.application.app."
            "run_application"
        ),
        return_value=expected,
    ):
        exit_code, result, text = (
            execute_application_command(
                question="Test question",
                config_path=(
                    "config/test.json"
                ),
                dependency_loader=(
                    lambda config: (
                        _dependencies()
                    )
                ),
            )
        )

    assert (
        exit_code
        == EXIT_SUCCESS
    )

    assert result == expected

    assert (
        "REVIEW_REQUIRED"
        in text
    )


def test_review_required_is_successful_process_execution():
    expected = _observed_result()

    with patch(
        (
            "src.application.app."
            "load_application_config"
        ),
        return_value=RAGRuntimeConfig(),
    ), patch(
        (
            "src.application.app."
            "run_application"
        ),
        return_value=expected,
    ):
        exit_code, result, _ = (
            execute_application_command(
                question="Test",
                config_path="config/test.json",
                dependency_loader=(
                    lambda config: (
                        _dependencies()
                    )
                ),
            )
        )

    assert (
        result[
            "final_outcome"
        ]
        == "REVIEW_REQUIRED"
    )

    assert (
        exit_code
        == EXIT_SUCCESS
    )


def test_optional_jsonl_export_is_used():
    expected = _observed_result()

    with patch(
        (
            "src.application.app."
            "load_application_config"
        ),
        return_value=RAGRuntimeConfig(),
    ), patch(
        (
            "src.application.app."
            "run_application"
        ),
        return_value=expected,
    ), patch(
        (
            "src.application.app."
            "export_jsonl_log_records"
        ),
        return_value=Path(
            "outputs/log.jsonl"
        ),
    ) as exporter:
        exit_code, result, text = (
            execute_application_command(
                question="Test",
                config_path="config/test.json",
                dependency_loader=(
                    lambda config: (
                        _dependencies()
                    )
                ),
                log_jsonl=(
                    "outputs/log.jsonl"
                ),
            )
        )

    assert (
        exit_code
        == EXIT_SUCCESS
    )

    assert result == expected

    exporter.assert_called_once_with(
        expected,
        "outputs/log.jsonl",
    )

    assert (
        "outputs\\log.jsonl"
        in text
        or "outputs/log.jsonl"
        in text
    )


def test_log_export_failure_preserves_governed_result():
    expected = _observed_result()

    with patch(
        (
            "src.application.app."
            "load_application_config"
        ),
        return_value=RAGRuntimeConfig(),
    ), patch(
        (
            "src.application.app."
            "run_application"
        ),
        return_value=expected,
    ), patch(
        (
            "src.application.app."
            "export_jsonl_log_records"
        ),
        side_effect=RuntimeError(
            "Sensitive export detail"
        ),
    ):
        exit_code, result, text = (
            execute_application_command(
                question="Test",
                config_path="config/test.json",
                dependency_loader=(
                    lambda config: (
                        _dependencies()
                    )
                ),
                log_jsonl=(
                    "outputs/log.jsonl"
                ),
            )
        )

    assert (
        exit_code
        == EXIT_RUNTIME_FAILURE
    )

    assert result == expected

    assert (
        result[
            "final_outcome"
        ]
        == "REVIEW_REQUIRED"
    )

    assert (
        "RuntimeError"
        in text
    )

    assert (
        "Sensitive export detail"
        not in text
    )


def test_invalid_configuration_returns_exit_code_two():
    with patch(
        (
            "src.application.app."
            "load_application_config"
        ),
        side_effect=ValueError(
            "Sensitive invalid detail"
        ),
    ):
        exit_code, result, text = (
            execute_application_command(
                question="Test",
                config_path="bad.json",
                dependency_loader=(
                    lambda config: (
                        _dependencies()
                    )
                ),
            )
        )

    assert (
        exit_code
        == EXIT_INVALID_INVOCATION
    )

    assert result is None

    assert (
        "ValueError"
        in text
    )

    assert (
        "Sensitive invalid detail"
        not in text
    )


def test_unexpected_runtime_failure_returns_exit_code_one():
    with patch(
        (
            "src.application.app."
            "load_application_config"
        ),
        return_value=RAGRuntimeConfig(),
    ):
        def broken_loader(
            config,
        ):
            raise RuntimeError(
                "Sensitive runtime detail"
            )

        exit_code, result, text = (
            execute_application_command(
                question="Test",
                config_path=(
                    "config/test.json"
                ),
                dependency_loader=(
                    broken_loader
                ),
            )
        )

    assert (
        exit_code
        == EXIT_RUNTIME_FAILURE
    )

    assert result is None

    assert (
        "RuntimeError"
        in text
    )

    assert (
        "Sensitive runtime detail"
        not in text
    )


def test_main_uses_default_local_loader(
    capsys,
):
    with patch(
        (
            "src.application.app."
            "_load_default_dependency_loader"
        ),
        return_value=(
            lambda config: (
                _dependencies()
            )
        ),
    ) as loader, patch(
        (
            "src.application.app."
            "execute_application_command"
        ),
        return_value=(
            EXIT_SUCCESS,
            _observed_result(),
            "Safe summary",
        ),
    ):
        exit_code = main(
            [
                "--question",
                "Test question",
            ]
        )

    loader.assert_called_once()

    captured = capsys.readouterr()

    assert (
        exit_code
        == EXIT_SUCCESS
    )

    assert (
        "Safe summary"
        in captured.out
    )


def test_explicit_loader_overrides_default_loader(
    capsys,
):
    explicit_loader = (
        lambda config: (
            _dependencies()
        )
    )

    with patch(
        (
            "src.application.app."
            "_load_default_dependency_loader"
        ),
    ) as default_loader, patch(
        (
            "src.application.app."
            "execute_application_command"
        ),
        return_value=(
            EXIT_SUCCESS,
            _observed_result(),
            "Explicit loader summary",
        ),
    ):
        exit_code = main(
            [
                "--question",
                "Test question",
            ],
            dependency_loader=(
                explicit_loader
            ),
        )

    default_loader.assert_not_called()

    captured = capsys.readouterr()

    assert (
        exit_code
        == EXIT_SUCCESS
    )

    assert (
        "Explicit loader summary"
        in captured.out
    )


def test_main_forwards_jsonl_path(
    capsys,
):
    with patch(
        (
            "src.application.app."
            "_load_default_dependency_loader"
        ),
        return_value=(
            lambda config: (
                _dependencies()
            )
        ),
    ), patch(
        (
            "src.application.app."
            "execute_application_command"
        ),
        return_value=(
            EXIT_SUCCESS,
            _observed_result(),
            "Safe summary",
        ),
    ) as executor:
        exit_code = main(
            [
                "--question",
                "Test question",
                "--log-jsonl",
                "outputs/test.jsonl",
            ]
        )

    kwargs = (
        executor.call_args.kwargs
    )

    assert (
        kwargs[
            "log_jsonl"
        ]
        == "outputs/test.jsonl"
    )

    assert (
        exit_code
        == EXIT_SUCCESS
    )

    capsys.readouterr()