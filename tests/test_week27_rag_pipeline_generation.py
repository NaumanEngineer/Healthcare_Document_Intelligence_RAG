"""Session 5 generation composition with local providers and real Week 24 functions."""

from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from src.application import rag_pipeline as app
from src.generation.generation_fallback import resolve_generation_with_fallback
from src.generation.grounded_answer import build_grounded_response
from src.generation.mock_model_provider import (
    DeterministicMockProvider, ErrorMockProvider, FreeTextMockProvider,
)
from src.generation.model_execution import execute_governed_model


QUESTION = "What is the operational escalation policy?"
PACKET_ID = "EVIDENCE_PACKET::GENERATION_TEST"
PRIVATE_TEXT = "CANDIDATE_CONTENT_WITHHELD_UNTIL_ASSURANCE"


def _packet(decision="AUTO_ANSWER"):
    return {
        "packet_id": PACKET_ID,
        "question": QUESTION,
        "governance": {
            "decision": decision,
            "reason": "Existing governed assessment.",
            "may_generate_answer": decision == "AUTO_ANSWER",
            "requires_human_review": decision == "REVIEW_REQUIRED",
            "document_ids": ["DOC-001"],
        },
        "precedence_assessment": {"decision": "SAFE_TO_COMBINE"},
        "evidence": {
            "supporting": [] if decision == "ABSTAIN" else [{
                "evidence_id": "EVIDENCE::DOC-001-V1.0-P001-C001",
                "document_id": "DOC-001",
                "chunk_id": "DOC-001-V1.0-P001-C001",
                "title": "Operational Policy", "document_type": "Policy",
                "source_file": "policy.pdf", "version": "1.0",
                "status": "Active", "page": 1,
                "evidence_text": PRIVATE_TEXT, "evidence_role": "supporting",
            }],
            "relationship_evidence": [], "context": [],
        },
        "evidence_count": 0 if decision == "ABSTAIN" else 1,
        "document_ids": ["DOC-001"],
        "retrieval": {"route": "RETURN_INITIAL", "stop_reason": "TEST"},
        "evidence_sufficiency": {"sufficient": decision != "ABSTAIN"},
        "missing_evidence": {
            "initial_missing_topics": [], "final_missing_topics": [],
            "unsupported_claims": [],
        },
    }


def _model_output(decision="AUTO_ANSWER"):
    review = decision == "REVIEW_REQUIRED"
    return {
        "packet_id": PACKET_ID,
        "governance_decision": decision,
        "response_type": "REVIEW" if review else "ANSWER",
        "requires_human_review": review,
        "model_generation_status": "MODEL_REVIEW_SUMMARY" if review else "MODEL_GENERATED",
        "sections": {"evidence_summary" if review else "management_summary": PRIVATE_TEXT},
        "citations_used": ["E1"],
        "model_safety_notes": [],
        "extra_raw_field": "RAW_PROVIDER_FIELD_MUST_NOT_ESCAPE",
    }


@pytest.fixture
def boundary():
    records = {}

    def build(contract, context):
        records["deterministic"] = build_grounded_response(contract, context)
        return records["deterministic"]

    def resolve(execution, deterministic):
        records["resolution"] = resolve_generation_with_fallback(execution, deterministic)
        return records["resolution"]

    with (
        patch.object(app, "orchestrate_retrieval", return_value={}) as retrieval,
        patch.object(app, "build_evidence_packet", return_value=_packet()) as packet,
        patch.object(app, "build_grounded_response", side_effect=build) as deterministic,
        patch.object(app, "execute_governed_model", wraps=execute_governed_model) as execution,
        patch.object(app, "resolve_generation_with_fallback", side_effect=resolve) as fallback,
        patch.object(app, "_summarize_selected_response", wraps=app._summarize_selected_response) as selected,
    ):
        yield SimpleNamespace(
            records=records, retrieval=retrieval, packet=packet,
            deterministic=deterministic, execution=execution,
            fallback=fallback, selected=selected,
        )


def _run(boundary, **kwargs):
    return app.run_rag_pipeline(
        question=QUESTION, chunks=[], embedded_chunks=[],
        embedding_model=object(), embedding_model_name="fake-embedding-model",
        **kwargs,
    )


