"""Evidence Packet construction.

Week 22 Day 2.

An Evidence Packet groups Architecture v2 retrieval evidence,
provenance, sufficiency and governance into one deterministic,
auditable structure.

The packet does not create new claims and does not grant permission
to answer. Existing retrieval and governance controls remain
authoritative.
"""

from __future__ import annotations

import hashlib

from src.evidence.evidence_from_retrieval import (
    build_evidence_from_retrieval,
)
from src.governance.retrieval_review_integration import (
    decide_retrieval_governance_outcome,
)


def _require_non_empty_string(
    value,
    field_name: str,
) -> str:
    """Validate a required non-empty string."""

    if (
        not isinstance(value, str)
        or not value.strip()
    ):
        raise ValueError(
            f"{field_name} must be a non-empty string"
        )

    return value.strip()


def _build_packet_id(
    question: str,
) -> str:
    """Create a deterministic packet identifier from the question."""

    digest = hashlib.sha256(
        question.encode(
            "utf-8"
        )
    ).hexdigest()[:16]

    return (
        f"EVIDENCE_PACKET::{digest}"
    )


def _unique_document_ids(
    evidence_objects: list[dict],
) -> list[str]:
    """Return unique evidence document IDs preserving order."""

    document_ids: list[str] = []

    for evidence in evidence_objects:
        document_id = evidence.get(
            "document_id"
        )

        if (
            isinstance(document_id, str)
            and document_id
            and document_id not in document_ids
        ):
            document_ids.append(
                document_id
            )

    return document_ids


def _group_evidence_by_role(
    evidence_objects: list[dict],
) -> dict:
    """Group evidence objects by their existing evidence role."""

    grouped = {
        "supporting": [],
        "relationship_evidence": [],
        "context": [],
    }

    for evidence in evidence_objects:
        role = evidence.get(
            "evidence_role"
        )

        if role not in grouped:
            raise ValueError(
                "Evidence object contains unsupported "
                f"evidence_role: {role}"
            )

        grouped[
            role
        ].append(
            evidence
        )

    return grouped


def _build_lifecycle_summary(
    evidence_objects: list[dict],
) -> dict:
    """Summarise lifecycle states without changing their meaning."""

    status_counts: dict[str, int] = {}

    for evidence in evidence_objects:
        status = evidence.get(
            "status"
        )

        if (
            not isinstance(status, str)
            or not status.strip()
        ):
            raise ValueError(
                "Evidence object is missing valid status"
            )

        status_counts[
            status
        ] = (
            status_counts.get(
                status,
                0,
            )
            + 1
        )

    return {
        "status_counts": status_counts,
        "all_active": (
            bool(evidence_objects)
            and all(
                evidence.get(
                    "status"
                )
                == "Active"
                for evidence in evidence_objects
            )
        ),
    }


def _compact_evidence_sufficiency(
    final_evidence: dict | None,
) -> dict | None:
    """Preserve the current evidence-sufficiency decision."""

    if final_evidence is None:
        return None

    if not isinstance(
        final_evidence,
        dict,
    ):
        raise ValueError(
            "final_evidence must be a dictionary or None"
        )

    return {
        "sufficient": final_evidence.get(
            "sufficient"
        ),
        "decision": final_evidence.get(
            "decision"
        ),
        "reason": final_evidence.get(
            "reason"
        ),
        "matched_query_terms": final_evidence.get(
            "matched_query_terms",
            [],
        ),
        "evidence_terms": final_evidence.get(
            "evidence_terms",
            [],
        ),
        "result_count": final_evidence.get(
            "result_count"
        ),
        "topic_sufficient": final_evidence.get(
            "topic_sufficient"
        ),
        "claim_sufficient": final_evidence.get(
            "claim_sufficient"
        ),
        "claim_requirements": final_evidence.get(
            "claim_requirements",
            [],
        ),
        "unsupported_claims": final_evidence.get(
            "unsupported_claims",
            [],
        ),
    }


def _build_missing_evidence(
    audit: dict,
    final_evidence: dict | None,
) -> dict:
    """Separate initial diagnosed gaps from final unresolved gaps.

    routing_decision.missing_topics describes why Architecture v2
    considered an enhancement route after the initial retrieval.

    Those topics must not automatically be reported as still missing
    after successful bounded recovery.

    Final unresolved claim gaps remain authoritative from the final
    evidence-sufficiency assessment.
    """

    initial_missing_topics = []

    routing_decision = audit.get(
        "routing_decision"
    )

    if isinstance(
        routing_decision,
        dict,
    ):
        value = routing_decision.get(
            "missing_topics",
            [],
        )

        if isinstance(
            value,
            list,
        ):
            initial_missing_topics = value

    final_unsupported_claims = []

    final_sufficient = False

    if isinstance(
        final_evidence,
        dict,
    ):
        final_sufficient = (
            final_evidence.get(
                "sufficient"
            )
            is True
        )

        value = final_evidence.get(
            "unsupported_claims",
            [],
        )

        if isinstance(
            value,
            list,
        ):
            final_unsupported_claims = value

    # If final evidence is sufficient, the initial topic diagnosis
    # was successfully resolved and must not be labelled as missing.
    final_missing_topics = (
        []
        if final_sufficient
        else initial_missing_topics
    )

    return {
        "initial_missing_topics": (
            initial_missing_topics
        ),
        "final_missing_topics": (
            final_missing_topics
        ),
        "unsupported_claims": (
            final_unsupported_claims
        ),
    }


