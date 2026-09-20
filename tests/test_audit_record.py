from src.governance.audit_record import (
    build_audit_record,
)


def test_review_required_defaults_to_pending():
    record = build_audit_record(
        query_id="Q001",
        question="What should operational leadership do?",
        scope_assessment={
            "scope": "IN_SCOPE",
            "allowed": True,
            "reason": "Operational query",
        },
        decision={
            "decision": "REVIEW_REQUIRED",
            "reason": "Evidence ambiguous",
            "requires_human_review": True,
            "may_generate_answer": False,
            "document_ids": [
                "DOC-001",
            ],
        },
        results=[
            {
                "document_id": "DOC-001",
                "title": "Operational Escalation Policy",
                "version": "1.0",
                "status": "Active",
                "page": 1,
                "chunk_id": "DOC-001-C001",
                "similarity_score": 0.65,
            }
        ],
        retrieval_method="hybrid",
    )

    assert record["reviewer_status"] == "PENDING"
    assert record["decision"] == "REVIEW_REQUIRED"
    assert record["evidence"][0]["document_id"] == "DOC-001"


def test_auto_answer_defaults_to_not_required():
    record = build_audit_record(
        query_id="Q003",
        question="Which guidance covers bed capacity?",
        scope_assessment={
            "scope": "IN_SCOPE",
            "allowed": True,
        },
        decision={
            "decision": "AUTO_ANSWER",
            "reason": "Strong evidence",
            "requires_human_review": False,
            "may_generate_answer": True,
            "document_ids": [
                "DOC-004",
            ],
        },
        results=[
            {
                "document_id": "DOC-004",
                "status": "Active",
            }
        ],
        retrieval_method="hybrid",
    )

    assert record["reviewer_status"] == "NOT_REQUIRED"
    assert record["may_generate_answer"] is True


def test_abstain_defaults_to_not_required():
    record = build_audit_record(
        query_id="Q007",
        question="What medication should be prescribed?",
        scope_assessment={
            "scope": "OUT_OF_SCOPE",
            "allowed": False,
        },
        decision={
            "decision": "ABSTAIN",
            "reason": "Out of scope",
            "requires_human_review": False,
            "may_generate_answer": False,
            "document_ids": [],
        },
        results=[],
        retrieval_method="hybrid",
    )

    assert record["reviewer_status"] == "NOT_REQUIRED"
    assert record["decision"] == "ABSTAIN"