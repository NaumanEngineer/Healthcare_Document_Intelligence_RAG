from unittest.mock import patch

from src.application.contracts import (
    OUTCOME_ABSTAIN,
    OUTCOME_REVIEW_REQUIRED,
    STATUS_COMPLETED,
    STATUS_FAILED_CLOSED,
)
from src.application.rag_pipeline import (
    run_rag_pipeline,
)


class FakeEmbeddingModel:
    pass


def _runtime_dependencies() -> dict:
    return {
        "chunks": [],
        "embedded_chunks": [],
        "embedding_model": FakeEmbeddingModel(),
        "embedding_model_name": "fake-embedding-model",
    }


def _retrieval_output(
    *,
    decision: str,
) -> dict:
    return {
        "results": [],
        "audit": {
            "original_query": "What is the policy?",
            "scope": {
                "allowed": False,
                "scope": "OUT_OF_SCOPE",
                "reason": "Synthetic test.",
                "matching_terms": [],
            },
            "initial_retrieval_call_count": 0,
            "initial_evidence": None,
            "selected_route": "STOP_OUT_OF_SCOPE",
            "routing_decision": None,
            "route_audit": None,
            "final_evidence": None,
            "total_hybrid_retrieval_calls": 0,
            "stop_reason": "ORIGINAL_QUERY_OUT_OF_SCOPE",
        },
        "_test_decision": decision,
    }


def _packet(
    decision: str,
) -> dict:
    return {
        "packet_id": "PKT-TEST",
        "question": "What is the policy?",
        "retrieval": {
            "route": "RETURN_INITIAL",
            "stop_reason": "TEST",
        },
        "evidence_sufficiency": {
            "sufficient": decision != "ABSTAIN",
        },
        "evidence": {
            "supporting": [] if decision == "ABSTAIN" else [{
                "evidence_id": "EVIDENCE::DOC-001-V1.0-P001-C001",
                "document_id": "DOC-001",
                "chunk_id": "DOC-001-V1.0-P001-C001",
                "title": "Operational Policy",
                "document_type": "Operational Policy",
                "source_file": "policy.pdf",
                "version": "1.0",
                "status": "Active",
                "page": 1,
                "evidence_text": "Operational leadership reviews escalation conditions.",
                "evidence_role": "supporting",
            }],
            "relationship_evidence": [],
            "context": [],
        },
        "evidence_count": (
            0
            if decision == "ABSTAIN"
            else 1
        ),
        "document_ids": (
            []
            if decision == "ABSTAIN"
            else ["DOC-001"]
        ),
        "provenance": [],
        "provenance_summary": {},
        "precedence_assessment": {
            "decision": "SAFE_TO_COMBINE",
        },
        "missing_evidence": {
            "initial_missing_topics": [],
            "final_missing_topics": [],
            "unsupported_claims": [],
        },
        "lifecycle_summary": {},
        "governance": {
            "decision": decision,
            "reason": "Synthetic governance decision.",
            "requires_human_review": (
                decision == "REVIEW_REQUIRED"
            ),
            "may_generate_answer": (
                decision == "AUTO_ANSWER"
            ),
            "document_ids": (
                []
                if decision == "ABSTAIN"
                else ["DOC-001"]
            ),
        },
        "audit_summary": {},
    }


def test_invalid_question_fails_closed() -> None:
    result = run_rag_pipeline(
        question="   ",
        **_runtime_dependencies(),
    )

    assert result[
        "status"
    ] == STATUS_FAILED_CLOSED

    assert result[
        "final_outcome"
    ] == OUTCOME_ABSTAIN

    assert result[
        "failure"
    ][
        "stage"
    ] == "INPUT_VALIDATION"


@patch(
    "src.application.rag_pipeline.build_evidence_packet"
)
@patch(
    "src.application.rag_pipeline.orchestrate_retrieval"
)
def test_upstream_auto_answer_stays_at_review_without_required_temporal_inputs(
    mock_retrieval,
    mock_packet,
) -> None:
    mock_retrieval.return_value = (
        _retrieval_output(
            decision="AUTO_ANSWER"
        )
    )

    mock_packet.return_value = _packet(
        "AUTO_ANSWER"
    )

    result = run_rag_pipeline(
        question="What is the policy?",
        **_runtime_dependencies(),
    )

    assert result[
        "status"
    ] == STATUS_COMPLETED

    assert result[
        "final_outcome"
    ] == OUTCOME_REVIEW_REQUIRED

    assert result[
        "governance"
    ][
        "authority_increased"
    ] is False

    assert result["assurance"]["status"] == "COMPLETED"
    assert result["assurance"]["required_checks_complete"] is False
    assert result["assurance"]["temporal_version"]["state"] == "SKIPPED_WITH_REASON"


@patch(
    "src.application.rag_pipeline.build_evidence_packet"
)
@patch(
    "src.application.rag_pipeline.orchestrate_retrieval"
)
def test_review_required_remains_review_required(
    mock_retrieval,
    mock_packet,
) -> None:
    mock_retrieval.return_value = (
        _retrieval_output(
            decision="REVIEW_REQUIRED"
        )
    )

    mock_packet.return_value = _packet(
        "REVIEW_REQUIRED"
    )

    result = run_rag_pipeline(
        question="What is the policy?",
        **_runtime_dependencies(),
    )

    assert result[
        "final_outcome"
    ] == OUTCOME_REVIEW_REQUIRED


@patch(
    "src.application.rag_pipeline.build_evidence_packet"
)
@patch(
    "src.application.rag_pipeline.orchestrate_retrieval"
)
def test_abstain_remains_abstain(
    mock_retrieval,
    mock_packet,
) -> None:
    mock_retrieval.return_value = (
        _retrieval_output(
            decision="ABSTAIN"
        )
    )

    mock_packet.return_value = _packet(
        "ABSTAIN"
    )

    result = run_rag_pipeline(
        question="What is the policy?",
        **_runtime_dependencies(),
    )

    assert result[
        "final_outcome"
    ] == OUTCOME_ABSTAIN


@patch(
    "src.application.rag_pipeline.orchestrate_retrieval"
)
def test_retrieval_exception_fails_closed(
    mock_retrieval,
) -> None:
    mock_retrieval.side_effect = RuntimeError(
        "synthetic retrieval failure"
    )

    result = run_rag_pipeline(
        question="What is the policy?",
        **_runtime_dependencies(),
    )

    assert result[
        "status"
    ] == STATUS_FAILED_CLOSED

    assert result[
        "final_outcome"
    ] == OUTCOME_ABSTAIN

    assert result[
        "failure"
    ][
        "stage"
    ] == "RETRIEVAL"


@patch(
    "src.application.rag_pipeline.build_evidence_packet"
)
@patch(
    "src.application.rag_pipeline.orchestrate_retrieval"
)
def test_packet_exception_fails_closed(
    mock_retrieval,
    mock_packet,
) -> None:
    mock_retrieval.return_value = (
        _retrieval_output(
            decision="AUTO_ANSWER"
        )
    )

    mock_packet.side_effect = RuntimeError(
        "synthetic packet failure"
    )

    result = run_rag_pipeline(
        question="What is the policy?",
        **_runtime_dependencies(),
    )

    assert result[
        "status"
    ] == STATUS_FAILED_CLOSED

    assert result[
        "final_outcome"
    ] == OUTCOME_ABSTAIN

    assert result[
        "failure"
    ][
        "stage"
    ] == "EVIDENCE_PACKET"
