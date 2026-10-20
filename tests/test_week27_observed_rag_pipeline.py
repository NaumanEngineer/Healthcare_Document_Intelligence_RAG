from copy import deepcopy
from unittest.mock import patch

import pytest

from src.application.observed_rag_pipeline import (
    OBSERVABILITY_COMPLETED,
    OBSERVABILITY_FAILED,
    attach_observability,
    run_observed_rag_pipeline,
)
from src.application.runtime_config import (
    DETERMINISTIC_ONLY,
)


def _canonical_result():
    return {
        "request_id": "REQ-OBS-001",
        "status": "COMPLETED",
        "final_outcome": (
            "REVIEW_REQUIRED"
        ),
        "execution_trace": [
            "REQUEST_RECEIVED",
            "INPUT_VALIDATED",
            "RETRIEVAL_COMPLETED",
            "EVIDENCE_PACKET_BUILT",
            "PRE_GOVERNANCE_COMPLETED",
            "ANSWER_CONTRACT_BUILT",
            "ANSWER_CONTEXT_BUILT",
            "DETERMINISTIC_RESPONSE_BUILT",
            "RESPONSE_SELECTED",
            "ASSURANCE_COMPLETED",
            "FINAL_GOVERNANCE_COMPLETED",
        ],
        "evidence": {
            "evidence_count": 2,
            "retrieval_route": (
                "RETURN_INITIAL"
            ),
            "evidence_sufficient": True,
            "precedence_decision": (
                "SAFE_TO_COMBINE"
            ),
        },
        "governance": {
            "pre_generation_decision": (
                "AUTO_ANSWER"
            ),
            "final_decision": (
                "REVIEW_REQUIRED"
            ),
            "runtime": {
                "source": (
                    "LEGACY_ARGUMENTS"
                ),
                "execution_mode": (
                    "DETERMINISTIC_ONLY"
                ),
            },
        },
        "assurance": {
            "status": "COMPLETED",
            "required_checks_complete": (
                True
            ),
            "final_assurance_decision": (
                "REVIEW_REQUIRED"
            ),
            "authority_increased": False,
        },
        "response": None,
    }


def test_attach_observability_preserves_original_result():
    original = _canonical_result()

    before = deepcopy(
        original
    )

    observed = attach_observability(
        original
    )

    assert original == before

    for key, value in before.items():
        assert (
            observed[
                key
            ]
            == value
        )

    assert (
        "observability"
        in observed
    )


def test_attach_observability_builds_completed_envelope():
    observed = attach_observability(
        _canonical_result()
    )

    envelope = observed[
        "observability"
    ]

    assert (
        envelope[
            "status"
        ]
        == OBSERVABILITY_COMPLETED
    )

    assert (
        envelope[
            "event_count"
        ]
        == len(
            envelope[
                "events"
            ]
        )
    )

    assert (
        envelope[
            "event_count"
        ]
        > 0
    )


def test_observability_does_not_change_final_outcome():
    original = _canonical_result()

    observed = attach_observability(
        original
    )

    assert (
        observed[
            "final_outcome"
        ]
        == original[
            "final_outcome"
        ]
    )

    assert (
        observed[
            "governance"
        ]
        == original[
            "governance"
        ]
    )

    assert (
        observed[
            "assurance"
        ]
        == original[
            "assurance"
        ]
    )


