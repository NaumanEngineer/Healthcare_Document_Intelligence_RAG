from src.governance.retrieval_review_integration import (
    decide_retrieval_governance_outcome,
)
from src.governance.review_decision import (
    ABSTAIN,
    AUTO_ANSWER,
    REVIEW_REQUIRED,
)


def _result(
    *,
    document_id="DOC-001",
    status="Active",
    similarity_score=0.80,
):
    return {
        "document_id": document_id,
        "status": status,
        "similarity_score": similarity_score,
    }


def _retrieval_output(
    *,
    results,
    sufficient,
    allowed=True,
    selected_route="RETURN_INITIAL",
    stop_reason="INITIAL_EVIDENCE_SUFFICIENT",
):
    return {
        "results": results,
        "audit": {
            "scope": {
                "scope": (
                    "IN_SCOPE"
                    if allowed
                    else "OUT_OF_SCOPE"
                ),
                "allowed": allowed,
            },
            "selected_route": selected_route,
            "stop_reason": stop_reason,
            "final_evidence": {
                "sufficient": sufficient,
            },
        },
    }


def test_insufficient_evidence_abstains_even_with_high_similarity():
    output = _retrieval_output(
        results=[
            _result(
                similarity_score=0.99,
            )
        ],
        sufficient=False,
        selected_route="STOP_INSUFFICIENT",
        stop_reason="NO_SAFE_RETRIEVAL_EXPANSION",
    )

    result = decide_retrieval_governance_outcome(
        question="Explain staffing escalation",
        retrieval_output=output,
    )

    assert result["decision"] == ABSTAIN
    assert result["may_generate_answer"] is False
    assert result["requires_human_review"] is False


def test_sufficient_strong_active_evidence_can_auto_answer():
    output = _retrieval_output(
        results=[
            _result(
                similarity_score=0.82,
            )
        ],
        sufficient=True,
    )

    result = decide_retrieval_governance_outcome(
        question="Explain staffing escalation",
        retrieval_output=output,
    )

    assert result["decision"] == AUTO_ANSWER
    assert result["may_generate_answer"] is True
    assert result["requires_human_review"] is False


def test_sufficient_but_weak_evidence_requires_review():
    output = _retrieval_output(
        results=[
            _result(
                similarity_score=0.60,
            )
        ],
        sufficient=True,
    )

    result = decide_retrieval_governance_outcome(
        question="Explain staffing escalation",
        retrieval_output=output,
    )

    assert result["decision"] == REVIEW_REQUIRED
    assert result["may_generate_answer"] is False
    assert result["requires_human_review"] is True


def test_sufficient_ambiguous_scores_require_review():
    output = _retrieval_output(
        results=[
            _result(
                document_id="DOC-001",
                similarity_score=0.80,
            ),
            _result(
                document_id="DOC-002",
                similarity_score=0.77,
            ),
        ],
        sufficient=True,
    )

    result = decide_retrieval_governance_outcome(
        question="Explain staffing escalation",
        retrieval_output=output,
    )

    assert result["decision"] == REVIEW_REQUIRED
    assert result["may_generate_answer"] is False
    assert result["requires_human_review"] is True


def test_lifecycle_risk_cannot_be_bypassed():
    output = _retrieval_output(
        results=[
            _result(
                status="Draft",
                similarity_score=0.99,
            )
        ],
        sufficient=True,
    )

    result = decide_retrieval_governance_outcome(
        question="Explain staffing escalation",
        retrieval_output=output,
    )

    assert result["decision"] == REVIEW_REQUIRED
    assert result["may_generate_answer"] is False
    assert result["requires_human_review"] is True


def test_cross_document_intent_cannot_be_bypassed():
    output = _retrieval_output(
        results=[
            _result(
                document_id="DOC-001",
                similarity_score=0.90,
            ),
            _result(
                document_id="DOC-002",
                similarity_score=0.70,
            ),
        ],
        sufficient=True,
    )

    result = decide_retrieval_governance_outcome(
        question=(
            "Compare staffing and bed pressure "
            "across documents"
        ),
        retrieval_output=output,
    )

    assert result["decision"] == REVIEW_REQUIRED
    assert result["may_generate_answer"] is False
    assert result["requires_human_review"] is True


def test_out_of_scope_retrieval_remains_abstain():
    output = _retrieval_output(
        results=[],
        sufficient=False,
        allowed=False,
        selected_route="STOP_OUT_OF_SCOPE",
        stop_reason="ORIGINAL_QUERY_OUT_OF_SCOPE",
    )

    result = decide_retrieval_governance_outcome(
        question="What medication should be prescribed?",
        retrieval_output=output,
    )

    assert result["decision"] == ABSTAIN
    assert result["may_generate_answer"] is False
    assert result["requires_human_review"] is False


def test_missing_final_evidence_fails_closed():
    output = {
        "results": [
            _result(
                similarity_score=0.99,
            )
        ],
        "audit": {
            "scope": {
                "scope": "IN_SCOPE",
                "allowed": True,
            },
            "selected_route": "RETURN_INITIAL",
            "stop_reason": "UNKNOWN",
            "final_evidence": None,
        },
    }

    result = decide_retrieval_governance_outcome(
        question="Explain staffing escalation",
        retrieval_output=output,
    )

    assert result["decision"] == ABSTAIN
    assert result["may_generate_answer"] is False


def test_retrieval_route_is_preserved_in_governance_output():
    output = _retrieval_output(
        results=[
            _result(
                similarity_score=0.82,
            )
        ],
        sufficient=True,
        selected_route="BOUNDED_AGENTIC",
        stop_reason="EVIDENCE_SUFFICIENT_AFTER_REFINEMENT",
    )

    result = decide_retrieval_governance_outcome(
        question="Explain staffing escalation",
        retrieval_output=output,
    )

    assert result["retrieval_route"] == "BOUNDED_AGENTIC"

    assert result["retrieval_stop_reason"] == (
        "EVIDENCE_SUFFICIENT_AFTER_REFINEMENT"
    )