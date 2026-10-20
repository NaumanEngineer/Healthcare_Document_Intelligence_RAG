import json

import pytest

from src.application.runtime_config import (
    CONTROLLED_PROVIDER,
    RAGRuntimeConfig,
    RetrievalConfig,
    RuntimeMetadata,
)
from src.application.runtime_config_io import (
    load_runtime_config,
    runtime_config_from_dict,
    save_runtime_config,
)


def test_runtime_config_from_dict_builds_valid_config():
    config = runtime_config_from_dict(
        {
            "execution_mode": "DETERMINISTIC_ONLY",
            "retrieval": {
                "semantic_k": 8,
                "keyword_k": 7,
                "final_k": 4,
                "rrf_k": 50,
                "max_related_chunks": 3,
            },
            "metadata": {
                "environment": "test",
                "application_name": "Healthcare RAG",
                "runtime_version": "week27-day3",
            },
        }
    )

    assert isinstance(
        config,
        RAGRuntimeConfig,
    )

    assert config.retrieval.semantic_k == 8
    assert config.retrieval.keyword_k == 7
    assert config.retrieval.final_k == 4
    assert config.metadata.environment == "test"


def test_unknown_top_level_key_is_rejected():
    with pytest.raises(
        ValueError,
        match="Unknown runtime configuration keys",
    ):
        runtime_config_from_dict(
            {
                "unexpected": True,
            }
        )


@pytest.mark.parametrize(
    "payload",
    [
        {
            "api_key": "secret",
        },
        {
            "metadata": {
                "password": "secret",
            }
        },
        {
            "retrieval": {
                "authorization_token": "secret",
            }
        },
        {
            "metadata": {
                "nested": {
                    "client_secret": "secret",
                }
            }
        },
    ],
)
def test_secret_like_keys_are_rejected(
    payload,
):
    with pytest.raises(
        ValueError,
        match="Forbidden sensitive configuration key",
    ):
        runtime_config_from_dict(
            payload
        )


def test_save_and_load_round_trip(
    tmp_path,
):
    config = RAGRuntimeConfig(
        retrieval=RetrievalConfig(
            semantic_k=12,
            keyword_k=9,
            final_k=5,
            semantic_min_similarity=0.4,
            keyword_min_score=1.2,
            min_rrf_score=0.02,
            rrf_k=55,
            max_related_chunks=4,
        ),
        metadata=RuntimeMetadata(
            environment="test",
            application_name="Healthcare RAG",
            runtime_version="week27-day3",
        ),
        execution_mode=CONTROLLED_PROVIDER,
    )

    path = tmp_path / "runtime_config.json"

    saved_path = save_runtime_config(
        config,
        path,
    )

    loaded = load_runtime_config(
        saved_path
    )

    assert loaded.to_dict() == config.to_dict()


def test_saved_json_contains_no_secret_fields(
    tmp_path,
):
    config = RAGRuntimeConfig()

    path = tmp_path / "runtime_config.json"

    save_runtime_config(
        config,
        path,
    )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    serialized = json.dumps(
        payload
    ).lower()

    assert "api_key" not in serialized
    assert "password" not in serialized
    assert "secret" not in serialized
    assert "token" not in serialized


def test_missing_file_is_rejected(
    tmp_path,
):
    path = tmp_path / "missing.json"

    with pytest.raises(
        ValueError,
        match="does not exist",
    ):
        load_runtime_config(
            path
        )


def test_non_json_file_is_rejected(
    tmp_path,
):
    path = tmp_path / "runtime_config.txt"

    path.write_text(
        "{}",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="must use .json",
    ):
        load_runtime_config(
            path
        )


def test_invalid_json_is_rejected(
    tmp_path,
):
    path = tmp_path / "runtime_config.json"

    path.write_text(
        "{invalid json",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="contains invalid JSON",
    ):
        load_runtime_config(
            path
        )


def test_loaded_invalid_execution_mode_is_rejected(
    tmp_path,
):
    path = tmp_path / "runtime_config.json"

    path.write_text(
        json.dumps(
            {
                "execution_mode": "UNKNOWN",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="execution_mode must be one of",
    ):
        load_runtime_config(
            path
        )