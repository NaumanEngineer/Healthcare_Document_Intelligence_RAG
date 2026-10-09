"""Question-level Evidence Packet builder.

Week 22.

The Evidence Packet brings together:

- retrieval outcome;
- evidence sufficiency;
- structured evidence objects;
- provenance;
- provenance summary;
- lifecycle information;
- conflict / supersession / precedence assessment;
- governance outcome;
- retrieval audit information.

The packet does not create new facts.

It does not override retrieval, evidence sufficiency or governance.

Existing governance remains authoritative.
"""

from __future__ import annotations

import hashlib
from typing import Any

from src.evidence.evidence_from_retrieval import (
    build_evidence_from_retrieval,
)
from src.evidence.evidence_precedence import (
    assess_evidence_precedence,
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


SUPPORTED_EVIDENCE_ROLES = (
    "supporting",
    "relationship_evidence",
    "context",
)


def _require_mapping(
    value: Any,
    field_name: str,
) -> dict:
    """Require a dictionary value."""

    if not isinstance(
        value,
        dict,
    ):
        raise TypeError(
            f"{field_name} must be a dictionary"
        )

    return value


def _require_list(
    value: Any,
    field_name: str,
) -> list:
    """Require a list value."""

    if not isinstance(
        value,
        list,
    ):
        raise TypeError(
            f"{field_name} must be a list"
        )

    return value


def _build_packet_id(
    question: str,
) -> str:
    """Build deterministic packet identifier."""

    if not isinstance(
        question,
        str,
    ):
        raise TypeError(
            "question must be a string"
        )

    cleaned = question.strip()

    if not cleaned:
        raise ValueError(
            "question must not be blank"
        )

    digest = hashlib.sha256(
        cleaned.encode(
            "utf-8"
        )
    ).hexdigest()[:16]

    return (
        f"EVIDENCE_PACKET::{digest}"
    )


def _group_evidence(
    evidence_objects: list[dict],
) -> dict:
    """Group evidence objects by evidence role."""

    grouped = {
        "supporting": [],
        "relationship_evidence": [],
        "context": [],
    }

    for evidence in evidence_objects:
        if not isinstance(
            evidence,
            dict,
        ):
            raise TypeError(
                "each evidence object must be a dictionary"
            )

        role = evidence.get(
            "evidence_role"
        )

        if role not in SUPPORTED_EVIDENCE_ROLES:
            raise ValueError(
                "Unsupported evidence role: "
                f"{role}"
            )

        grouped[
            role
        ].append(
            evidence
        )

    return grouped


def _document_ids(
    evidence_objects: list[dict],
) -> list[str]:
    """Return distinct evidence document IDs in first-seen order."""

    document_ids = []

    seen = set()

    for evidence in evidence_objects:
        document_id = evidence.get(
            "document_id"
        )

        if (
            not isinstance(
                document_id,
                str,
            )
            or not document_id.strip()
        ):
            raise ValueError(
                "Evidence document_id must be "
                "a non-empty string"
            )

        document_id = (
            document_id.strip()
        )

        if document_id not in seen:
            seen.add(
                document_id
            )

            document_ids.append(
                document_id
            )

    return document_ids


def _build_lifecycle_summary(
    evidence_objects: list[dict],
) -> dict:
    """Summarize lifecycle states across evidence objects."""

    status_counts: dict[
        str,
        int,
    ] = {}

    for evidence in evidence_objects:
        status = evidence.get(
            "status"
        )

        if (
            not isinstance(
                status,
                str,
            )
            or not status.strip()
        ):
            raise ValueError(
                "Evidence status must be "
                "a non-empty string"
            )

        status = status.strip()

        status_counts[
            status
        ] = (
            status_counts.get(
                status,
                0,
            )
            + 1
        )

    all_active = bool(
        evidence_objects
    ) and all(
        evidence.get(
            "status"
        )
        == "Active"
        for evidence
        in evidence_objects
    )

    return {
        "status_counts": (
            status_counts
        ),
        "all_active": (
            all_active
        ),
    }


def _build_provenance_summary(
    provenance_records: list[dict],
) -> dict:
    """Summarize provenance verification results."""

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
                "each provenance record must "
                "be a dictionary"
            )

        traceability = record.get(
            "traceability"
        )

        if not isinstance(
            traceability,
            dict,
        ):
            raise TypeError(
                "provenance traceability must "
                "be a dictionary"
            )

        traceability_status = (
            traceability.get(
                "traceability_status"
            )
        )

        if (
            traceability_status
            not in status_counts
        ):
            raise ValueError(
                "Unsupported traceability status: "
                f"{traceability_status}"
            )

        status_counts[
            traceability_status
        ] += 1

        evidence_id = record.get(
            "evidence_id"
        )

        if (
            traceability_status
            == TRACEABILITY_MISMATCH
        ):
            mismatch_evidence_ids.append(
                evidence_id
            )

        if (
            traceability_status
            == TRACEABILITY_UNREGISTERED
        ):
            unregistered_evidence_ids.append(
                evidence_id
            )

    record_count = len(
        provenance_records
    )

    verified_count = (
        status_counts[
            TRACEABILITY_VERIFIED
        ]
    )

    all_verified = (
        record_count > 0
        and verified_count
        == record_count
    )

    return {
        "record_count": (
            record_count
        ),
        "status_counts": (
            status_counts
        ),
        "all_verified": (
            all_verified
        ),
        "mismatch_evidence_ids": (
            mismatch_evidence_ids
        ),
        "unregistered_evidence_ids": (
            unregistered_evidence_ids
        ),
    }


