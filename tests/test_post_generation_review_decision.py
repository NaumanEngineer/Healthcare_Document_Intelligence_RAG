from src.governance.review_decision import (
    ABSTAIN,
    AUTO_ANSWER,
    REVIEW_REQUIRED,
    decide_post_generation_outcome,
)


def _pre(decision):
    return {
        "decision": decision,
        "document_ids": ["DOC-001"],
    }


def _citation(decision):
    return {
        "decision": decision,
    }


def test_auto_answer_plus_pass_remains_auto_answer():
    result = decide_post_generation_outcome(
        _pre(AUTO_ANSWER),
        _citation("PASS"),
    )

    assert result["decision"] == AUTO_ANSWER
    assert result["may_return_answer"] is True
    assert result["requires_human_review"] is False


def test_auto_answer_plus_review_becomes_review_required():
    result = decide_post_generation_outcome(
        _pre(AUTO_ANSWER),
        _citation(REVIEW_REQUIRED),
    )

    assert result["decision"] == REVIEW_REQUIRED
    assert result["may_return_answer"] is False
    assert result["requires_human_review"] is True


def test_auto_answer_plus_abstain_becomes_abstain():
    result = decide_post_generation_outcome(
        _pre(AUTO_ANSWER),
        _citation(ABSTAIN),
    )

    assert result["decision"] == ABSTAIN
    assert result["may_return_answer"] is False


def test_pre_generation_abstain_cannot_be_upgraded_by_pass():
    result = decide_post_generation_outcome(
        _pre(ABSTAIN),
        _citation("PASS"),
    )

    assert result["decision"] == ABSTAIN
    assert result["may_return_answer"] is False


def test_pre_generation_review_cannot_be_upgraded_by_pass():
    result = decide_post_generation_outcome(
        _pre(REVIEW_REQUIRED),
        _citation("PASS"),
    )

    assert result["decision"] == REVIEW_REQUIRED
    assert result["may_return_answer"] is False


def test_unknown_citation_decision_fails_safe():
    result = decide_post_generation_outcome(
        _pre(AUTO_ANSWER),
        _citation("UNKNOWN"),
    )

    assert result["decision"] == REVIEW_REQUIRED
    assert result["may_return_answer"] is False