from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


VALID_REVIEW_STATUSES = {
    "NOT_REQUIRED",
    "PENDING",
    "APPROVED",
    "REJECTED",
    "OVERRIDDEN",
}


def build_audit_record(
    *,
    query_id: str,
    question: str,
    scope_assessment: dict[str, Any],
    decision: dict[str, Any],
    results: list[dict[str, Any]],
    retrieval_method: str,
    reviewer_status: str | None = None,
) -> dict[str, Any]:
    """
    Build a structured governance audit record for one query.
    """

    if not isinstance(query_id, str) or not query_id.strip():
        raise ValueError(
            "query_id must be a non-empty string"
        )

    if not isinstance(question, str) or not question.strip():
        raise ValueError(
            "question must be a non-empty string"
        )

    if not isinstance(scope_assessment, dict):
        raise TypeError(
            "scope_assessment must be a dictionary"
        )

    if not isinstance(decision, dict):
        raise TypeError(
            "decision must be a dictionary"
        )

    if not isinstance(results, list):
        raise TypeError(
            "results must be a list"
        )

    if not isinstance(retrieval_method, str) or not retrieval_method.strip():
        raise ValueError(
            "retrieval_method must be a non-empty string"
        )

    requires_review = bool(
        decision.get(
            "requires_human_review"
        )
    )

    if reviewer_status is None:
        reviewer_status = (
            "PENDING"
            if requires_review
            else "NOT_REQUIRED"
        )

    if reviewer_status not in VALID_REVIEW_STATUSES:
        raise ValueError(
            "invalid reviewer_status"
        )

    evidence = []

    for result in results:
        evidence.append(
            {
                "document_id": result.get(
                    "document_id"
                ),
                "title": result.get(
                    "title"
                ),
                "version": result.get(
                    "version"
                ),
                "status": result.get(
                    "status"
                ),
                "page": result.get(
                    "page"
                ),
                "chunk_id": result.get(
                    "chunk_id"
                ),
                "similarity_score": result.get(
                    "similarity_score"
                ),
                "keyword_score": result.get(
                    "keyword_score"
                ),
                "rrf_score": result.get(
                    "rrf_score"
                ),
            }
        )

    return {
        "query_id": query_id,
        "question": question,
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "retrieval_method": retrieval_method,
        "scope": scope_assessment.get(
            "scope"
        ),
        "scope_allowed": scope_assessment.get(
            "allowed"
        ),
        "scope_reason": scope_assessment.get(
            "reason"
        ),
        "decision": decision.get(
            "decision"
        ),
        "decision_reason": decision.get(
            "reason"
        ),
        "requires_human_review": requires_review,
        "may_generate_answer": decision.get(
            "may_generate_answer"
        ),
        "document_ids": decision.get(
            "document_ids",
            [],
        ),
        "evidence": evidence,
        "reviewer_status": reviewer_status,
        "reviewer_id": None,
        "reviewer_comment": None,
        "reviewed_at_utc": None,
    }