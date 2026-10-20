"""Session 4 composition checks using the real answer contract/context builders."""

from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from src.application.rag_pipeline import run_rag_pipeline
from src.generation.answer_contract import build_answer_contract
from src.generation.answer_context import build_answer_context


QUESTION = "What is the operational escalation policy?"
DECISIONS = ("AUTO_ANSWER", "REVIEW_REQUIRED", "ABSTAIN")
PRECEDENCE = (
    "SAFE_TO_COMBINE", "REVIEW_BEFORE_COMBINATION", "BLOCK_COMBINATION",
)


def _packet(decision="AUTO_ANSWER", precedence="SAFE_TO_COMBINE"):
    evidence = {
        "evidence_id": "EVIDENCE::DOC-001-V1.0-P001-C001",
        "document_id": "DOC-001",
        "chunk_id": "DOC-001-V1.0-P001-C001",
        "title": "Operational Policy",
        "document_type": "Policy",
        "source_file": "policy.pdf",
        "version": "1.0",
        "status": "Active",
        "page": 1,
        "evidence_text": "SENSITIVE_EVIDENCE_NOT_FOR_APPLICATION_SUMMARY",
        "evidence_role": "supporting",
    }
    return {
        "packet_id": "EVIDENCE_PACKET::SESSION4",
        "question": QUESTION,
        "governance": {
            "decision": decision,
            "reason": "Mature governance assessment.",
            "may_generate_answer": decision == "AUTO_ANSWER",
            "requires_human_review": decision == "REVIEW_REQUIRED",
            "document_ids": ["DOC-001"],
            "retrieval_route": "RETURN_INITIAL",
        },
        "precedence_assessment": {
            "decision": precedence,
            "reason": "Mature precedence assessment.",
            "blocking_relationships": ["conflict"] if precedence == "BLOCK_COMBINATION" else [],
        },
        "evidence": {
            "supporting": [evidence] if decision != "ABSTAIN" else [],
            "relationship_evidence": [],
            "context": [],
        },
        "evidence_count": 0 if decision == "ABSTAIN" else 1,
        "document_ids": ["DOC-001"],
        "retrieval": {"route": "RETURN_INITIAL", "stop_reason": "TEST"},
        "evidence_sufficiency": {"sufficient": decision != "ABSTAIN"},
        "missing_evidence": {
            "initial_missing_topics": [], "final_missing_topics": [],
            "unsupported_claims": [],
        },
        "lifecycle_summary": {},
        "provenance_summary": {},
    }


@pytest.fixture
def boundary():
    with (
        patch("src.application.rag_pipeline.orchestrate_retrieval", return_value={}) as retrieval,
        patch("src.application.rag_pipeline.build_evidence_packet") as packet,
        patch("src.application.rag_pipeline.build_answer_contract", wraps=build_answer_contract) as contract,
        patch("src.application.rag_pipeline.build_answer_context", wraps=build_answer_context) as context,
    ):
        yield SimpleNamespace(
            retrieval=retrieval, packet=packet, contract=contract, context=context,
        )


def _run(boundary, packet):
    boundary.packet.return_value = packet
    return run_rag_pipeline(
        question=QUESTION,
        chunks=[], embedded_chunks=[],
        embedding_model=object(), embedding_model_name="fake-embedding-model",
    )


