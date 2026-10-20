"""Week 27 Day 4 — safe structured JSON logging for governed RAG."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


_FORBIDDEN_KEY_FRAGMENTS = {
    "api_key",
    "apikey",
    "secret",
    "password",
    "token",
    "credential",
    "authorization",
    "bearer",
    "raw_prompt",
    "raw_output",
    "raw_response",
    "evidence_text",
    "patient",
    "question",
    "prompt",
    "answer_text",
    "model_output",
}


_REQUIRED_EVENT_KEYS = {
    "request_id",
    "event_type",
    "stage",
    "status",
    "timestamp",
    "metadata",
}


def _require_non_empty_string(
    value: Any,
    name: str,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or not value.strip()
    ):
        raise ValueError(
            f"{name} must be a non-empty string."
        )

    return value.strip()


def _require_dictionary(
    value: Any,
    name: str,
) -> dict:
    if not isinstance(
        value,
        dict,
    ):
        raise ValueError(
            f"{name} must be a dictionary."
        )

    return value


def _reject_sensitive_keys(
    value: Any,
    *,
    path: str = "record",
) -> None:
    if isinstance(
        value,
        dict,
    ):
        for key, child in value.items():
            if not isinstance(
                key,
                str,
            ):
                raise ValueError(
                    f"{path} keys must be strings."
                )

            normalized = (
                key.lower()
                .replace(
                    "-",
                    "_",
                )
            )

            if any(
                fragment
                in normalized
                for fragment
                in _FORBIDDEN_KEY_FRAGMENTS
            ):
                raise ValueError(
                    "Sensitive logging field "
                    f"is not permitted: {path}.{key}"
                )

            _reject_sensitive_keys(
                child,
                path=f"{path}.{key}",
            )

    elif isinstance(
        value,
        list,
    ):
        for index, child in enumerate(
            value
        ):
            _reject_sensitive_keys(
                child,
                path=f"{path}[{index}]",
            )


def build_correlation_id(
    request_id: str,
) -> str:
    """Build a stable non-reversible correlation identifier."""

    request_id = _require_non_empty_string(
        request_id,
        "request_id",
    )

    digest = hashlib.sha256(
        request_id.encode(
            "utf-8"
        )
    ).hexdigest()

    return (
        "CORR-"
        + digest[
            :20
        ].upper()
    )


def _validate_event(
    event: dict,
) -> dict:
    event = _require_dictionary(
        event,
        "event",
    )

    missing = (
        _REQUIRED_EVENT_KEYS
        - set(
            event.keys()
        )
    )

    if missing:
        raise ValueError(
            "event is missing required fields: "
            + ", ".join(
                sorted(
                    missing
                )
            )
        )

    _require_non_empty_string(
        event.get(
            "request_id"
        ),
        "event.request_id",
    )

    _require_non_empty_string(
        event.get(
            "event_type"
        ),
        "event.event_type",
    )

    _require_non_empty_string(
        event.get(
            "stage"
        ),
        "event.stage",
    )

    _require_non_empty_string(
        event.get(
            "status"
        ),
        "event.status",
    )

    _require_non_empty_string(
        event.get(
            "timestamp"
        ),
        "event.timestamp",
    )

    if not isinstance(
        event.get(
            "metadata"
        ),
        dict,
    ):
        raise ValueError(
            "event.metadata must be a dictionary."
        )

    _reject_sensitive_keys(
        event
    )

    return event


def build_json_log_record(
    event: dict,
) -> dict:
    """Convert one observability event into one safe JSON log record."""

    event = _validate_event(
        event
    )

    request_id = event[
        "request_id"
    ]

    return {
        "correlation_id": (
            build_correlation_id(
                request_id
            )
        ),
        "request_id": request_id,
        "event_type": event[
            "event_type"
        ],
        "stage": event[
            "stage"
        ],
        "status": event[
            "status"
        ],
        "timestamp": event[
            "timestamp"
        ],
        "metadata": dict(
            event[
                "metadata"
            ]
        ),
    }


def build_json_log_records(
    observed_result: dict,
) -> list[dict]:
    """Build safe JSON records from one observed application result."""

    observed_result = (
        _require_dictionary(
            observed_result,
            "observed_result",
        )
    )

    observability = (
        observed_result.get(
            "observability"
        )
    )

    if not isinstance(
        observability,
        dict,
    ):
        raise ValueError(
            "observed_result.observability "
            "must be a dictionary."
        )

    status = observability.get(
        "status"
    )

    if status == "FAILED":
        return []

    if status != "COMPLETED":
        raise ValueError(
            "Unknown observability status."
        )

    events = observability.get(
        "events"
    )

    if not isinstance(
        events,
        list,
    ):
        raise ValueError(
            "observability.events must be a list."
        )

    records = [
        build_json_log_record(
            event
        )
        for event
        in events
    ]

    correlation_ids = {
        record[
            "correlation_id"
        ]
        for record
        in records
    }

    if len(
        correlation_ids
    ) > 1:
        raise ValueError(
            "Observability events contain "
            "multiple request identities."
        )

    return records


def serialize_json_log_record(
    record: dict,
) -> str:
    """Serialize one validated safe log record."""

    record = _require_dictionary(
        record,
        "record",
    )

    _reject_sensitive_keys(
        record
    )

    return json.dumps(
        record,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
    )


def export_jsonl_log_records(
    observed_result: dict,
    path: str | Path,
) -> Path:
    """Write safe observability records to a JSONL file."""

    if not isinstance(
        path,
        (
            str,
            Path,
        ),
    ):
        raise ValueError(
            "path must be a string or Path."
        )

    output_path = Path(
        path
    )

    if (
        output_path.suffix.lower()
        != ".jsonl"
    ):
        raise ValueError(
            "Observability export path "
            "must use .jsonl."
        )

    records = build_json_log_records(
        observed_result
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    serialized = [
        serialize_json_log_record(
            record
        )
        for record
        in records
    ]

    content = (
        "\n".join(
            serialized
        )
    )

    if content:
        content += "\n"

    output_path.write_text(
        content,
        encoding="utf-8",
    )

    return output_path