def _assert_ceiling(result, decision="AUTO_ANSWER"):
    assert result["status"] == "COMPLETED"
    expected = "ABSTAIN" if decision == "ABSTAIN" else "REVIEW_REQUIRED"
    assert result["final_outcome"] == expected
    assert result["governance"]["application_release_ceiling"] == expected
    assert result["governance"]["authority_increased"] is False
    assert result["governance"]["generation"]["selected_response"]["governance_decision"] == decision
    assert result["assurance"]["status"] == "COMPLETED"
    assert result["governance"]["generation"]["selected_response_released"] is (decision == "ABSTAIN")
    assert PRIVATE_TEXT not in str(result)
    assert "RAW_PROVIDER_FIELD_MUST_NOT_ESCAPE" not in str(result)
    assert "raw_output" not in str(result)
    assert result["execution_trace"][-3:] == [
        "RESPONSE_SELECTED", "ASSURANCE_COMPLETED", "FINAL_GOVERNANCE_COMPLETED",
    ]


def test_default_mode_selects_actual_deterministic_response_without_provider(boundary):
    provider = Mock()
    result = _run(boundary, model_provider=provider)
    _assert_ceiling(result)
    boundary.execution.assert_not_called()
    boundary.fallback.assert_not_called()
    provider.generate.assert_not_called()
    boundary.deterministic.assert_called_once()
    assert boundary.selected.call_args.args[0] is boundary.records["deterministic"]
    generation = result["governance"]["generation"]
    assert generation["execution_mode"] == "DETERMINISTIC_ONLY"
    assert generation["final_response_source"] == "DETERMINISTIC_ONLY"
    assert generation["fallback_used"] is False
    assert generation["provider_execution"] == "SKIPPED_WITH_REASON"
    assert generation["provider_skip_reason"]
    assert generation["model_execution_status"] is None
    assert generation["provider_name"] is None
    assert generation["model_name"] is None


@pytest.mark.parametrize("decision", ["AUTO_ANSWER", "REVIEW_REQUIRED"])
def test_provider_acceptance_selects_only_validated_model_response(boundary, decision):
    boundary.packet.return_value = _packet(decision)
    provider = DeterministicMockProvider(_model_output(decision))
    result = _run(boundary, execution_mode="CONTROLLED_PROVIDER", model_provider=provider)
    _assert_ceiling(result, decision)
    boundary.execution.assert_called_once()
    boundary.fallback.assert_called_once()
    context, passed_provider = boundary.execution.call_args.args
    assert passed_provider is provider
    assert context["governance_decision"] == decision
    execution, deterministic = boundary.fallback.call_args.args
    assert deterministic is boundary.records["deterministic"]
    assert execution["execution_status"] == "ACCEPTED"
    candidate = boundary.selected.call_args.args[0]
    assert candidate is boundary.records["resolution"]["final_response"]
    assert candidate == execution["validated_output"]
    assert "extra_raw_field" not in candidate
    assert "generation_status" not in candidate  # no merged deterministic sections
    assert candidate["sections"] == _model_output(decision)["sections"]
    generation = result["governance"]["generation"]
    assert generation["final_response_source"] == "MODEL"
    assert generation["model_execution_status"] == "ACCEPTED"
    assert generation["fallback_used"] is False
    assert generation["provider_name"] == provider.provider_name
    assert generation["model_name"] == provider.model_name
    assert generation["failure_type"] is None
    trace = result["execution_trace"]
    assert trace.index("DETERMINISTIC_RESPONSE_BUILT") < trace.index("MODEL_EXECUTION_COMPLETED")
    assert trace.index("MODEL_EXECUTION_COMPLETED") < trace.index("RESPONSE_SELECTED")


