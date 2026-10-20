from pathlib import Path

import numpy as np
import pytest

from src.application.app_dependencies import (
    AppDependencies,
)
from src.application.local_dependencies import (
    DEFAULT_LOCAL_EMBEDDING_MODEL_NAME,
    LocalDependencySettings,
    LocalDeterministicEmbeddingModel,
    default_local_dependency_loader,
    load_local_dependencies,
)
from src.application.runtime_config import (
    CONTROLLED_PROVIDER,
    DETERMINISTIC_ONLY,
    RAGRuntimeConfig,
)


def test_local_dependency_settings_accept_existing_directory(
    tmp_path,
):
    settings = LocalDependencySettings(
        project_root=tmp_path
    )

    assert (
        settings.project_root
        == tmp_path
    )


def test_local_dependency_settings_reject_non_path():
    with pytest.raises(
        ValueError,
        match="project_root must be a Path",
    ):
        LocalDependencySettings(
            project_root="."
        )


def test_local_dependency_settings_reject_missing_directory(
    tmp_path,
):
    missing = (
        tmp_path
        / "missing"
    )

    with pytest.raises(
        ValueError,
        match="project_root must exist",
    ):
        LocalDependencySettings(
            project_root=missing
        )


def test_local_dependency_settings_reject_file(
    tmp_path,
):
    file_path = (
        tmp_path
        / "file.txt"
    )

    file_path.write_text(
        "test",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match=(
            "project_root must be a directory"
        ),
    ):
        LocalDependencySettings(
            project_root=file_path
        )


def test_local_embedding_model_encodes_string():
    model = (
        LocalDeterministicEmbeddingModel()
    )

    vector = model.encode(
        "hello world"
    )

    assert isinstance(
        vector,
        np.ndarray,
    )

    assert (
        vector.ndim
        == 1
    )

    assert (
        len(
            vector
        )
        == 3
    )


def test_local_embedding_model_string_supports_tolist():
    model = (
        LocalDeterministicEmbeddingModel()
    )

    vector = model.encode(
        "hello world"
    )

    converted = (
        vector.tolist()
    )

    assert isinstance(
        converted,
        list,
    )

    assert len(
        converted
    ) == 3


def test_local_embedding_model_encodes_list():
    model = (
        LocalDeterministicEmbeddingModel()
    )

    vectors = model.encode(
        [
            "one",
            "two",
        ]
    )

    assert isinstance(
        vectors,
        np.ndarray,
    )

    assert (
        vectors.ndim
        == 2
    )

    assert (
        len(
            vectors
        )
        == 2
    )


def test_local_embedding_model_is_deterministic():
    model = (
        LocalDeterministicEmbeddingModel()
    )

    first = model.encode(
        [
            "same input"
        ]
    )

    second = model.encode(
        [
            "same input"
        ]
    )

    assert np.array_equal(
        first,
        second,
    )


@pytest.mark.parametrize(
    "value",
    [
        None,
        {},
        1,
        True,
    ],
)
def test_local_embedding_model_rejects_invalid_input(
    value,
):
    model = (
        LocalDeterministicEmbeddingModel()
    )

    with pytest.raises(
        ValueError,
        match=(
            "texts must be a string or list"
        ),
    ):
        model.encode(
            value
        )


def test_local_embedding_model_rejects_non_string_list_member():
    model = (
        LocalDeterministicEmbeddingModel()
    )

    with pytest.raises(
        ValueError,
        match=(
            "embedding input must be "
            "a string"
        ),
    ):
        model.encode(
            [
                "valid",
                1,
            ]
        )


def test_deterministic_local_dependencies_build(
    tmp_path,
):
    config = RAGRuntimeConfig(
        execution_mode=(
            DETERMINISTIC_ONLY
        )
    )

    dependencies = (
        load_local_dependencies(
            config,
            project_root=tmp_path,
        )
    )

    assert isinstance(
        dependencies,
        AppDependencies,
    )

    assert (
        dependencies.chunks
        == []
    )

    assert (
        dependencies.embedded_chunks
        == []
    )

    assert isinstance(
        dependencies.embedding_model,
        LocalDeterministicEmbeddingModel,
    )

    assert (
        dependencies.embedding_model_name
        == DEFAULT_LOCAL_EMBEDDING_MODEL_NAME
    )

    assert (
        dependencies.model_provider
        is None
    )


def test_controlled_provider_requires_provider(
    tmp_path,
):
    config = RAGRuntimeConfig(
        execution_mode=(
            CONTROLLED_PROVIDER
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "model_provider must be supplied"
        ),
    ):
        load_local_dependencies(
            config,
            project_root=tmp_path,
        )


def test_controlled_provider_accepts_supplied_provider(
    tmp_path,
):
    provider = object()

    config = RAGRuntimeConfig(
        execution_mode=(
            CONTROLLED_PROVIDER
        )
    )

    dependencies = (
        load_local_dependencies(
            config,
            project_root=tmp_path,
            model_provider=provider,
        )
    )

    assert (
        dependencies.model_provider
        is provider
    )


def test_default_loader_uses_current_directory(
    monkeypatch,
    tmp_path,
):
    monkeypatch.chdir(
        tmp_path
    )

    config = RAGRuntimeConfig(
        execution_mode=(
            DETERMINISTIC_ONLY
        )
    )

    dependencies = (
        default_local_dependency_loader(
            config
        )
    )

    assert isinstance(
        dependencies,
        AppDependencies,
    )


def test_invalid_runtime_config_is_rejected(
    tmp_path,
):
    with pytest.raises(
        ValueError,
        match=(
            "runtime_config must be "
            "a RAGRuntimeConfig"
        ),
    ):
        load_local_dependencies(
            {},
            project_root=tmp_path,
        )