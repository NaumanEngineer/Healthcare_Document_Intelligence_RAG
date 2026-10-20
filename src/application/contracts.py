"""Application-level contracts for the governed Healthcare RAG pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any


STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED_CLOSED = "FAILED_CLOSED"

OUTCOME_ANSWER = "ANSWER"
OUTCOME_REVIEW_REQUIRED = "REVIEW_REQUIRED"
OUTCOME_ABSTAIN = "ABSTAIN"

VALID_STATUSES = {
    STATUS_COMPLETED,
    STATUS_FAILED_CLOSED,
}

VALID_OUTCOMES = {
    OUTCOME_ANSWER,
    OUTCOME_REVIEW_REQUIRED,
    OUTCOME_ABSTAIN,
}


def _require_non_empty_string(
    value: Any,
    name: str,
) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
    ):
        raise ValueError(
            f"{name} must be a non-empty string."
        )

    return value.strip()


def build_request_id(
    question: str,
) -> str:
    """Build a stable non-sensitive request identifier from the question."""

    question = _require_non_empty_string(
        question,
        "question",
    )

    digest = sha256(
        question.encode("utf-8")
    ).hexdigest()[:16]

    return f"REQ-{digest}"


@dataclass(frozen=True)
class RAGRequest:
    """Canonical application request."""

    question: str

    def __post_init__(self) -> None:
        _require_non_empty_string(
            self.question,
            "question",
        )


@dataclass(frozen=True)
class FailureDetail:
    """Controlled fail-closed failure description."""

    stage: str
    error_type: str
    reason: str

    def __post_init__(self) -> None:
        _require_non_empty_string(
            self.stage,
            "stage",
        )
        _require_non_empty_string(
            self.error_type,
            "error_type",
        )
        _require_non_empty_string(
            self.reason,
            "reason",
        )

    def to_dict(self) -> dict:
        return {
            "stage": self.stage,
            "error_type": self.error_type,
            "reason": self.reason,
        }


@dataclass
class RAGResult:
    """Canonical top-level application result."""

    request_id: str
    question: str
    status: str
    final_outcome: str
    response: dict = field(default_factory=dict)
    governance: dict = field(default_factory=dict)
    assurance: dict = field(default_factory=dict)
    evidence_summary: dict = field(default_factory=dict)
    execution_trace: list = field(default_factory=list)
    failure: FailureDetail | None = None

    def __post_init__(self) -> None:
        _require_non_empty_string(
            self.request_id,
            "request_id",
        )

        _require_non_empty_string(
            self.question,
            "question",
        )

        if self.status not in VALID_STATUSES:
            raise ValueError(
                f"Unsupported status: {self.status}"
            )

        if self.final_outcome not in VALID_OUTCOMES:
            raise ValueError(
                f"Unsupported final_outcome: {self.final_outcome}"
            )

        if not isinstance(self.response, dict):
            raise ValueError(
                "response must be a dictionary."
            )

        if not isinstance(self.governance, dict):
            raise ValueError(
                "governance must be a dictionary."
            )

        if not isinstance(self.assurance, dict):
            raise ValueError(
                "assurance must be a dictionary."
            )

        if not isinstance(self.evidence_summary, dict):
            raise ValueError(
                "evidence_summary must be a dictionary."
            )

        if not isinstance(self.execution_trace, list):
            raise ValueError(
                "execution_trace must be a list."
            )

        if (
            self.status == STATUS_FAILED_CLOSED
            and self.final_outcome != OUTCOME_ABSTAIN
        ):
            raise ValueError(
                "FAILED_CLOSED result must have final_outcome=ABSTAIN."
            )

        if (
            self.status == STATUS_FAILED_CLOSED
            and self.failure is None
        ):
            raise ValueError(
                "FAILED_CLOSED result requires failure details."
            )

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "question": self.question,
            "status": self.status,
            "final_outcome": self.final_outcome,
            "response": dict(self.response),
            "governance": dict(self.governance),
            "assurance": dict(self.assurance),
            "evidence_summary": dict(
                self.evidence_summary
            ),
            "execution_trace": list(
                self.execution_trace
            ),
            "failure": (
                None
                if self.failure is None
                else self.failure.to_dict()
            ),
        }


def build_failed_closed_result(
    *,
    question: str,
    stage: str,
    error: Exception,
    execution_trace: list | None = None,
) -> dict:
    """Build a controlled application-level fail-closed result."""

    question = _require_non_empty_string(
        question,
        "question",
    )

    trace = (
        list(execution_trace)
        if isinstance(execution_trace, list)
        else []
    )

    failure = FailureDetail(
        stage=_require_non_empty_string(
            stage,
            "stage",
        ),
        error_type=type(error).__name__,
        reason=str(error) or "Unknown application error.",
    )

    result = RAGResult(
        request_id=build_request_id(
            question
        ),
        question=question,
        status=STATUS_FAILED_CLOSED,
        final_outcome=OUTCOME_ABSTAIN,
        response={
            "unable_to_answer_safely": (
                "The request could not be completed safely."
            ),
            "reason": (
                "The application encountered an integration failure."
            ),
            "missing_information": (
                "A valid governed execution path was not completed."
            ),
            "what_is_needed_to_continue": (
                "Resolve the reported application failure and retry."
            ),
        },
        governance={
            "final_decision": OUTCOME_ABSTAIN,
            "authority_increased": False,
        },
        assurance={
            "status": "FAILED",
            "fail_closed": True,
        },
        evidence_summary={},
        execution_trace=trace,
        failure=failure,
    )

    return result.to_dict()