@pytest.mark.parametrize("provider,status,failure_type", [
    (ErrorMockProvider("Local provider unavailable"), "FAILED", "PROVIDER_ERROR"),
    (FreeTextMockProvider("REJECTED_RAW_TEXT"), "REJECTED", "PARSE_ERROR"),
    (DeterministicMockProvider({"packet_id": "WRONG"}), "REJECTED", "VALIDATION_ERROR"),
])
def test_failed_or_rejected_execution_selects_real_fallback(boundary, provider, status, failure_type):
    result = _run(boundary, execution_mode="CONTROLLED_PROVIDER", model_provider=provider)
    _assert_ceiling(result)
    execution, deterministic = boundary.fallback.call_args.args
    assert execution["execution_status"] == status
    candidate = boundary.selected.call_args.args[0]
    assert candidate is boundary.records["resolution"]["final_response"]
    assert candidate == deterministic == boundary.records["deterministic"]
    assert "model_generation_status" not in candidate
    generation = result["governance"]["generation"]
    assert generation["final_response_source"] == "DETERMINISTIC_FALLBACK"
    assert generation["fallback_used"] is True
    assert generation["model_execution_status"] == status
    assert generation["failure_type"] == failure_type
    assert generation["failure_reason"] == execution["failure_reason"]
    assert generation["fallback_reason"] == execution["failure_reason"]
    assert generation["provider_name"] == provider.provider_name
    assert generation["model_name"] == provider.model_name
    assert "REJECTED_RAW_TEXT" not in str(result)


@pytest.mark.parametrize("decision", ["AUTO_ANSWER", "REVIEW_REQUIRED"])
def test_unknown_citation_or_authority_upgrade_uses_existing_validator_and_fallback(boundary, decision):
    boundary.packet.return_value = _packet(decision)
    output = _model_output(decision)
    if decision == "AUTO_ANSWER":
        output["citations_used"] = ["E999"]
    else:
        output["sections"]["approved_action"] = "UNAPPROVED_ACTION"
    result = _run(
        boundary, execution_mode="CONTROLLED_PROVIDER",
        model_provider=DeterministicMockProvider(output),
    )
    _assert_ceiling(result, decision)
    assert result["governance"]["generation"]["model_execution_status"] == "REJECTED"
    assert boundary.selected.call_args.args[0] == boundary.records["deterministic"]
    assert "UNAPPROVED_ACTION" not in str(result)


@pytest.mark.parametrize("mode", ["UNKNOWN", "", None, [], {}, True, 1])
def test_invalid_mode_fails_closed_before_retrieval_or_generation(boundary, mode):
    result = _run(boundary, execution_mode=mode)
    assert result["status"] == "FAILED_CLOSED"
    assert result["final_outcome"] == "ABSTAIN"
    assert result["failure"]["stage"] == "INPUT_VALIDATION"
    boundary.retrieval.assert_not_called()
    boundary.deterministic.assert_not_called()
    boundary.execution.assert_not_called()


def test_provider_mode_requires_provider(boundary):
    result = _run(boundary, execution_mode="CONTROLLED_PROVIDER")
    assert result["status"] == "FAILED_CLOSED"
    assert result["final_outcome"] == "ABSTAIN"
    assert "model_provider is required" in result["failure"]["reason"]
    boundary.retrieval.assert_not_called()
    boundary.execution.assert_not_called()


@pytest.mark.parametrize("mode", ["DETERMINISTIC_ONLY", "CONTROLLED_PROVIDER"])
def test_abstention_stays_deterministic_without_evidence_or_citations(boundary, mode):
    boundary.packet.return_value = _packet("ABSTAIN")
    provider = Mock()
    result = _run(boundary, execution_mode=mode, model_provider=provider)
    _assert_ceiling(result, "ABSTAIN")
    boundary.execution.assert_not_called()
    boundary.fallback.assert_not_called()
    provider.generate.assert_not_called()
    candidate, context = boundary.selected.call_args.args
    assert candidate is boundary.records["deterministic"]
    assert candidate["response_type"] == "ABSTENTION"
    assert candidate["citations_used"] == []
    assert context["evidence_context"] == []
    assert context["citation_index"] == []
    assert "evidence_based_explanation" not in candidate["sections"]
    assert "sources" not in candidate["sections"]


