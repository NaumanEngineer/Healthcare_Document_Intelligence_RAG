import pytest

from src.application.runtime_config import (
    CONTROLLED_PROVIDER,
    DETERMINISTIC_ONLY,
    AssurancePolicy,
    RAGRuntimeConfig,
    RetrievalConfig,
    RuntimeMetadata,
    build_default_runtime_config,
)


def test_default_runtime_config_is_deterministic_only() -> None:
    config = build_default_runtime_config()

    assert config.execution_mode == DETERMINISTIC_ONLY
    assert config.assurance.require_citation_assurance is True
    assert config.assurance.require_faithfulness_assurance is True
    assert config.assurance.require_system_safety is True
    assert config.assurance.require_prompt_injection_check is True


def test_controlled_provider_mode_is_valid() -> None:
    config = RAGRuntimeConfig(
        execution_mode=CONTROLLED_PROVIDER
    )

    assert config.execution_mode == CONTROLLED_PROVIDER


@pytest.mark.parametrize(
    "mode",
    [
        "",
        "UNKNOWN",
        "AUTO",
        "PASS",
        None,
        [],
        {},
        True,
        1,
    ],
)
def test_invalid_execution_mode_is_rejected(
    mode,
) -> None:
    with pytest.raises(
        ValueError,
        match="execution_mode must be one of",
    ):
        RAGRuntimeConfig(
            execution_mode=mode
        )


@pytest.mark.parametrize(
    "field",
    [
        "semantic_k",
        "keyword_k",
        "final_k",
        "rrf_k",
        "max_related_chunks",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        0,
        -1,
        True,
        1.5,
        "10",
        None,
    ],
)
def test_positive_integer_retrieval_values_are_validated(
    field,
    value,
) -> None:
    kwargs = {
        field: value,
    }

    with pytest.raises(
        ValueError,
        match="must be a positive integer",
    ):
        RetrievalConfig(
            **kwargs
        )


@pytest.mark.parametrize(
    "field",
    [
        "semantic_min_similarity",
        "keyword_min_score",
        "min_rrf_score",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        -0.1,
        True,
        "0.5",
        [],
        {},
    ],
)
def test_optional_score_thresholds_are_validated(
    field,
    value,
) -> None:
    kwargs = {
        field: value,
    }

    with pytest.raises(
        ValueError,
        match="must be a non-negative number or None",
    ):
        RetrievalConfig(
            **kwargs
        )


def test_score_thresholds_allow_none() -> None:
    config = RetrievalConfig(
        semantic_min_similarity=None,
        keyword_min_score=None,
        min_rrf_score=None,
    )

    assert config.semantic_min_similarity is None
    assert config.keyword_min_score is None
    assert config.min_rrf_score is None


@pytest.mark.parametrize(
    "field",
    [
        "require_citation_assurance",
        "require_faithfulness_assurance",
        "require_system_safety",
        "require_prompt_injection_check",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        None,
        1,
        0,
        "true",
        [],
        {},
    ],
)
def test_assurance_policy_requires_booleans(
    field,
    value,
) -> None:
    kwargs = {
        field: value,
    }

    with pytest.raises(
        ValueError,
        match="must be a boolean",
    ):
        AssurancePolicy(
            **kwargs
        )


@pytest.mark.parametrize(
    "field",
    [
        "environment",
        "application_name",
        "runtime_version",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
        None,
        [],
        {},
        1,
    ],
)
def test_runtime_metadata_requires_non_empty_strings(
    field,
    value,
) -> None:
    kwargs = {
        field: value,
    }

    with pytest.raises(
        ValueError,
        match="must be a non-empty string",
    ):
        RuntimeMetadata(
            **kwargs
        )


def test_runtime_config_serialises_to_safe_dictionary() -> None:
    config = RAGRuntimeConfig(
        retrieval=RetrievalConfig(
            semantic_k=8,
            keyword_k=6,
            final_k=4,
            semantic_min_similarity=0.4,
            keyword_min_score=1.0,
            min_rrf_score=0.01,
            rrf_k=50,
            max_related_chunks=3,
        ),
        assurance=AssurancePolicy(),
        metadata=RuntimeMetadata(
            environment="test",
            application_name="Healthcare RAG Test",
            runtime_version="week27-day3",
        ),
        execution_mode=CONTROLLED_PROVIDER,
    )

    payload = config.to_dict()

    assert payload["execution_mode"] == CONTROLLED_PROVIDER
    assert payload["retrieval"]["semantic_k"] == 8
    assert payload["retrieval"]["final_k"] == 4
    assert payload["metadata"]["environment"] == "test"
    assert payload["metadata"]["runtime_version"] == "week27-day3"

    assert "provider" not in payload
    assert "api_key" not in payload
    assert "secret" not in payload