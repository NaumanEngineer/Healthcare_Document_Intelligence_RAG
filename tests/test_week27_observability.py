import pytest

from src.application.observability import (
    EVENT_ASSURANCE,
    EVENT_FAILURE,
    EVENT_FINAL,
    EVENT_GENERATION,
    EVENT_GOVERNANCE,
    EVENT_REQUEST,
    EVENT_RETRIEVAL,
    EVENT_STAGE,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_SKIPPED,
    STATUS_STARTED,
    ObservabilityEvent,
    ObservabilityTrace,
    build_observability_event,
)


def test_build_observability_event():
    event = build_observability_event(
        request_id="REQ-001",
        event_type=EVENT_REQUEST,
        stage="REQUEST_RECEIVED",
        status=STATUS_STARTED,
        metadata={
            "execution_mode": (
                "DETERMINISTIC_ONLY"
            ),
        },
    )

    payload = event.to_dict()

    assert payload[
        "request_id"
    ] == "REQ-001"

    assert payload[
        "event_type"
    ] == EVENT_REQUEST

    assert payload[
        "stage"
    ] == "REQUEST_RECEIVED"

    assert payload[
        "status"
    ] == STATUS_STARTED

    assert isinstance(
        payload[
            "timestamp"
        ],
        str,
    )

    assert payload[
        "metadata"
    ][
        "execution_mode"
    ] == "DETERMINISTIC_ONLY"


@pytest.mark.parametrize(
    "event_type",
    [
        EVENT_REQUEST,
        EVENT_STAGE,
        EVENT_RETRIEVAL,
        EVENT_GOVERNANCE,
        EVENT_GENERATION,
        EVENT_ASSURANCE,
        EVENT_FINAL,
        EVENT_FAILURE,
    ],
)
def test_all_supported_event_types_are_valid(
    event_type,
):
    event = build_observability_event(
        request_id="REQ-001",
        event_type=event_type,
        stage="TEST_STAGE",
        status=STATUS_COMPLETED,
    )

    assert (
        event.event_type
        == event_type
    )


@pytest.mark.parametrize(
    "status",
    [
        STATUS_STARTED,
        STATUS_COMPLETED,
        STATUS_SKIPPED,
        STATUS_FAILED,
    ],
)
def test_all_supported_statuses_are_valid(
    status,
):
    event = build_observability_event(
        request_id="REQ-001",
        event_type=EVENT_STAGE,
        stage="TEST_STAGE",
        status=status,
    )

    assert (
        event.status
        == status
    )


@pytest.mark.parametrize(
    "value",
    [
        "",
        "UNKNOWN",
        None,
        [],
        {},
        True,
        1,
    ],
)
def test_invalid_event_type_is_rejected(
    value,
):
    with pytest.raises(
        ValueError,
        match="event_type must be one of",
    ):
        build_observability_event(
            request_id="REQ-001",
            event_type=value,
            stage="TEST_STAGE",
            status=STATUS_COMPLETED,
        )


@pytest.mark.parametrize(
    "value",
    [
        "",
        "UNKNOWN",
        None,
        [],
        {},
        True,
        1,
    ],
)
def test_invalid_status_is_rejected(
    value,
):
    with pytest.raises(
        ValueError,
        match="status must be one of",
    ):
        build_observability_event(
            request_id="REQ-001",
            event_type=EVENT_STAGE,
            stage="TEST_STAGE",
            status=value,
        )


@pytest.mark.parametrize(
    "metadata",
    [
        {
            "api_key": "secret",
        },
        {
            "password": "secret",
        },
        {
            "access_token": "secret",
        },
        {
            "authorization_header": (
                "Bearer secret"
            ),
        },
        {
            "raw_prompt": "hidden prompt",
        },
        {
            "raw_output": "hidden output",
        },
        {
            "evidence_text": (
                "raw source text"
            ),
        },
        {
            "nested": {
                "client_secret": (
                    "secret"
                ),
            },
        },
        {
            "patient_record": {
                "name": "Example",
            },
        },
    ],
)
def test_sensitive_metadata_keys_are_rejected(
    metadata,
):
    with pytest.raises(
        ValueError,
        match=(
            "Sensitive observability field"
        ),
    ):
        build_observability_event(
            request_id="REQ-001",
            event_type=EVENT_STAGE,
            stage="TEST_STAGE",
            status=STATUS_COMPLETED,
            metadata=metadata,
        )


def test_safe_metadata_is_allowed():
    event = build_observability_event(
        request_id="REQ-001",
        event_type=EVENT_RETRIEVAL,
        stage="RETRIEVAL_COMPLETED",
        status=STATUS_COMPLETED,
        metadata={
            "retrieval_route": (
                "RETURN_INITIAL"
            ),
            "result_count": 3,
            "evidence_sufficient": True,
        },
    )

    assert (
        event.metadata[
            "result_count"
        ]
        == 3
    )


def test_trace_records_events_in_order():
    trace = ObservabilityTrace(
        "REQ-001"
    )

    trace.record(
        event_type=EVENT_REQUEST,
        stage="REQUEST_RECEIVED",
        status=STATUS_STARTED,
    )

    trace.record(
        event_type=EVENT_RETRIEVAL,
        stage="RETRIEVAL_COMPLETED",
        status=STATUS_COMPLETED,
        metadata={
            "result_count": 3,
        },
    )

    events = trace.to_list()

    assert len(
        events
    ) == 2

    assert events[
        0
    ][
        "stage"
    ] == "REQUEST_RECEIVED"

    assert events[
        1
    ][
        "stage"
    ] == "RETRIEVAL_COMPLETED"


def test_trace_event_count():
    trace = ObservabilityTrace(
        "REQ-001"
    )

    assert (
        trace.event_count()
        == 0
    )

    trace.record(
        event_type=EVENT_STAGE,
        stage="INPUT_VALIDATED",
        status=STATUS_COMPLETED,
    )

    assert (
        trace.event_count()
        == 1
    )


def test_trace_returns_new_list():
    trace = ObservabilityTrace(
        "REQ-001"
    )

    trace.record(
        event_type=EVENT_FINAL,
        stage="FINAL_GOVERNANCE_COMPLETED",
        status=STATUS_COMPLETED,
        metadata={
            "final_outcome": (
                "REVIEW_REQUIRED"
            ),
        },
    )

    first = trace.to_list()
    second = trace.to_list()

    assert (
        first
        == second
    )

    assert (
        first
        is not second
    )


def test_direct_event_rejects_non_dictionary_metadata():
    with pytest.raises(
        ValueError,
        match="metadata must be a dictionary",
    ):
        ObservabilityEvent(
            request_id="REQ-001",
            event_type=EVENT_STAGE,
            stage="TEST_STAGE",
            status=STATUS_COMPLETED,
            timestamp=(
                "2026-10-20T08:00:00+00:00"
            ),
            metadata=[],
        )