@pytest.mark.parametrize("mode", ["DETERMINISTIC_ONLY", "CONTROLLED_PROVIDER"])
def test_review_and_blocked_combination_never_gain_authority(boundary, mode):
    packet = _packet()
    packet["precedence_assessment"]["decision"] = "BLOCK_COMBINATION"
    original = deepcopy(packet)
    boundary.packet.return_value = packet
    result = _run(
        boundary, execution_mode=mode,
        model_provider=DeterministicMockProvider(_model_output("REVIEW_REQUIRED")),
    )
    _assert_ceiling(result, "REVIEW_REQUIRED")
    candidate = boundary.selected.call_args.args[0]
    assert candidate["response_type"] == "REVIEW"
    assert candidate["requires_human_review"] is True
    assert packet == original


@pytest.mark.parametrize("mock_name,stage", [
    ("deterministic", "DETERMINISTIC_RESPONSE"),
    ("execution", "MODEL_EXECUTION"),
    ("fallback", "FALLBACK_RESOLUTION"),
])
def test_integration_exceptions_fail_closed(boundary, mock_name, stage):
    getattr(boundary, mock_name).side_effect = RuntimeError("Synthetic integration failure")
    result = _run(
        boundary, execution_mode="CONTROLLED_PROVIDER",
        model_provider=DeterministicMockProvider(_model_output()),
    )
    assert result["status"] == "FAILED_CLOSED"
    assert result["final_outcome"] == "ABSTAIN"
    assert result["failure"]["stage"] == stage
    assert result["governance"]["application_release_ceiling"] == "ABSTAIN"
    assert result["governance"]["authority_increased"] is False
    assert result["governance"]["original_pre_generation"]["decision"] == "AUTO_ANSWER"
    assert "RESPONSE_SELECTED" not in result["execution_trace"]
    if mock_name == "deterministic":
        boundary.execution.assert_not_called()
    if mock_name in {"deterministic", "execution"}:
        boundary.fallback.assert_not_called()


def test_real_provider_metadata_setup_failure_fails_closed(boundary):
    result = _run(boundary, execution_mode="CONTROLLED_PROVIDER", model_provider=object())
    assert result["status"] == "FAILED_CLOSED"
    assert result["failure"]["stage"] == "MODEL_EXECUTION"
    assert result["final_outcome"] == "ABSTAIN"
    boundary.fallback.assert_not_called()


@pytest.mark.parametrize("candidate", [None, [], "not structured", {}])
def test_malformed_resolver_selected_response_fails_closed(boundary, candidate):
    boundary.fallback.side_effect = None
    boundary.fallback.return_value = {
        "final_response_source": "MODEL", "fallback_used": False,
        "fallback_reason": None, "final_response": candidate,
    }
    result = _run(
        boundary, execution_mode="CONTROLLED_PROVIDER",
        model_provider=DeterministicMockProvider(_model_output()),
    )
    assert result["status"] == "FAILED_CLOSED"
    assert result["final_outcome"] == "ABSTAIN"
    assert result["failure"]["stage"] == "RESPONSE_SELECTION"


@pytest.mark.parametrize("field,value", [
    ("packet_id", "OTHER_PACKET"), ("governance_decision", "ABSTAIN"),
    ("response_type", "REVIEW"), ("requires_human_review", True),
    ("sections", []), ("sections", {}), ("citations_used", "E1"),
])
def test_selected_response_envelope_cannot_change_context(boundary, field, value):
    def mismatched_resolution(execution, deterministic):
        resolution = resolve_generation_with_fallback(execution, deterministic)
        resolution["final_response"][field] = value
        return resolution

    boundary.fallback.side_effect = mismatched_resolution
    result = _run(
        boundary, execution_mode="CONTROLLED_PROVIDER",
        model_provider=DeterministicMockProvider(_model_output()),
    )
    assert result["status"] == "FAILED_CLOSED"
    assert result["final_outcome"] == "ABSTAIN"
    assert result["failure"]["stage"] == "RESPONSE_SELECTION"


def test_invalid_deterministic_candidate_fails_closed(boundary):
    boundary.deterministic.side_effect = None
    boundary.deterministic.return_value = None
    result = _run(boundary)
    assert result["status"] == "FAILED_CLOSED"
    assert result["failure"]["stage"] == "RESPONSE_SELECTION"
    assert result["final_outcome"] == "ABSTAIN"
    boundary.execution.assert_not_called()
