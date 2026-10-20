"""Week 27 Day 6 — real end-to-end governed RAG regression.

These tests exercise the synthetic Week 27 demo through the real application
boundary rather than mocking retrieval, evidence construction, governance,
generation, assurance, or observability.

The demo corpus is synthetic and contains no patient data.
"""

from __future__ import annotations

from src.application.app import (
    EXIT_SUCCESS,
)
from src.application.week27_demo_data import (
    DEMO_DOCUMENT_ID,
    DEMO_QUESTION,
)
from src.application.week27_demo_runner import (
    run_week27_demo,
)
from src.ingestion.document_metadata import (
    DOCUMENT_REGISTER,
)


EXPECTED_EXECUTION_TRACE = [
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
]


def _run_real_demo() -> dict:
    exit_code, result, _ = (
        run_week27_demo()
    )

    assert (
        exit_code
        == EXIT_SUCCESS
    )

    assert isinstance(
        result,
        dict,
    )

    return result


def test_real_demo_completes_successfully():
    result = _run_real_demo()

    assert (
        result[
            "status"
        ]
        == "COMPLETED"
    )

    assert (
        result[
            "final_outcome"
        ]
        == "ANSWER"
    )

    assert (
        result[
            "failure"
        ]
        is None
    )


def test_real_demo_executes_complete_canonical_trace():
    result = _run_real_demo()

    assert (
        result[
            "execution_trace"
        ]
        == EXPECTED_EXECUTION_TRACE
    )


def test_real_demo_reaches_assurance_and_final_governance():
    result = _run_real_demo()

    trace = (
        result[
            "execution_trace"
        ]
    )

    assert (
        "ASSURANCE_COMPLETED"
        in trace
    )

    assert (
        "FINAL_GOVERNANCE_COMPLETED"
        in trace
    )

    assert (
        trace.index(
            "ASSURANCE_COMPLETED"
        )
        <
        trace.index(
            "FINAL_GOVERNANCE_COMPLETED"
        )
    )


def test_real_demo_never_increases_authority():
    result = _run_real_demo()

    governance = (
        result[
            "governance"
        ]
    )

    assert (
        governance[
            "application_release_ceiling"
        ]
        == "ANSWER"
    )

    assert (
        governance[
            "authority_increased"
        ]
        is False
    )


def test_real_demo_observability_completes():
    result = _run_real_demo()

    observability = (
        result[
            "observability"
        ]
    )

    assert (
        observability[
            "status"
        ]
        == "COMPLETED"
    )

    assert (
        observability[
            "event_count"
        ]
        > 0
    )


def test_real_demo_observability_covers_full_execution():
    result = _run_real_demo()

    observability = (
        result[
            "observability"
        ]
    )

    assert (
        observability[
            "event_count"
        ]
        == 11
    )


def test_real_demo_question_identity_is_preserved():
    result = _run_real_demo()

    assert (
        result[
            "question"
        ]
        == DEMO_QUESTION
    )


def test_demo_registration_is_removed_after_successful_run():
    assert (
        DEMO_DOCUMENT_ID
        not in DOCUMENT_REGISTER
    )

    _run_real_demo()

    assert (
        DEMO_DOCUMENT_ID
        not in DOCUMENT_REGISTER
    )


def test_demo_registration_is_not_persistent_between_runs():
    first = _run_real_demo()

    assert (
        DEMO_DOCUMENT_ID
        not in DOCUMENT_REGISTER
    )

    second = _run_real_demo()

    assert (
        DEMO_DOCUMENT_ID
        not in DOCUMENT_REGISTER
    )

    assert (
        first[
            "final_outcome"
        ]
        == second[
            "final_outcome"
        ]
        == "ANSWER"
    )


def test_real_demo_is_reproducible():
    first = _run_real_demo()
    second = _run_real_demo()

    assert (
        first[
            "status"
        ]
        == second[
            "status"
        ]
        == "COMPLETED"
    )

    assert (
        first[
            "final_outcome"
        ]
        == second[
            "final_outcome"
        ]
        == "ANSWER"
    )

    assert (
        first[
            "execution_trace"
        ]
        == second[
            "execution_trace"
        ]
        == EXPECTED_EXECUTION_TRACE
    )

    assert (
        first[
            "governance"
        ][
            "authority_increased"
        ]
        is False
    )

    assert (
        second[
            "governance"
        ][
            "authority_increased"
        ]
        is False
    )