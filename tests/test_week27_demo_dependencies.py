"""Tests for Week 27 Day 6 demo dependency composition."""

import pytest

from src.application.app_dependencies import (
    AppDependencies,
)
from src.application.local_dependencies import (
    DEFAULT_LOCAL_EMBEDDING_MODEL_NAME,
    LocalDeterministicEmbeddingModel,
)
from src.application.runtime_config import (
    CONTROLLED_PROVIDER,
    DETERMINISTIC_ONLY,
    RAGRuntimeConfig,
)
from src.application.week27_demo_data import (
    DEMO_CHUNK_ID,
    DEMO_DOCUMENT_ID,
)
from src.application.week27_demo_dependencies import (
    build_demo_document_metadata,
    load_week27_demo_dependencies,
    temporary_demo_document_registration,
    week27_demo_dependency_loader,
)
from src.ingestion.document_metadata import (
    DOCUMENT_REGISTER,
    DocumentMetadata,
)


def test_demo_document_metadata_is_valid_contract():
    metadata = (
        build_demo_document_metadata()
    )

    assert isinstance(
        metadata,
        DocumentMetadata,
    )

    assert (
        metadata.document_id
        == DEMO_DOCUMENT_ID
    )

    assert (
        metadata.status
        == "Active"
    )


def test_temporary_registration_adds_demo_document():
    assert (
        DEMO_DOCUMENT_ID
        not in DOCUMENT_REGISTER
    )

    with temporary_demo_document_registration():
        assert (
            DEMO_DOCUMENT_ID
            in DOCUMENT_REGISTER
        )

        metadata = (
            DOCUMENT_REGISTER[
                DEMO_DOCUMENT_ID
            ]
        )

        assert (
            metadata.document_id
            == DEMO_DOCUMENT_ID
        )

        assert (
            metadata.status
            == "Active"
        )

    assert (
        DEMO_DOCUMENT_ID
        not in DOCUMENT_REGISTER
    )


def test_temporary_registration_restores_after_exception():
    assert (
        DEMO_DOCUMENT_ID
        not in DOCUMENT_REGISTER
    )

    with pytest.raises(
        RuntimeError,
        match="synthetic failure",
    ):
        with temporary_demo_document_registration():
            assert (
                DEMO_DOCUMENT_ID
                in DOCUMENT_REGISTER
            )

            raise RuntimeError(
                "synthetic failure"
            )

    assert (
        DEMO_DOCUMENT_ID
        not in DOCUMENT_REGISTER
    )


def test_temporary_registration_restores_existing_entry():
    original = (
        build_demo_document_metadata()
    )

    DOCUMENT_REGISTER[
        DEMO_DOCUMENT_ID
    ] = original

    try:
        with temporary_demo_document_registration():
            assert (
                DEMO_DOCUMENT_ID
                in DOCUMENT_REGISTER
            )

        assert (
            DOCUMENT_REGISTER[
                DEMO_DOCUMENT_ID
            ]
            is original
        )

    finally:
        DOCUMENT_REGISTER.pop(
            DEMO_DOCUMENT_ID,
            None,
        )


def test_demo_dependencies_build_in_deterministic_mode():
    config = RAGRuntimeConfig(
        execution_mode=(
            DETERMINISTIC_ONLY
        )
    )

    dependencies = (
        load_week27_demo_dependencies(
            config
        )
    )

    assert isinstance(
        dependencies,
        AppDependencies,
    )

    assert len(
        dependencies.chunks
    ) == 1

    assert len(
        dependencies.embedded_chunks
    ) == 1


def test_demo_dependencies_use_expected_document():
    config = RAGRuntimeConfig(
        execution_mode=(
            DETERMINISTIC_ONLY
        )
    )

    dependencies = (
        load_week27_demo_dependencies(
            config
        )
    )

    assert (
        dependencies.chunks[
            0
        ][
            "document_id"
        ]
        == DEMO_DOCUMENT_ID
    )

    assert (
        dependencies.chunks[
            0
        ][
            "chunk_id"
        ]
        == DEMO_CHUNK_ID
    )


def test_demo_plain_and_embedded_identity_match():
    config = RAGRuntimeConfig(
        execution_mode=(
            DETERMINISTIC_ONLY
        )
    )

    dependencies = (
        load_week27_demo_dependencies(
            config
        )
    )

    plain = (
        dependencies.chunks[
            0
        ]
    )

    embedded = (
        dependencies.embedded_chunks[
            0
        ]
    )

    assert (
        plain[
            "chunk_id"
        ]
        == embedded[
            "chunk_id"
        ]
    )

    assert (
        plain[
            "document_id"
        ]
        == embedded[
            "document_id"
        ]
    )


def test_demo_dependencies_use_local_embedding_adapter():
    config = RAGRuntimeConfig(
        execution_mode=(
            DETERMINISTIC_ONLY
        )
    )

    dependencies = (
        load_week27_demo_dependencies(
            config
        )
    )

    assert isinstance(
        dependencies.embedding_model,
        LocalDeterministicEmbeddingModel,
    )

    assert (
        dependencies.embedding_model_name
        == DEFAULT_LOCAL_EMBEDDING_MODEL_NAME
    )


def test_demo_deterministic_mode_has_no_provider():
    config = RAGRuntimeConfig(
        execution_mode=(
            DETERMINISTIC_ONLY
        )
    )

    dependencies = (
        load_week27_demo_dependencies(
            config
        )
    )

    assert (
        dependencies.model_provider
        is None
    )


def test_demo_controlled_provider_requires_provider():
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
        load_week27_demo_dependencies(
            config
        )


def test_demo_controlled_provider_accepts_provider():
    config = RAGRuntimeConfig(
        execution_mode=(
            CONTROLLED_PROVIDER
        )
    )

    provider = object()

    dependencies = (
        load_week27_demo_dependencies(
            config,
            model_provider=provider,
        )
    )

    assert (
        dependencies.model_provider
        is provider
    )


def test_demo_loader_returns_application_contract():
    config = RAGRuntimeConfig(
        execution_mode=(
            DETERMINISTIC_ONLY
        )
    )

    dependencies = (
        week27_demo_dependency_loader(
            config
        )
    )

    assert isinstance(
        dependencies,
        AppDependencies,
    )


@pytest.mark.parametrize(
    "invalid",
    [
        None,
        {},
        [],
        "invalid",
        1,
        True,
    ],
)
def test_demo_loader_rejects_invalid_runtime_config(
    invalid,
):
    with pytest.raises(
        ValueError,
        match=(
            "runtime_config must be "
            "a RAGRuntimeConfig"
        ),
    ):
        load_week27_demo_dependencies(
            invalid
        )