def _extract_retrieval_metadata(
    retrieval_output: dict,
) -> dict:
    """Extract route, stop reason and scope."""

    audit = retrieval_output.get(
        "audit",
        {},
    )

    if audit is None:
        audit = {}

    audit = _require_mapping(
        audit,
        "retrieval_output.audit",
    )

    route = (
        audit.get(
            "selected_route"
        )
        or retrieval_output.get(
            "selected_route"
        )
    )

    stop_reason = (
        audit.get(
            "stop_reason"
        )
        or retrieval_output.get(
            "stop_reason"
        )
    )

    scope = (
        retrieval_output.get(
            "scope"
        )
        or audit.get(
            "scope"
        )
        or {}
    )

    if not isinstance(
        scope,
        dict,
    ):
        raise TypeError(
            "retrieval scope must be a dictionary"
        )

    return {
        "route": route,
        "stop_reason": (
            stop_reason
        ),
        "scope": scope,
    }


def _extract_final_evidence(
    retrieval_output: dict,
) -> dict:
    """Return the final evidence-sufficiency assessment.

    Out-of-scope retrieval may legitimately have no final evidence.
    In that case an empty dictionary is returned.
    """

    audit = retrieval_output.get(
        "audit",
        {},
    )

    if audit is None:
        audit = {}

    audit = _require_mapping(
        audit,
        "retrieval_output.audit",
    )

    final_evidence = audit.get(
        "final_evidence"
    )

    if final_evidence is None:
        final_evidence = retrieval_output.get(
            "final_evidence"
        )

    if final_evidence is None:
        return {}

    if not isinstance(
        final_evidence,
        dict,
    ):
        raise TypeError(
            "final_evidence must be a dictionary"
        )

    return final_evidence


def _extract_missing_evidence(
    retrieval_output: dict,
    final_evidence: dict,
) -> dict:
    """Separate initial diagnosis from final unresolved evidence gaps."""

    audit = retrieval_output.get(
        "audit",
        {},
    )

    if audit is None:
        audit = {}

    audit = _require_mapping(
        audit,
        "retrieval_output.audit",
    )

    routing_decision = (
        audit.get(
            "routing_decision"
        )
        or retrieval_output.get(
            "routing_decision"
        )
        or {}
    )

    if not isinstance(
        routing_decision,
        dict,
    ):
        raise TypeError(
            "routing_decision must be a dictionary"
        )

    initial_missing_topics = (
        routing_decision.get(
            "missing_topics",
            [],
        )
    )

    if not isinstance(
        initial_missing_topics,
        list,
    ):
        raise TypeError(
            "routing_decision.missing_topics "
            "must be a list"
        )

    if (
        final_evidence.get(
            "sufficient"
        )
        is True
    ):
        final_missing_topics = []

    else:
        final_missing_topics = (
            final_evidence.get(
                "missing_topics",
                initial_missing_topics,
            )
        )

        if not isinstance(
            final_missing_topics,
            list,
        ):
            raise TypeError(
                "final missing_topics must be a list"
            )

    unsupported_claims = (
        final_evidence.get(
            "unsupported_claims",
            [],
        )
    )

    if not isinstance(
        unsupported_claims,
        list,
    ):
        raise TypeError(
            "unsupported_claims must be a list"
        )

    return {
        "initial_missing_topics": (
            initial_missing_topics
        ),
        "final_missing_topics": (
            final_missing_topics
        ),
        "unsupported_claims": (
            unsupported_claims
        ),
    }


