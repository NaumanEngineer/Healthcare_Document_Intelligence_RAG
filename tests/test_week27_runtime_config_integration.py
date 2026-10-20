from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from src.application.rag_pipeline import run_rag_pipeline
from src.application.runtime_config import (
    CONTROLLED_PROVIDER,
    DETERMINISTIC_ONLY,
    RAGRuntimeConfig,
    RetrievalConfig,
    RuntimeMetadata,
)


QUESTION = "What is the operational escalation policy?"


def _packet():
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
        "evidence_text": (
            "Operational escalation must follow the approved pathway."
        ),
        "evidence_role": "supporting",
    }

    return {
        "packet_id": "EVIDENCE_PACKET::W27-D3",
        "question": QUESTION,
        "governance": {
            "decision": "REVIEW_REQUIRED",
            "reason": "Human review required.",
            "may_generate_answer": False,
            "requires_human_review": True,
            "document_ids": ["DOC-001"],
            "retrieval_route": "RETURN_INITIAL",
        },
        "precedence_assessment": {
            "decision": "SAFE_TO_COMBINE",
            "reason": "Single active source.",
            "blocking_relationships": [],
        },
        "evidence": {
            "supporting": [evidence],
            "relationship_evidence": [],
            "context": [],
        },
        "evidence_count": 1,
        "document_ids": ["DOC-001"],
        "retrieval": {
            "route": "RETURN_INITIAL",
            "stop_reason": "TEST",
        },
        "evidence_sufficiency": {
            "sufficient": True,
        },
        "missing_evidence": {
            "initial_missing_topics": [],
            "final_missing_topics": [],
            "unsupported_claims": [],
        },
        "lifecycle_summary": {},
        "provenance_summary": {},
    }


@pytest.fixture
def boundary():
    with (
        patch(
            "src.application.rag_pipeline.orchestrate_retrieval",
            return_value={
                "results": [],
            },
        ) as retrieval,
        patch(
            "src.application.rag_pipeline.build_evidence_packet",
            return_value=_packet(),
        ) as packet,
        patch(
            "src.application.rag_pipeline.assure_selected_response",
            return_value={
                "status": "COMPLETED",
                "required_checks_complete": True,
                "final_assurance_decision": "REVIEW_REQUIRED",
                "authority_increased": False,
            },
        ) as assurance,
        patch(
            "src.application.rag_pipeline.finalize_request_governance",
            return_value={
                "decision": "REVIEW_REQUIRED",
                "may_return_answer": False,
                "requires_human_review": True,
                "authority_increased": False,
            },
        ) as final_governance,
    ):
        yield SimpleNamespace(
            retrieval=retrieval,
            packet=packet,
            assurance=assurance,
            final_governance=final_governance,
        )


def _run(**kwargs):
    return run_rag_pipeline(
        question=QUESTION,
        chunks=[],
        embedded_chunks=[],
        embedding_model=object(),
        embedding_model_name="fake-embedding-model",
        **kwargs,
    )


def test_legacy_arguments_remain_authoritative_without_runtime_config(
    boundary,
):
    result = _run(
        semantic_k=7,
        keyword_k=8,
        final_k=4,
        semantic_min_similarity=0.25,
        keyword_min_score=1.5,
        min_rrf_score=0.02,
        rrf_k=40,
        max_related_chunks=5,
        execution_mode=DETERMINISTIC_ONLY,
    )

    call = boundary.retrieval.call_args.kwargs

    assert call["semantic_k"] == 7
    assert call["keyword_k"] == 8
    assert call["final_k"] == 4
    assert call["semantic_min_similarity"] == 0.25
    assert call["keyword_min_score"] == 1.5
    assert call["min_rrf_score"] == 0.02
    assert call["rrf_k"] == 40
    assert call["max_related_chunks"] == 5

    assert result["governance"]["runtime"]["source"] == (
        "LEGACY_ARGUMENTS"
    )
    assert (
        result["governance"]["runtime"]["execution_mode"]
        == DETERMINISTIC_ONLY
    )


def test_runtime_config_overrides_legacy_retrieval_arguments(
    boundary,
):
    config = RAGRuntimeConfig(
        retrieval=RetrievalConfig(
            semantic_k=11,
            keyword_k=12,
            final_k=6,
            semantic_min_similarity=0.45,
            keyword_min_score=2.0,
            min_rrf_score=0.03,
            rrf_k=70,
            max_related_chunks=4,
        ),
        metadata=RuntimeMetadata(
            environment="test",
            application_name="Healthcare RAG",
            runtime_version="week27-day3",
        ),
        execution_mode=DETERMINISTIC_ONLY,
    )

    result = _run(
        semantic_k=1,
        keyword_k=1,
        final_k=1,
        semantic_min_similarity=0.01,
        keyword_min_score=0.01,
        min_rrf_score=0.01,
        rrf_k=1,
        max_related_chunks=1,
        execution_mode=CONTROLLED_PROVIDER,
        runtime_config=config,
    )

    call = boundary.retrieval.call_args.kwargs

    assert call["semantic_k"] == 11
    assert call["keyword_k"] == 12
    assert call["final_k"] == 6
    assert call["semantic_min_similarity"] == 0.45
    assert call["keyword_min_score"] == 2.0
    assert call["min_rrf_score"] == 0.03
    assert call["rrf_k"] == 70
    assert call["max_related_chunks"] == 4

    runtime = result["governance"]["runtime"]

    assert runtime["source"] == "RUNTIME_CONFIG"
    assert runtime["execution_mode"] == DETERMINISTIC_ONLY
    assert runtime["retrieval"]["semantic_k"] == 11
    assert runtime["metadata"]["environment"] == "test"
    assert runtime["metadata"]["runtime_version"] == "week27-day3"


def test_runtime_config_execution_mode_is_authoritative(
    boundary,
):
    config = RAGRuntimeConfig(
        execution_mode=DETERMINISTIC_ONLY
    )

    result = _run(
        execution_mode=CONTROLLED_PROVIDER,
        runtime_config=config,
    )

    assert (
        result["governance"]["generation"]["execution_mode"]
        == DETERMINISTIC_ONLY
    )


def test_invalid_runtime_config_type_fails_closed_before_retrieval(
    boundary,
):
    result = _run(
        runtime_config={},
    )

    assert result["status"] == "FAILED_CLOSED"
    assert result["final_outcome"] == "ABSTAIN"
    assert result["failure"]["stage"] == "INPUT_VALIDATION"

    boundary.retrieval.assert_not_called()


def test_runtime_config_cannot_disable_required_assurance(
    boundary,
):
    from src.application.runtime_config import AssurancePolicy

    config = RAGRuntimeConfig(
        assurance=AssurancePolicy(
            require_citation_assurance=False,
        )
    )

    result = _run(
        runtime_config=config,
    )

    assert result["status"] == "FAILED_CLOSED"
    assert result["final_outcome"] == "ABSTAIN"
    assert result["failure"]["stage"] == "INPUT_VALIDATION"

    boundary.retrieval.assert_not_called()


def test_runtime_config_does_not_mutate_caller_object(
    boundary,
):
    config = RAGRuntimeConfig(
        retrieval=RetrievalConfig(
            semantic_k=9,
            keyword_k=8,
            final_k=5,
        ),
        metadata=RuntimeMetadata(
            environment="test",
            application_name="Healthcare RAG",
            runtime_version="week27-day3",
        ),
    )

    before = deepcopy(
        config.to_dict()
    )

    _run(
        runtime_config=config,
    )

    assert config.to_dict() == before