def test_observability_failure_preserves_governed_result():
    original = _canonical_result()

    with patch(
        (
            "src.application."
            "observed_rag_pipeline."
            "build_pipeline_observability"
        ),
        side_effect=RuntimeError(
            "Sensitive diagnostic detail"
        ),
    ):
        observed = attach_observability(
            original
        )

    assert (
        observed[
            "final_outcome"
        ]
        == "REVIEW_REQUIRED"
    )

    assert (
        observed[
            "governance"
        ]
        == original[
            "governance"
        ]
    )

    assert (
        observed[
            "assurance"
        ]
        == original[
            "assurance"
        ]
    )

    envelope = observed[
        "observability"
    ]

    assert (
        envelope[
            "status"
        ]
        == OBSERVABILITY_FAILED
    )

    assert (
        envelope[
            "event_count"
        ]
        == 0
    )

    assert (
        envelope[
            "events"
        ]
        == []
    )

    assert (
        envelope[
            "error_type"
        ]
        == "RuntimeError"
    )

    assert (
        "Sensitive diagnostic detail"
        not in str(
            envelope
        )
    )


def test_run_observed_pipeline_forwards_dependencies():
    expected = _canonical_result()

    with patch(
        (
            "src.application."
            "observed_rag_pipeline."
            "run_rag_pipeline"
        ),
        return_value=expected,
    ) as pipeline:
        observed = (
            run_observed_rag_pipeline(
                question="Test question",
                chunks=[],
                embedded_chunks=[],
                embedding_model=object(),
                embedding_model_name=(
                    "test-model"
                ),
                semantic_k=7,
                keyword_k=8,
                final_k=4,
                rrf_k=50,
                max_related_chunks=3,
                execution_mode=(
                    DETERMINISTIC_ONLY
                ),
                query_date="2026-10-20",
            )
        )

    kwargs = (
        pipeline.call_args.kwargs
    )

    assert (
        kwargs[
            "question"
        ]
        == "Test question"
    )

    assert (
        kwargs[
            "semantic_k"
        ]
        == 7
    )

    assert (
        kwargs[
            "keyword_k"
        ]
        == 8
    )

    assert (
        kwargs[
            "final_k"
        ]
        == 4
    )

    assert (
        kwargs[
            "rrf_k"
        ]
        == 50
    )

    assert (
        kwargs[
            "max_related_chunks"
        ]
        == 3
    )

    assert (
        kwargs[
            "execution_mode"
        ]
        == DETERMINISTIC_ONLY
    )

    assert (
        observed[
            "observability"
        ][
            "status"
        ]
        == OBSERVABILITY_COMPLETED
    )


def test_run_observed_pipeline_does_not_modify_pipeline_result():
    original = _canonical_result()

    before = deepcopy(
        original
    )

    with patch(
        (
            "src.application."
            "observed_rag_pipeline."
            "run_rag_pipeline"
        ),
        return_value=original,
    ):
        run_observed_rag_pipeline(
            question="Test question",
            chunks=[],
            embedded_chunks=[],
            embedding_model=object(),
            embedding_model_name=(
                "test-model"
            ),
        )

    assert original == before


@pytest.mark.parametrize(
    "value",
    [
        None,
        [],
        "invalid",
        1,
        True,
    ],
)
def test_attach_observability_rejects_non_dictionary(
    value,
):
    with pytest.raises(
        ValueError,
        match=(
            "result must be a dictionary"
        ),
    ):
        attach_observability(
            value
        )


def test_observed_failure_result_preserves_abstention():
    result = {
        "request_id": "REQ-FAIL-001",
        "status": "FAILED_CLOSED",
        "final_outcome": "ABSTAIN",
        "execution_trace": [
            "REQUEST_RECEIVED",
        ],
        "failure": {
            "stage": "RETRIEVAL",
            "error_type": (
                "RuntimeError"
            ),
            "message": (
                "Internal sensitive message"
            ),
        },
    }

    observed = attach_observability(
        result
    )

    assert (
        observed[
            "final_outcome"
        ]
        == "ABSTAIN"
    )

    assert (
        observed[
            "status"
        ]
        == "FAILED_CLOSED"
    )

    assert (
        observed[
            "observability"
        ][
            "status"
        ]
        == OBSERVABILITY_COMPLETED
    )

    serialized = str(
        observed[
            "observability"
        ]
    )

    assert (
        "Internal sensitive message"
        not in serialized
    )