def _build_audit_summary(
    retrieval_output: dict,
    retrieval_metadata: dict,
) -> dict:
    """Build compact retrieval audit summary."""

    audit = retrieval_output.get(
        "audit",
        {},
    )

    if audit is None:
        audit = {}

    audit = _require_mapping(
        audit,
        "retrieval_output.audit",
    )

    initial_retrieval_call_count = (
        audit.get(
            "initial_retrieval_call_count",
            1,
        )
    )

    total_hybrid_retrieval_calls = (
        audit.get(
            "total_hybrid_retrieval_calls"
        )
    )

    if (
        total_hybrid_retrieval_calls
        is None
    ):
        total_hybrid_retrieval_calls = (
            audit.get(
                "hybrid_retrieval_call_count",
                initial_retrieval_call_count,
            )
        )

    return {
        "initial_retrieval_call_count": (
            initial_retrieval_call_count
        ),
        "total_hybrid_retrieval_calls": (
            total_hybrid_retrieval_calls
        ),
        "selected_route": (
            retrieval_metadata[
                "route"
            ]
        ),
        "stop_reason": (
            retrieval_metadata[
                "stop_reason"
            ]
        ),
    }


def build_evidence_packet(
    question: str,
    retrieval_output: dict,
) -> dict:
    """Build one structured question-level Evidence Packet.

    Safety sequence:

    Question
    -> Scope Gate
    -> Evidence Sufficiency
    -> Structured Evidence
    -> Provenance
    -> Precedence Assessment
    -> Governance

    The packet does not grant permission to answer.
    """

    if not isinstance(
        question,
        str,
    ):
        raise TypeError(
            "question must be a string"
        )

    question = question.strip()

    if not question:
        raise ValueError(
            "question must not be blank"
        )

    retrieval_output = (
        _require_mapping(
            retrieval_output,
            "retrieval_output",
        )
    )

    packet_id = (
        _build_packet_id(
            question
        )
    )

    retrieval_metadata = (
        _extract_retrieval_metadata(
            retrieval_output
        )
    )

    final_evidence = (
        _extract_final_evidence(
            retrieval_output
        )
    )

    scope_allowed = (
        retrieval_metadata[
            "scope"
        ].get(
            "allowed"
        )
    )

    if (
        scope_allowed is True
        and final_evidence.get(
            "sufficient"
        )
        is True
    ):
        evidence_objects = (
            build_evidence_from_retrieval(
                retrieval_output
            )
        )

    else:
        evidence_objects = []

    _require_list(
        evidence_objects,
        "evidence_objects",
    )

    grouped_evidence = (
        _group_evidence(
            evidence_objects
        )
    )

    document_ids = (
        _document_ids(
            evidence_objects
        )
    )

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

    lifecycle_summary = (
        _build_lifecycle_summary(
            evidence_objects
        )
    )

    precedence_assessment = (
        assess_evidence_precedence(
            evidence_objects
        )
    )

    governance = (
        decide_retrieval_governance_outcome(
            question,
            retrieval_output,
        )
    )

    missing_evidence = (
        _extract_missing_evidence(
            retrieval_output,
            final_evidence,
        )
    )

    audit_summary = (
        _build_audit_summary(
            retrieval_output,
            retrieval_metadata,
        )
    )

    return {
        "packet_id": packet_id,
        "question": question,
        "retrieval": (
            retrieval_metadata
        ),
        "evidence_sufficiency": (
            final_evidence
        ),
        "evidence": (
            grouped_evidence
        ),
        "evidence_count": len(
            evidence_objects
        ),
        "document_ids": (
            document_ids
        ),
        "provenance": (
            provenance_records
        ),
        "provenance_summary": (
            provenance_summary
        ),
        "precedence_assessment": (
            precedence_assessment
        ),
        "missing_evidence": (
            missing_evidence
        ),
        "lifecycle_summary": (
            lifecycle_summary
        ),
        "governance": (
            governance
        ),
        "audit_summary": (
            audit_summary
        ),
    }