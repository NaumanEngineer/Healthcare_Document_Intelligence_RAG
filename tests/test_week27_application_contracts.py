import pytest

from src.application.contracts import (
    OUTCOME_ABSTAIN,
    OUTCOME_ANSWER,
    RAGRequest,
    RAGResult,
    STATUS_COMPLETED,
    STATUS_FAILED_CLOSED,
    build_failed_closed_result,
    build_request_id,
)


def test_request_rejects_blank_question() -> None:
    with pytest.raises(
        ValueError,
        match="question must be a non-empty string",
    ):
        RAGRequest(
            question="   "
        )


def test_request_id_is_stable() -> None:
    first = build_request_id(
        "What should operational leadership do?"
    )

    second = build_request_id(
        "What should operational leadership do?"
    )

    assert first == second
    assert first.startswith("REQ-")


def test_completed_answer_result_is_valid() -> None:
    result = RAGResult(
        request_id="REQ-123",
        question="What is the policy?",
        status=STATUS_COMPLETED,
        final_outcome=OUTCOME_ANSWER,
    )

    assert result.to_dict()[
        "final_outcome"
    ] == OUTCOME_ANSWER


def test_failed_closed_requires_abstain() -> None:
    with pytest.raises(
        ValueError,
        match="FAILED_CLOSED result must have final_outcome=ABSTAIN",
    ):
        RAGResult(
            request_id="REQ-123",
            question="What is the policy?",
            status=STATUS_FAILED_CLOSED,
            final_outcome=OUTCOME_ANSWER,
            failure=None,
        )


def test_failed_closed_builder_returns_safe_abstention() -> None:
    try:
        raise RuntimeError(
            "simulated failure"
        )
    except RuntimeError as exc:
        result = build_failed_closed_result(
            question="What is the policy?",
            stage="INPUT_VALIDATION",
            error=exc,
            execution_trace=[
                "REQUEST_RECEIVED",
            ],
        )

    assert result[
        "status"
    ] == STATUS_FAILED_CLOSED

    assert result[
        "final_outcome"
    ] == OUTCOME_ABSTAIN

    assert result[
        "assurance"
    ][
        "fail_closed"
    ] is True

    assert result[
        "governance"
    ][
        "authority_increased"
    ] is False

    assert result[
        "failure"
    ][
        "stage"
    ] == "INPUT_VALIDATION"