from src.governance.retrieval_review_integration import (
    decide_retrieval_governance_outcome,
)
from src.governance.review_decision import (
    ABSTAIN,
    AUTO_ANSWER,
    REVIEW_REQUIRED,
    decide_post_generation_outcome,
)


def _result(
    *,
    document_id="DOC-001",
    status="Active",
    similarity_score=0.82,
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


def test_auto_answer_plus_citation_pass_returns_answer():
    retrieval = _retrieval_output(
        results=[
            _result(
                similarity_score=0.82,
            )
        ],
        sufficient=True,
    )

    pre = decide_retrieval_governance_outcome(
        question="Explain staffing escalation",
        retrieval_output=retrieval,
    )

    final = decide_post_generation_outcome(
        pre,
        {
            "decision": "PASS",
        },
    )

    assert pre["decision"] == AUTO_ANSWER
    assert final["decision"] == AUTO_ANSWER
    assert final["may_return_answer"] is True


def test_auto_answer_can_be_downgraded_to_review():
    retrieval = _retrieval_output(
        results=[
            _result(
                similarity_score=0.82,
            )
        ],
        sufficient=True,
    )

    pre = decide_retrieval_governance_outcome(
        question="Explain staffing escalation",
        retrieval_output=retrieval,
    )

    final = decide_post_generation_outcome(
        pre,
        {
            "decision": REVIEW_REQUIRED,
        },
    )

    assert pre["decision"] == AUTO_ANSWER
    assert final["decision"] == REVIEW_REQUIRED
    assert final["may_return_answer"] is False


def test_auto_answer_can_be_downgraded_to_abstain():
    retrieval = _retrieval_output(
        results=[
            _result(
                similarity_score=0.82,
            )
        ],
        sufficient=True,
    )

    pre = decide_retrieval_governance_outcome(
        question="Explain staffing escalation",
        retrieval_output=retrieval,
    )

    final = decide_post_generation_outcome(
        pre,
        {
            "decision": ABSTAIN,
        },
    )

    assert pre["decision"] == AUTO_ANSWER
    assert final["decision"] == ABSTAIN
    assert final["may_return_answer"] is False


def test_insufficient_retrieval_cannot_be_upgraded_by_citation_pass():
    retrieval = _retrieval_output(
        results=[
            _result(
                similarity_score=0.99,
            )
        ],
        sufficient=False,
        selected_route="STOP_INSUFFICIENT",
        stop_reason="NO_SAFE_RETRIEVAL_EXPANSION",
    )

    pre = decide_retrieval_governance_outcome(
        question="Explain staffing escalation",
        retrieval_output=retrieval,
    )

    final = decide_post_generation_outcome(
        pre,
        {
            "decision": "PASS",
        },
    )

    assert pre["decision"] == ABSTAIN
    assert final["decision"] == ABSTAIN
    assert final["may_return_answer"] is False


def test_review_required_cannot_be_upgraded_by_citation_pass():
    retrieval = _retrieval_output(
        results=[
            _result(
                similarity_score=0.60,
            )
        ],
        sufficient=True,
    )

    pre = decide_retrieval_governance_outcome(
        question="Explain staffing escalation",
        retrieval_output=retrieval,
    )

    final = decide_post_generation_outcome(
        pre,
        {
            "decision": "PASS",
        },
    )

    assert pre["decision"] == REVIEW_REQUIRED
    assert final["decision"] == REVIEW_REQUIRED
    assert final["may_return_answer"] is False


def test_out_of_scope_retrieval_cannot_be_upgraded():
    retrieval = _retrieval_output(
        results=[],
        sufficient=False,
        allowed=False,
        selected_route="STOP_OUT_OF_SCOPE",
        stop_reason="ORIGINAL_QUERY_OUT_OF_SCOPE",
    )

    pre = decide_retrieval_governance_outcome(
        question="What medication should be prescribed?",
        retrieval_output=retrieval,
    )

    final = decide_post_generation_outcome(
        pre,
        {
            "decision": "PASS",
        },
    )

    assert pre["decision"] == ABSTAIN
    assert final["decision"] == ABSTAIN
    assert final["may_return_answer"] is False


def test_relationship_route_still_respects_cross_document_review():
    retrieval = _retrieval_output(
        results=[
            _result(
                document_id="DOC-011",
                similarity_score=0.90,
            ),
            _result(
                document_id="DOC-003",
                similarity_score=0.72,
            ),
        ],
        sufficient=True,
        selected_route="RELATIONSHIP_AWARE",
        stop_reason=(
            "EVIDENCE_SUFFICIENT_AFTER_RELATIONSHIP_EXPANSION"
        ),
    )

    pre = decide_retrieval_governance_outcome(
        question=(
            "Compare the relationship between staffing "
            "and workforce escalation across documents"
        ),
        retrieval_output=retrieval,
    )

    final = decide_post_generation_outcome(
        pre,
        {
            "decision": "PASS",
        },
    )

    assert pre["decision"] == REVIEW_REQUIRED
    assert final["decision"] == REVIEW_REQUIRED
    assert final["may_return_answer"] is False