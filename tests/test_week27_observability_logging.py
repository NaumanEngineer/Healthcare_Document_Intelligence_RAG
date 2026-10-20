import json

import pytest

from src.application.observability_logging import (
    build_correlation_id,
    build_json_log_record,
    build_json_log_records,
    export_jsonl_log_records,
    serialize_json_log_record,
)


def _event(
    *,
    request_id="REQ-001",
    stage="RETRIEVAL_COMPLETED",
):
    return {
        "request_id": request_id,
        "event_type": "RETRIEVAL",
        "stage": stage,
        "status": "COMPLETED",
        "timestamp": (
            "2026-10-20T08:00:00+00:00"
        ),
        "metadata": {
            "retrieval_route": (
                "RETURN_INITIAL"
            ),
            "evidence_count": 3,
        },
    }


def _observed_result():
    return {
        "request_id": "REQ-001",
        "final_outcome": (
            "REVIEW_REQUIRED"
        ),
        "observability": {
            "status": "COMPLETED",
            "event_count": 2,
            "events": [
                {
                    "request_id": (
                        "REQ-001"
                    ),
                    "event_type": (
                        "REQUEST"
                    ),
                    "stage": (
                        "REQUEST_RECEIVED"
                    ),
                    "status": (
                        "STARTED"
                    ),
                    "timestamp": (
                        "2026-10-20T08:00:00"
                        "+00:00"
                    ),
                    "metadata": {
                        "execution_mode": (
                            "DETERMINISTIC_ONLY"
                        ),
                    },
                },
                _event(),
            ],
        },
    }


def test_correlation_id_is_stable():
    first = build_correlation_id(
        "REQ-001"
    )

    second = build_correlation_id(
        "REQ-001"
    )

    assert first == second

    assert first.startswith(
        "CORR-"
    )

    assert len(
        first
    ) == 25


def test_different_requests_get_different_correlation_ids():
    first = build_correlation_id(
        "REQ-001"
    )

    second = build_correlation_id(
        "REQ-002"
    )

    assert first != second


@pytest.mark.parametrize(
    "request_id",
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
def test_invalid_request_id_is_rejected(
    request_id,
):
    with pytest.raises(
        ValueError,
        match=(
            "request_id must be "
            "a non-empty string"
        ),
    ):
        build_correlation_id(
            request_id
        )


def test_json_log_record_contains_correlation_id():
    record = build_json_log_record(
        _event()
    )

    assert (
        record[
            "request_id"
        ]
        == "REQ-001"
    )

    assert (
        record[
            "correlation_id"
        ]
        == build_correlation_id(
            "REQ-001"
        )
    )

    assert (
        record[
            "stage"
        ]
        == "RETRIEVAL_COMPLETED"
    )


def test_all_events_share_same_correlation_id():
    records = build_json_log_records(
        _observed_result()
    )

    correlation_ids = {
        record[
            "correlation_id"
        ]
        for record
        in records
    }

    assert len(
        correlation_ids
    ) == 1


def test_logging_does_not_include_application_payload():
    observed = _observed_result()

    observed[
        "question"
    ] = (
        "Potentially sensitive question"
    )

    observed[
        "raw_model_output"
    ] = (
        "DO NOT LOG MODEL OUTPUT"
    )

    observed[
        "evidence"
    ] = {
        "evidence_text": (
            "DO NOT LOG EVIDENCE"
        ),
    }

    records = build_json_log_records(
        observed
    )

    serialized = json.dumps(
        records
    ).lower()

    assert (
        "potentially sensitive question"
        not in serialized
    )

    assert (
        "do not log model output"
        not in serialized
    )

    assert (
        "do not log evidence"
        not in serialized
    )


@pytest.mark.parametrize(
    "metadata",
    [
        {
            "api_key": "secret",
        },
        {
            "access_token": "secret",
        },
        {
            "password": "secret",
        },
        {
            "raw_prompt": "secret",
        },
        {
            "raw_output": "secret",
        },
        {
            "evidence_text": "secret",
        },
        {
            "patient_record": {
                "id": "123",
            },
        },
        {
            "nested": {
                "client_secret": (
                    "secret"
                ),
            },
        },
    ],
)
def test_sensitive_event_fields_are_rejected(
    metadata,
):
    event = _event()

    event[
        "metadata"
    ] = metadata

    with pytest.raises(
        ValueError,
        match=(
            "Sensitive logging field"
        ),
    ):
        build_json_log_record(
            event
        )


def test_failed_observability_returns_no_records():
    observed = {
        "request_id": "REQ-001",
        "observability": {
            "status": "FAILED",
            "event_count": 0,
            "events": [],
            "error_type": (
                "RuntimeError"
            ),
        },
    }

    records = build_json_log_records(
        observed
    )

    assert records == []


def test_unknown_observability_status_is_rejected():
    observed = {
        "request_id": "REQ-001",
        "observability": {
            "status": "UNKNOWN",
            "events": [],
        },
    }

    with pytest.raises(
        ValueError,
        match=(
            "Unknown observability status"
        ),
    ):
        build_json_log_records(
            observed
        )


def test_multiple_request_ids_are_rejected():
    observed = _observed_result()

    observed[
        "observability"
    ][
        "events"
    ][
        1
    ][
        "request_id"
    ] = "REQ-002"

    with pytest.raises(
        ValueError,
        match=(
            "multiple request identities"
        ),
    ):
        build_json_log_records(
            observed
        )


def test_serialization_is_valid_json():
    record = build_json_log_record(
        _event()
    )

    serialized = (
        serialize_json_log_record(
            record
        )
    )

    loaded = json.loads(
        serialized
    )

    assert loaded == record


def test_jsonl_export_round_trip(
    tmp_path,
):
    output_path = (
        tmp_path
        / "observability.jsonl"
    )

    returned = (
        export_jsonl_log_records(
            _observed_result(),
            output_path,
        )
    )

    assert returned == output_path

    lines = (
        output_path.read_text(
            encoding="utf-8"
        )
        .splitlines()
    )

    assert len(
        lines
    ) == 2

    records = [
        json.loads(
            line
        )
        for line
        in lines
    ]

    assert (
        records[
            0
        ][
            "correlation_id"
        ]
        == records[
            1
        ][
            "correlation_id"
        ]
    )


def test_export_creates_parent_directory(
    tmp_path,
):
    output_path = (
        tmp_path
        / "logs"
        / "rag"
        / "observability.jsonl"
    )

    export_jsonl_log_records(
        _observed_result(),
        output_path,
    )

    assert (
        output_path.exists()
    )


def test_non_jsonl_export_is_rejected(
    tmp_path,
):
    output_path = (
        tmp_path
        / "observability.json"
    )

    with pytest.raises(
        ValueError,
        match=(
            "must use .jsonl"
        ),
    ):
        export_jsonl_log_records(
            _observed_result(),
            output_path,
        )