def _compact_governance(
    governance: dict,
) -> dict:
    """Preserve the authoritative governance outcome."""

    if not isinstance(
        governance,
        dict,
    ):
        raise TypeError(
            "governance must be a dictionary"
        )

    return {
        "decision": governance.get(
            "decision"
        ),
        "reason": governance.get(
            "reason"
        ),
        "requires_human_review": governance.get(
            "requires_human_review"
        ),
        "may_generate_answer": governance.get(
            "may_generate_answer"
        ),
        "document_ids": governance.get(
            "document_ids",
            [],
        ),
        "retrieval_route": governance.get(
            "retrieval_route"
        ),
        "retrieval_stop_reason": governance.get(
            "retrieval_stop_reason"
        ),
    }


def build_evidence_packet(
    question: str,
    retrieval_output: dict,
) -> dict:
    """Build one deterministic Evidence Packet.

    Existing Architecture v2 retrieval and governance decisions
    remain authoritative.

    The packet only organises those outputs into one auditable
    structure.
    """

    question = _require_non_empty_string(
        question,
        "question",
    )

    if not isinstance(
        retrieval_output,
        dict,
    ):
        raise TypeError(
            "retrieval_output must be a dictionary"
        )

    audit = retrieval_output.get(
        "audit"
    )

    if not isinstance(
        audit,
        dict,
    ):
        raise ValueError(
            "retrieval_output must contain an audit dictionary"
        )

    results = retrieval_output.get(
        "results"
    )

    if not isinstance(
        results,
        list,
    ):
        raise ValueError(
            "retrieval_output must contain a results list"
        )

    scope = audit.get(
        "scope"
    )

    if not isinstance(
        scope,
        dict,
    ):
        raise ValueError(
            "retrieval audit must contain a scope dictionary"
        )

    route = audit.get(
        "selected_route"
    )

    route = _require_non_empty_string(
        route,
        "selected_route",
    )

    stop_reason = audit.get(
        "stop_reason"
    )

    if stop_reason is not None:
        stop_reason = _require_non_empty_string(
            stop_reason,
            "stop_reason",
        )

    final_evidence = audit.get(
        "final_evidence"
    )

    governance = (
        decide_retrieval_governance_outcome(
            question=question,
            retrieval_output=retrieval_output,
        )
    )

    # Out-of-scope questions legitimately contain no usable evidence.
    if scope.get(
        "allowed"
    ) is not True:
        evidence_objects = []

    # Valid in-scope retrieval must retain the Day 1 fail-closed
    # evidence conversion behaviour.
    else:
        if not isinstance(
            final_evidence,
            dict,
        ):
            evidence_objects = []

        elif final_evidence.get(
            "sufficient"
        ) is True:
            evidence_objects = (
                build_evidence_from_retrieval(
                    retrieval_output
                )
            )

        else:
            evidence_objects = []

    grouped_evidence = (
        _group_evidence_by_role(
            evidence_objects
        )
    )

    document_ids = (
        _unique_document_ids(
            evidence_objects
        )
    )

    lifecycle_summary = (
        _build_lifecycle_summary(
            evidence_objects
        )
    )

    packet = {
        "packet_id": (
            _build_packet_id(
                question
            )
        ),
        "question": question,
        "retrieval": {
            "route": route,
            "stop_reason": stop_reason,
            "scope": scope,
        },
        "evidence_sufficiency": (
            _compact_evidence_sufficiency(
                final_evidence
            )
        ),
        "evidence": grouped_evidence,
        "evidence_count": len(
            evidence_objects
        ),
        "document_ids": document_ids,
        "missing_evidence": (
            _build_missing_evidence(
                audit,
                final_evidence,
            )
        ),
        "lifecycle_summary": (
            lifecycle_summary
        ),
        "governance": (
            _compact_governance(
                governance
            )
        ),
        "audit_summary": {
            "initial_retrieval_call_count": (
                audit.get(
                    "initial_retrieval_call_count"
                )
            ),
            "total_hybrid_retrieval_calls": (
                audit.get(
                    "total_hybrid_retrieval_calls"
                )
            ),
            "selected_route": route,
            "stop_reason": stop_reason,
        },
    }

    return packet