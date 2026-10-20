"""Week 27 Day 4 — structured observability for governed RAG execution."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


EVENT_REQUEST = "REQUEST"
EVENT_STAGE = "STAGE"
EVENT_RETRIEVAL = "RETRIEVAL"
EVENT_GOVERNANCE = "GOVERNANCE"
EVENT_GENERATION = "GENERATION"
EVENT_ASSURANCE = "ASSURANCE"
EVENT_FINAL = "FINAL"
EVENT_FAILURE = "FAILURE"

VALID_EVENT_TYPES = {
    EVENT_REQUEST,
    EVENT_STAGE,
    EVENT_RETRIEVAL,
    EVENT_GOVERNANCE,
    EVENT_GENERATION,
    EVENT_ASSURANCE,
    EVENT_FINAL,
    EVENT_FAILURE,
}

STATUS_STARTED = "STARTED"
STATUS_COMPLETED = "COMPLETED"
STATUS_SKIPPED = "SKIPPED"
STATUS_FAILED = "FAILED"

VALID_EVENT_STATUSES = {
    STATUS_STARTED,
    STATUS_COMPLETED,
    STATUS_SKIPPED,
    STATUS_FAILED,
}


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


def _validate_event_type(
    value: Any,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or value not in VALID_EVENT_TYPES
    ):
        raise ValueError(
            "event_type must be one of: "
            + ", ".join(
                sorted(
                    VALID_EVENT_TYPES
                )
            )
        )

    return value


def _validate_event_status(
    value: Any,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or value not in VALID_EVENT_STATUSES
    ):
        raise ValueError(
            "status must be one of: "
            + ", ".join(
                sorted(
                    VALID_EVENT_STATUSES
                )
            )
        )

    return value


def _reject_sensitive_payload(
    value: Any,
    *,
    path: str = "metadata",
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
                    "Sensitive observability field "
                    f"is not permitted: {path}.{key}"
                )

            _reject_sensitive_payload(
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
            _reject_sensitive_payload(
                child,
                path=f"{path}[{index}]",
            )


def _utc_timestamp() -> str:
    return datetime.now(
        UTC
    ).isoformat()


@dataclass(
    frozen=True
)
class ObservabilityEvent:
    """One non-sensitive structured application event."""

    request_id: str
    event_type: str
    stage: str
    status: str
    timestamp: str
    metadata: dict

    def __post_init__(
        self,
    ) -> None:
        _require_non_empty_string(
            self.request_id,
            "request_id",
        )

        _validate_event_type(
            self.event_type
        )

        _require_non_empty_string(
            self.stage,
            "stage",
        )

        _validate_event_status(
            self.status
        )

        _require_non_empty_string(
            self.timestamp,
            "timestamp",
        )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise ValueError(
                "metadata must be a dictionary."
            )

        _reject_sensitive_payload(
            self.metadata
        )

    def to_dict(
        self,
    ) -> dict:
        return {
            "request_id": (
                self.request_id
            ),
            "event_type": (
                self.event_type
            ),
            "stage": (
                self.stage
            ),
            "status": (
                self.status
            ),
            "timestamp": (
                self.timestamp
            ),
            "metadata": dict(
                self.metadata
            ),
        }


def build_observability_event(
    *,
    request_id: str,
    event_type: str,
    stage: str,
    status: str,
    metadata: dict | None = None,
) -> ObservabilityEvent:
    """Build one validated structured event."""

    safe_metadata = (
        {}
        if metadata is None
        else metadata
    )

    if not isinstance(
        safe_metadata,
        dict,
    ):
        raise ValueError(
            "metadata must be a dictionary."
        )

    return ObservabilityEvent(
        request_id=request_id,
        event_type=event_type,
        stage=stage,
        status=status,
        timestamp=_utc_timestamp(),
        metadata=dict(
            safe_metadata
        ),
    )


class ObservabilityTrace:
    """In-memory request trace for one governed RAG execution."""

    def __init__(
        self,
        request_id: str,
    ) -> None:
        self.request_id = (
            _require_non_empty_string(
                request_id,
                "request_id",
            )
        )

        self._events: list[
            ObservabilityEvent
        ] = []

    def record(
        self,
        *,
        event_type: str,
        stage: str,
        status: str,
        metadata: dict | None = None,
    ) -> ObservabilityEvent:
        event = build_observability_event(
            request_id=self.request_id,
            event_type=event_type,
            stage=stage,
            status=status,
            metadata=metadata,
        )

        self._events.append(
            event
        )

        return event

    def to_list(
        self,
    ) -> list[dict]:
        return [
            event.to_dict()
            for event
            in self._events
        ]

    def event_count(
        self,
    ) -> int:
        return len(
            self._events
        )