@pytest.mark.parametrize("decision", DECISIONS)
@pytest.mark.parametrize("precedence", PRECEDENCE)
def test_authority_composition_and_coherent_real_builders(boundary, decision, precedence):
    packet = _packet(decision, precedence)
    original = deepcopy(packet)
    result = _run(boundary, packet)
    expected = (
        "REVIEW_REQUIRED"
        if decision == "AUTO_ANSWER" and precedence != "SAFE_TO_COMBINE"
        else decision
    )
    audit = result["governance"]
    effective = audit["effective_pre_generation"]
    assert result["status"] == "COMPLETED"
    assert effective["decision"] == expected
    assert effective["may_generate_answer"] is (expected == "AUTO_ANSWER")
    assert effective["requires_human_review"] is (expected == "REVIEW_REQUIRED")
    assert audit["authority_reduced"] is (expected != decision)
    assert bool(audit["reduction_reason"]) is (expected != decision)
    assert audit["original_pre_generation"] == original["governance"]
    assert audit["precedence"] == original["precedence_assessment"]
    assert audit["pre_generation"] == original["governance"]
    assert packet == original
    assert audit["original_pre_generation"] is not packet["governance"]
    assert audit["precedence"] is not packet["precedence_assessment"]

    release = "ABSTAIN" if expected == "ABSTAIN" else "REVIEW_REQUIRED"
    assert result["final_outcome"] == release
    assert audit["application_release_ceiling"] == release
    assert audit["authority_increased"] is False
    assert result["assurance"]["status"] == "COMPLETED"
    levels = {"AUTO_ANSWER": 2, "REVIEW_REQUIRED": 1, "ABSTAIN": 0}
    assert levels[release] <= levels[expected] <= levels[decision]

    boundary.retrieval.assert_called_once()
    boundary.contract.assert_called_once()
    boundary.context.assert_called_once()
    contract_packet = boundary.contract.call_args.args[0]
    context_packet, contract = boundary.context.call_args.args
    assert contract_packet is context_packet
    assert context_packet is not packet
    assert context_packet["governance"] == effective
    assert contract["governance_decision"] == expected
    assert contract["packet_id"] == packet["packet_id"]
    summary = audit["answer_context"]
    assert summary["packet_id"] == packet["packet_id"]
    assert summary["governance_decision"] == expected
    assert summary["generation_permitted"] is (expected == "AUTO_ANSWER")
    assert summary["requires_human_review"] is (expected == "REVIEW_REQUIRED")
    assert summary["evidence_count"] == (0 if expected == "ABSTAIN" else 1)
    assert summary["citation_count"] == summary["evidence_count"]
    assert "SENSITIVE_EVIDENCE_NOT_FOR_APPLICATION_SUMMARY" not in str(result)
    assert result["execution_trace"] == [
        "REQUEST_RECEIVED", "INPUT_VALIDATED", "RETRIEVAL_COMPLETED",
        "EVIDENCE_PACKET_BUILT", "PRE_GOVERNANCE_COMPLETED",
        "ANSWER_CONTRACT_BUILT", "ANSWER_CONTEXT_BUILT",
        "DETERMINISTIC_RESPONSE_BUILT", "RESPONSE_SELECTED",
        "ASSURANCE_COMPLETED", "FINAL_GOVERNANCE_COMPLETED",
    ]


@pytest.mark.parametrize("field", ["governance", "precedence_assessment"])
@pytest.mark.parametrize("invalid", [None, [], "invalid", {}, {"decision": []}])
def test_malformed_assessment_fails_closed(boundary, field, invalid):
    packet = _packet()
    packet[field] = invalid
    original = deepcopy(packet)
    result = _run(boundary, packet)
    assert result["status"] == "FAILED_CLOSED"
    assert result["final_outcome"] == "ABSTAIN"
    assert result["failure"]["stage"] == "PRE_GENERATION_GOVERNANCE"
    assert result["governance"]["application_release_ceiling"] == "ABSTAIN"
    assert result["governance"]["original_pre_generation"] == original["governance"]
    assert result["governance"]["precedence"] == original["precedence_assessment"]
    assert packet == original
    boundary.contract.assert_not_called()
    boundary.context.assert_not_called()


@pytest.mark.parametrize("decision", [None, True, 1, [], {}, "", "UNKNOWN", "PASS"])
def test_invalid_governance_decision_fails_closed(boundary, decision):
    packet = _packet()
    packet["governance"]["decision"] = decision
    result = _run(boundary, packet)
    assert result["status"] == "FAILED_CLOSED"
    assert result["final_outcome"] == "ABSTAIN"
    assert result["failure"]["stage"] == "PRE_GENERATION_GOVERNANCE"
    boundary.contract.assert_not_called()


