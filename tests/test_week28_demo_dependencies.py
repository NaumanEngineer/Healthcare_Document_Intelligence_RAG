"""Tests for Week 28 three-outcome demo dependency composition."""

from __future__ import annotations

import pytest

from src.application.app_dependencies import (
    AppDependencies,
)
from src.application.runtime_config import (
    RAGRuntimeConfig,
)
from src.application.week28_demo_data import (
    ABSTAIN_CASE_ID,
    ANSWER_CASE_ID,
    ANSWER_DOCUMENT_ID,
    REVIEW_CAPACITY_DOCUMENT_ID,
    REVIEW_CASE_ID,
    REVIEW_WORKFORCE_DOCUMENT_ID,
)
from src.application.week28_demo_dependencies import (
    SUPPORTED_CASE_IDS,
    build_week28_dependency_loader,
    load_week28_demo_dependencies,
    temporary_week28_document_registration,
)
from src.ingestion.document_metadata import (
    DOCUMENT_REGISTER,
)


def _runtime_config() -> RAGRuntimeConfig:
    return RAGRuntimeConfig()


def test_supported_case_ids_are_exact():
    assert SUPPORTED_CASE_IDS == {
        ANSWER_CASE_ID,
        REVIEW_CASE_ID,
        ABSTAIN_CASE_ID,
    }


def test_answer_dependencies_build_successfully():
    dependencies = (
        load_week28_demo_dependencies(
            _runtime_config(),
            case_id=ANSWER_CASE_ID,
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


def test_review_dependencies_build_successfully():
    dependencies = (
        load_week28_demo_dependencies(
            _runtime_config(),
            case_id=REVIEW_CASE_ID,
        )
    )

    assert isinstance(
        dependencies,
        AppDependencies,
    )

    assert len(
        dependencies.chunks
    ) == 2

    assert len(
        dependencies.embedded_chunks
    ) == 2


def test_abstain_dependencies_preserve_empty_corpus():
    dependencies = (
        load_week28_demo_dependencies(
            _runtime_config(),
            case_id=ABSTAIN_CASE_ID,
        )
    )

    assert isinstance(
        dependencies,
        AppDependencies,
    )

    assert dependencies.chunks == []
    assert dependencies.embedded_chunks == []


def test_answer_registration_is_scoped():
    assert (
        ANSWER_DOCUMENT_ID
        not in DOCUMENT_REGISTER
    )

    with temporary_week28_document_registration(
        ANSWER_CASE_ID
    ) as metadata_items:
        assert len(
            metadata_items
        ) == 1

        assert (
            ANSWER_DOCUMENT_ID
            in DOCUMENT_REGISTER
        )

    assert (
        ANSWER_DOCUMENT_ID
        not in DOCUMENT_REGISTER
    )


def test_review_registration_is_scoped():
    review_document_ids = {
        REVIEW_WORKFORCE_DOCUMENT_ID,
        REVIEW_CAPACITY_DOCUMENT_ID,
    }

    for document_id in review_document_ids:
        assert (
            document_id
            not in DOCUMENT_REGISTER
        )

    with temporary_week28_document_registration(
        REVIEW_CASE_ID
    ) as metadata_items:
        assert len(
            metadata_items
        ) == 2

        assert {
            metadata.document_id
            for metadata in metadata_items
        } == review_document_ids

        for document_id in review_document_ids:
            assert (
                document_id
                in DOCUMENT_REGISTER
            )

    for document_id in review_document_ids:
        assert (
            document_id
            not in DOCUMENT_REGISTER
        )


def test_abstain_registration_requires_no_documents():
    before = dict(
        DOCUMENT_REGISTER
    )

    with temporary_week28_document_registration(
        ABSTAIN_CASE_ID
    ) as metadata_items:
        assert metadata_items == []

    assert (
        DOCUMENT_REGISTER
        == before
    )


def test_registration_restores_existing_entry():
    original = DOCUMENT_REGISTER.get(
        ANSWER_DOCUMENT_ID
    )

    sentinel = object()

    DOCUMENT_REGISTER[
        ANSWER_DOCUMENT_ID
    ] = sentinel

    try:
        with temporary_week28_document_registration(
            ANSWER_CASE_ID
        ):
            assert (
                DOCUMENT_REGISTER[
                    ANSWER_DOCUMENT_ID
                ]
                is not sentinel
            )

        assert (
            DOCUMENT_REGISTER[
                ANSWER_DOCUMENT_ID
            ]
            is sentinel
        )

    finally:
        if original is None:
            DOCUMENT_REGISTER.pop(
                ANSWER_DOCUMENT_ID,
                None,
            )
        else:
            DOCUMENT_REGISTER[
                ANSWER_DOCUMENT_ID
            ] = original


def test_registration_restores_after_exception():
    assert (
        ANSWER_DOCUMENT_ID
        not in DOCUMENT_REGISTER
    )

    with pytest.raises(
        RuntimeError
    ):
        with temporary_week28_document_registration(
            ANSWER_CASE_ID
        ):
            assert (
                ANSWER_DOCUMENT_ID
                in DOCUMENT_REGISTER
            )

            raise RuntimeError(
                "synthetic test failure"
            )

    assert (
        ANSWER_DOCUMENT_ID
        not in DOCUMENT_REGISTER
    )


def test_unknown_case_id_is_rejected():
    with pytest.raises(
        ValueError
    ):
        load_week28_demo_dependencies(
            _runtime_config(),
            case_id=(
                "W28-DEMO-UNKNOWN"
            ),
        )


def test_dependency_loader_matches_application_contract():
    loader = (
        build_week28_dependency_loader(
            ANSWER_CASE_ID
        )
    )

    dependencies = loader(
        _runtime_config()
    )

    assert isinstance(
        dependencies,
        AppDependencies,
    )

    assert len(
        dependencies.chunks
    ) == 1