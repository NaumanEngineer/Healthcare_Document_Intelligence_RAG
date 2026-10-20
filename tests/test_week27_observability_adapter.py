import json

import pytest

from src.application.observability import (
    EVENT_ASSURANCE,
    EVENT_FAILURE,
    EVENT_FINAL,
    EVENT_REQUEST,
    EVENT_RETRIEVAL,
    STATUS_FAILED,
)
from src.application.observability_adapter import (
    build_pipeline_observability,
)


def _completed_result():
    return {
        "request_id": "REQ-001",
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
            "evidence_count": 3,
            "retrieval_route": (
                "RETURN_INITIAL"
            ),
            "evidence_sufficient": True,
            "precedence_decision": (
                "SAFE_TO_COMBINE"
            ),
            "document_ids": [
                "DOC-001",
            ],
            "raw_evidence_text": (
                "DO NOT LOG THIS"
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
                    "RUNTIME_CONFIG"
                ),
                "execution_mode": (
                    "DETERMINISTIC_ONLY"
                ),
                "metadata": {
                    "environment": (
                        "test"
                    ),
                    "application_name": (
                        "Healthcare RAG"
                    ),
                    "runtime_version": (
                        "week27-day4"
                    ),
                },
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
        "selected_response": {
            "answer": (
                "DO NOT LOG MODEL OR "
                "ANSWER CONTENT"
            ),
        },
    }


def test_completed_pipeline_result_builds_trace():
    events = build_pipeline_observability(
        _completed_result()
    )

    assert len(
        events
    ) == 11

    assert events[
        0
    ][
        "event_type"
    ] == EVENT_REQUEST

    assert events[
        2
    ][
        "event_type"
    ] == EVENT_RETRIEVAL

    assert events[
        9
    ][
        "event_type"
    ] == EVENT_ASSURANCE

    assert events[
        10
    ][
        "event_type"
    ] == EVENT_FINAL


def test_retrieval_event_contains_only_safe_summary():
    events = build_pipeline_observability(
        _completed_result()
    )

    retrieval = next(
        event
        for event
        in events
        if event[
            "stage"
        ]
        == "RETRIEVAL_COMPLETED"
    )

    assert retrieval[
        "metadata"
    ] == {
        "retrieval_route": (
            "RETURN_INITIAL"
        ),
        "evidence_count": 3,
        "evidence_sufficient": True,
        "precedence_decision": (
            "SAFE_TO_COMBINE"
        ),
    }


def test_final_event_contains_governance_outcome():
    events = build_pipeline_observability(
        _completed_result()
    )

    final_event = next(
        event
        for event
        in events
        if event[
            "stage"
        ]
        == "FINAL_GOVERNANCE_COMPLETED"
    )

    metadata = final_event[
        "metadata"
    ]

    assert (
        metadata[
            "final_outcome"
        ]
        == "REVIEW_REQUIRED"
    )

    assert (
        metadata[
            "final_decision"
        ]
        == "REVIEW_REQUIRED"
    )

    assert (
        metadata[
            "authority_increased"
        ]
        if "authority_increased"
        in metadata
        else False
    ) is False


def test_observability_does_not_log_sensitive_content():
    result = _completed_result()

    result[
        "question"
    ] = "Potentially sensitive question"

    result[
        "raw_model_output"
    ] = (
        "DO NOT LOG THIS"
    )

    result[
        "api_key"
    ] = (
        "DO NOT LOG THIS"
    )

    events = build_pipeline_observability(
        result
    )

    serialized = json.dumps(
        events
    ).lower()

    assert (
        "do not log this"
        not in serialized
    )

    assert (
        "potentially sensitive question"
        not in serialized
    )

    assert (
        "api_key"
        not in serialized
    )

    assert (
        "raw_model_output"
        not in serialized
    )


def test_failure_result_creates_failure_event():
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
                "Sensitive internal detail"
            ),
        },
    }

    events = build_pipeline_observability(
        result
    )

    failure_event = events[
        -1
    ]

    assert (
        failure_event[
            "event_type"
        ]
        == EVENT_FAILURE
    )

    assert (
        failure_event[
            "status"
        ]
        == STATUS_FAILED
    )

    assert (
        failure_event[
            "metadata"
        ][
            "failure_stage"
        ]
        == "RETRIEVAL"
    )

    serialized = json.dumps(
        events
    )

    assert (
        "Sensitive internal detail"
        not in serialized
    )


def test_final_outcome_added_when_final_stage_missing():
    result = {
        "request_id": "REQ-002",
        "status": "COMPLETED",
        "final_outcome": "ABSTAIN",
        "execution_trace": [
            "REQUEST_RECEIVED",
            "INPUT_VALIDATED",
        ],
    }

    events = build_pipeline_observability(
        result
    )

    assert (
        events[
            -1
        ][
            "event_type"
        ]
        == EVENT_FINAL
    )

    assert (
        events[
            -1
        ][
            "stage"
        ]
        == "FINAL_OUTCOME"
    )

    assert (
        events[
            -1
        ][
            "metadata"
        ][
            "final_outcome"
        ]
        == "ABSTAIN"
    )


@pytest.mark.parametrize(
    "result",
    [
        None,
        [],
        "invalid",
        1,
        True,
    ],
)
def test_non_dictionary_result_is_rejected(
    result,
):
    with pytest.raises(
        ValueError,
        match=(
            "result must be a dictionary"
        ),
    ):
        build_pipeline_observability(
            result
        )


@pytest.mark.parametrize(
    "request_id",
    [
        None,
        "",
        "   ",
        [],
        {},
        1,
        True,
    ],
)
def test_invalid_request_id_is_rejected(
    request_id,
):
    result = _completed_result()

    result[
        "request_id"
    ] = request_id

    with pytest.raises(
        ValueError,
        match=(
            "result.request_id must be "
            "a non-empty string"
        ),
    ):
        build_pipeline_observability(
            result
        )


def test_missing_execution_trace_is_rejected():
    result = _completed_result()

    result.pop(
        "execution_trace"
    )

    with pytest.raises(
        ValueError,
        match=(
            "result.execution_trace "
            "must be a list"
        ),
    ):
        build_pipeline_observability(
            result
        )


def test_unknown_stage_is_safe_generic_event():
    result = {
        "request_id": "REQ-003",
        "status": "COMPLETED",
        "final_outcome": "ABSTAIN",
        "execution_trace": [
            "REQUEST_RECEIVED",
            "FUTURE_SAFE_STAGE",
        ],
    }

    events = build_pipeline_observability(
        result
    )

    future_event = events[
        1
    ]

    assert (
        future_event[
            "stage"
        ]
        == "FUTURE_SAFE_STAGE"
    )

    assert (
        future_event[
            "metadata"
        ]
        == {}
    )