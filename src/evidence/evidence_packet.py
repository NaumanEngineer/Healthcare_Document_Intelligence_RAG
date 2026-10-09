"""Question-level Evidence Packet.

Week 22 Day 2 + Day 3 provenance integration.

The Evidence Packet organizes retrieval output, structured evidence,
provenance, evidence sufficiency, lifecycle state, governance and
audit information into one deterministic object.

It does not create facts, generate claims, alter retrieval decisions,
or replace governance.
"""

from __future__ import annotations

import hashlib

from src.evidence.evidence_from_retrieval import (
    build_evidence_from_retrieval,
)
from src.evidence.provenance import (
    TRACEABILITY_MISMATCH,
    TRACEABILITY_UNREGISTERED,
    TRACEABILITY_VERIFIED,
    build_provenance_records,
)
from src.governance.retrieval_review_integration import (
    decide_retrieval_governance_outcome,
)


def _require_non_empty_string(
    value,
    field_name: str,
) -> str:
    """Require a non-empty string."""

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
    """Build a deterministic packet identifier."""

    digest = hashlib.sha256(
        question.encode("utf-8")
    ).hexdigest()[:16]

    return (
        f"EVIDENCE_PACKET::{digest}"
    )


def _unique_document_ids(
    evidence_objects: list[dict],
) -> list[str]:
    """Return document IDs in first-seen order."""

    document_ids = []

    seen = set()

    for evidence in evidence_objects:
        document_id = evidence.get(
            "document_id"
        )

        if (
            isinstance(document_id, str)
            and document_id
            and document_id not in seen
        ):
            seen.add(
                document_id
            )

            document_ids.append(
                document_id
            )

    return document_ids


def _group_evidence_by_role(
    evidence_objects: list[dict],
) -> dict:
    """Group evidence using the supported evidence roles."""

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
                "Unsupported evidence role in packet: "
                f"{role!r}"
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
    """Summarize lifecycle status across packet evidence."""

    status_counts = {}

    for evidence in evidence_objects:
        status = evidence.get(
            "status"
        )

        if not isinstance(
            status,
            str,
        ):
            continue

        status_counts[
            status
        ] = (
            status_counts.get(
                status,
                0,
            )
            + 1
        )

    all_active = (
        bool(evidence_objects)
        and all(
            evidence.get(
                "status"
            )
            == "Active"
            for evidence in evidence_objects
        )
    )

    return {
        "status_counts": status_counts,
        "all_active": all_active,
    }


def _build_provenance_summary(
    provenance_records: list[dict],
) -> dict:
    """Summarize provenance verification across packet evidence."""

    status_counts = {
        TRACEABILITY_VERIFIED: 0,
        TRACEABILITY_MISMATCH: 0,
        TRACEABILITY_UNREGISTERED: 0,
    }

    mismatch_evidence_ids = []

    unregistered_evidence_ids = []

    for record in provenance_records:
        if not isinstance(
            record,
            dict,
        ):
            raise TypeError(
                "provenance record must be a dictionary"
            )

        traceability = record.get(
            "traceability"
        )

        if not isinstance(
            traceability,
            dict,
        ):
            raise ValueError(
                "provenance record must contain "
                "traceability dictionary"
            )

        status = traceability.get(
            "traceability_status"
        )

        if status not in status_counts:
            raise ValueError(
                "Unsupported traceability status: "
                f"{status!r}"
            )

        status_counts[
            status
        ] += 1

        evidence_id = record.get(
            "evidence_id"
        )

        if status == TRACEABILITY_MISMATCH:
            mismatch_evidence_ids.append(
                evidence_id
            )

        if status == TRACEABILITY_UNREGISTERED:
            unregistered_evidence_ids.append(
                evidence_id
            )

    record_count = len(
        provenance_records
    )

    verified_count = status_counts[
        TRACEABILITY_VERIFIED
    ]

    all_verified = (
        record_count > 0
        and verified_count == record_count
    )

    return {
        "record_count": record_count,
        "status_counts": status_counts,
        "all_verified": all_verified,
        "mismatch_evidence_ids": (
            mismatch_evidence_ids
        ),
        "unregistered_evidence_ids": (
            unregistered_evidence_ids
        ),
    }


def _compact_evidence_sufficiency(
    final_evidence: dict | None,
) -> dict | None:
    """Return the useful final evidence-sufficiency fields."""

    if not isinstance(
        final_evidence,
        dict,
    ):
        return None

    fields = (
        "sufficient",
        "decision",
        "reason",
        "matched_query_terms",
        "evidence_terms",
        "result_count",
        "topic_sufficient",
        "claim_sufficient",
        "claim_requirements",
        "unsupported_claims",
    )

    return {
        field: final_evidence.get(
            field
        )
        for field in fields
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
    """Return the packet-level governance fields."""

    fields = (
        "decision",
        "reason",
        "requires_human_review",
        "may_generate_answer",
        "document_ids",
        "retrieval_route",
        "retrieval_stop_reason",
    )

    return {
        field: governance.get(
            field
        )
        for field in fields
    }


def build_evidence_packet(
    question: str,
    retrieval_output: dict,
) -> dict:
    """Build one deterministic question-level Evidence Packet."""

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
            "retrieval_output must contain audit dictionary"
        )

    results = retrieval_output.get(
        "results"
    )

    if not isinstance(
        results,
        list,
    ):
        raise ValueError(
            "retrieval_output must contain results list"
        )

    scope = audit.get(
        "scope"
    )

    if not isinstance(
        scope,
        dict,
    ):
        raise ValueError(
            "retrieval audit must contain scope dictionary"
        )

    selected_route = _require_non_empty_string(
        audit.get(
            "selected_route"
        ),
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
            question,
            retrieval_output,
        )
    )

    scope_allowed = (
        scope.get(
            "allowed"
        )
        is True
    )

    final_sufficient = (
        isinstance(
            final_evidence,
            dict,
        )
        and final_evidence.get(
            "sufficient"
        )
        is True
    )

    if (
        scope_allowed
        and final_sufficient
    ):
        evidence_objects = (
            build_evidence_from_retrieval(
                retrieval_output
            )
        )
    else:
        evidence_objects = []

    provenance_records = (
        build_provenance_records(
            evidence_objects
        )
    )

    provenance_summary = (
        _build_provenance_summary(
            provenance_records
        )
    )

    document_ids = (
        _unique_document_ids(
            evidence_objects
        )
    )

    return {
        "packet_id": _build_packet_id(
            question
        ),
        "question": question,
        "retrieval": {
            "route": selected_route,
            "stop_reason": stop_reason,
            "scope": scope,
        },
        "evidence_sufficiency": (
            _compact_evidence_sufficiency(
                final_evidence
            )
        ),
        "evidence": (
            _group_evidence_by_role(
                evidence_objects
            )
        ),
        "evidence_count": len(
            evidence_objects
        ),
        "document_ids": document_ids,
        "provenance": provenance_records,
        "provenance_summary": (
            provenance_summary
        ),
        "missing_evidence": (
            _build_missing_evidence(
                audit,
                final_evidence,
            )
        ),
        "lifecycle_summary": (
            _build_lifecycle_summary(
                evidence_objects
            )
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
            "selected_route": selected_route,
            "stop_reason": stop_reason,
        },
    }