@pytest.mark.parametrize("decision", [None, True, 1, [], {}, "", "UNKNOWN", "PASS"])
def test_invalid_precedence_decision_fails_closed_even_for_abstention(boundary, decision):
    packet = _packet("ABSTAIN")
    packet["precedence_assessment"]["decision"] = decision
    result = _run(boundary, packet)
    assert result["status"] == "FAILED_CLOSED"
    assert result["final_outcome"] == "ABSTAIN"
    assert result["failure"]["stage"] == "PRE_GENERATION_GOVERNANCE"
    boundary.contract.assert_not_called()


@pytest.mark.parametrize("key,value", [
    ("may_generate_answer", False), ("may_generate_answer", 1),
    ("requires_human_review", True), ("requires_human_review", 0),
    ("reason", ""), ("document_ids", "DOC-001"),
])
def test_malformed_governance_is_not_repaired_by_precedence_reduction(boundary, key, value):
    packet = _packet(precedence="REVIEW_BEFORE_COMBINATION")
    packet["governance"][key] = value
    result = _run(boundary, packet)
    assert result["status"] == "FAILED_CLOSED"
    assert result["final_outcome"] == "ABSTAIN"
    assert result["failure"]["stage"] == "PRE_GENERATION_GOVERNANCE"
    boundary.contract.assert_not_called()


@pytest.mark.parametrize("builder,stage", [
    ("contract", "ANSWER_CONTRACT"), ("context", "ANSWER_CONTEXT"),
])
def test_builder_exception_fails_closed_and_preserves_audit(boundary, builder, stage):
    packet = _packet(precedence="BLOCK_COMBINATION")
    original = deepcopy(packet)
    getattr(boundary, builder).side_effect = RuntimeError("Synthetic preparation failure")
    result = _run(boundary, packet)
    assert result["status"] == "FAILED_CLOSED"
    assert result["final_outcome"] == "ABSTAIN"
    assert result["failure"]["stage"] == stage
    assert result["governance"]["original_pre_generation"] == original["governance"]
    assert result["governance"]["effective_pre_generation"]["decision"] == "REVIEW_REQUIRED"
    assert result["governance"]["precedence"] == original["precedence_assessment"]
    assert result["governance"]["application_release_ceiling"] == "ABSTAIN"
    assert "ANSWER_CONTEXT_BUILT" not in result["execution_trace"]
    if builder == "contract":
        boundary.context.assert_not_called()
    assert packet == original


def test_real_context_identity_validation_is_preserved(boundary):
    def mismatched_contract(packet):
        contract = build_answer_contract(packet)
        contract["packet_id"] = "WRONG_PACKET"
        return contract

    boundary.contract.side_effect = mismatched_contract
    result = _run(boundary, _packet())
    assert result["status"] == "FAILED_CLOSED"
    assert result["final_outcome"] == "ABSTAIN"
    assert result["failure"]["stage"] == "ANSWER_CONTEXT"
    assert "packet IDs do not match" in result["failure"]["reason"]


def test_missing_non_abstain_evidence_is_rejected_by_real_context(boundary):
    packet = _packet()
    packet["evidence"]["supporting"] = []
    result = _run(boundary, packet)
    assert result["status"] == "FAILED_CLOSED"
    assert result["failure"]["stage"] == "ANSWER_CONTEXT"
    assert result["final_outcome"] == "ABSTAIN"


def test_result_audit_does_not_alias_original_packet(boundary):
    packet = _packet(precedence="BLOCK_COMBINATION")
    original = deepcopy(packet)
    result = _run(boundary, packet)
    result["governance"]["effective_pre_generation"]["document_ids"].append("DOC-NEW")
    result["governance"]["precedence"]["blocking_relationships"].clear()
    assert packet == original
