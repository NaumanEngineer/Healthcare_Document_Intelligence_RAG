from src.governance.review_decision import (
    ABSTAIN,
    AUTO_ANSWER,
    REVIEW_REQUIRED,
    decide_review_outcome,
)


def test_out_of_scope_query_abstains():
    result = decide_review_outcome(
        question=(
            "What antibiotic dose should be used?"
        ),
        scope_assessment={
            "allowed": False,
        },
        results=[],
    )

    assert result["decision"] == ABSTAIN
    assert result["may_generate_answer"] is False


def test_no_evidence_abstains():
    result = decide_review_outcome(
        question=(
            "What operational guidance applies?"
        ),
        scope_assessment={
            "allowed": True,
        },
        results=[],
    )

    assert result["decision"] == ABSTAIN


def test_single_strong_active_document_can_auto_answer():
    result = decide_review_outcome(
        question=(
            "What guidance applies during winter pressure?"
        ),
        scope_assessment={
            "allowed": True,
        },
        results=[
            {
                "document_id": "DOC-002",
                "status": "Active",
                "similarity_score": 0.72,
            }
        ],
    )

    assert result["decision"] == AUTO_ANSWER
    assert result["may_generate_answer"] is True


def test_superseded_evidence_requires_review():
    result = decide_review_outcome(
        question=(
            "What is the escalation process?"
        ),
        scope_assessment={
            "allowed": True,
        },
        results=[
            {
                "document_id": "DOC-001",
                "status": "Superseded",
            }
        ],
    )

    assert (
        result["decision"]
        == REVIEW_REQUIRED
    )


def test_cross_document_question_requires_review():
    result = decide_review_outcome(
        question=(
            "How should workforce and bed capacity "
            "pressures be managed together?"
        ),
        scope_assessment={
            "allowed": True,
        },
        results=[
            {
                "document_id": "DOC-003",
                "status": "Active",
            },
            {
                "document_id": "DOC-004",
                "status": "Active",
            },
        ],
    )

    assert (
        result["decision"]
        == REVIEW_REQUIRED
    )


def test_three_competing_documents_require_review():
    result = decide_review_outcome(
        question=(
            "What should operational leadership do?"
        ),
        scope_assessment={
            "allowed": True,
        },
        results=[
            {
                "document_id": "DOC-001",
                "status": "Active",
            },
            {
                "document_id": "DOC-006",
                "status": "Active",
            },
            {
                "document_id": "DOC-013",
                "status": "Active",
            },
        ],
    )

    assert (
        result["decision"]
        == REVIEW_REQUIRED
    )