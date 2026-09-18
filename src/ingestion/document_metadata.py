from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentMetadata:
    """
    Canonical document-level metadata used during ingestion.

    Chunk-level fields such as page, section, chunk_number and
    chunk_id are added later in the preprocessing pipeline.
    """

    document_id: str
    title: str
    document_type: str
    source_type: str
    source_location: str
    version: str
    effective_date: str
    status: str


DOCUMENT_REGISTER: dict[str, DocumentMetadata] = {
    "DOC-001": DocumentMetadata(
        document_id="DOC-001",
        title="Operational Escalation Policy",
        document_type="Policy",
        source_type="Synthetic",
        source_location=(
            "data/raw/"
            "DOC-001_operational_escalation_policy.pdf"
        ),
        version="1.0",
        effective_date="2026-01-01",
        status="Active",
    ),

    "DOC-002": DocumentMetadata(
        document_id="DOC-002",
        title="Winter Pressure Plan",
        document_type="Operational Plan",
        source_type="Synthetic",
        source_location=(
            "data/raw/"
            "DOC-002_winter_pressure_plan.pdf"
        ),
        version="1.0",
        effective_date="2026-01-01",
        status="Active",
    ),

    "DOC-003": DocumentMetadata(
        document_id="DOC-003",
        title="Workforce Escalation Procedure",
        document_type="Procedure",
        source_type="Synthetic",
        source_location=(
            "data/raw/"
            "DOC-003_workforce_escalation_procedure.pdf"
        ),
        version="1.0",
        effective_date="2026-01-01",
        status="Active",
    ),

    "DOC-004": DocumentMetadata(
        document_id="DOC-004",
        title="Bed Capacity Management Procedure",
        document_type="Procedure",
        source_type="Synthetic",
        source_location=(
            "data/raw/"
            "DOC-004_bed_capacity_management_procedure.pdf"
        ),
        version="1.0",
        effective_date="2026-01-01",
        status="Active",
    ),

    "DOC-005": DocumentMetadata(
        document_id="DOC-005",
        title="Business Continuity Procedure",
        document_type="Procedure",
        source_type="Synthetic",
        source_location=(
            "data/raw/"
            "DOC-005_business_continuity_procedure.pdf"
        ),
        version="1.0",
        effective_date="2026-01-01",
        status="Active",
    ),

    "DOC-006": DocumentMetadata(
        document_id="DOC-006",
        title="Operational Governance Standard",
        document_type="Governance Standard",
        source_type="Synthetic",
        source_location=(
            "data/raw/"
            "DOC-006_operational_governance_standard.pdf"
        ),
        version="1.0",
        effective_date="2026-01-01",
        status="Active",
    ),

    # ---------------------------------------------------------
    # WEEK 18 RETRIEVAL-STRESS CORPUS
    # ---------------------------------------------------------

    "DOC-007": DocumentMetadata(
        document_id="DOC-007",
        title="Emergency Department Escalation Procedure",
        document_type="Procedure",
        source_type="Synthetic",
        source_location=(
            "data/raw/"
            "DOC-007_emergency_department_escalation_procedure.pdf"
        ),
        version="1.0",
        effective_date="2026-01-01",
        status="Active",
    ),

    "DOC-008": DocumentMetadata(
        document_id="DOC-008",
        title="Ambulance Handover Escalation Guidance",
        document_type="Operational Guidance",
        source_type="Synthetic",
        source_location=(
            "data/raw/"
            "DOC-008_ambulance_handover_escalation_guidance.pdf"
        ),
        version="1.0",
        effective_date="2026-01-01",
        status="Active",
    ),

    "DOC-009": DocumentMetadata(
        document_id="DOC-009",
        title="Severe Weather Operational Plan",
        document_type="Operational Plan",
        source_type="Synthetic",
        source_location=(
            "data/raw/"
            "DOC-009_severe_weather_operational_plan.pdf"
        ),
        version="1.0",
        effective_date="2026-01-01",
        status="Active",
    ),

    "DOC-010": DocumentMetadata(
        document_id="DOC-010",
        title="Infection Surge Operational Response Plan",
        document_type="Operational Plan",
        source_type="Synthetic",
        source_location=(
            "data/raw/"
            "DOC-010_infection_surge_operational_response_plan.pdf"
        ),
        version="1.0",
        effective_date="2026-01-01",
        status="Active",
    ),

    "DOC-011": DocumentMetadata(
        document_id="DOC-011",
        title="Critical Staffing Contingency Procedure",
        document_type="Procedure",
        source_type="Synthetic",
        source_location=(
            "data/raw/"
            "DOC-011_critical_staffing_contingency_procedure.pdf"
        ),
        version="1.0",
        effective_date="2026-01-01",
        status="Active",
    ),

    "DOC-012": DocumentMetadata(
        document_id="DOC-012",
        title="Site Flow Coordination Procedure",
        document_type="Procedure",
        source_type="Synthetic",
        source_location=(
            "data/raw/"
            "DOC-012_site_flow_coordination_procedure.pdf"
        ),
        version="1.0",
        effective_date="2026-01-01",
        status="Active",
    ),

    "DOC-013": DocumentMetadata(
        document_id="DOC-013",
        title="Operational Pressure Coordination Guidance",
        document_type="Operational Guidance",
        source_type="Synthetic",
        source_location=(
            "data/raw/"
            "DOC-013_operational_pressure_coordination_guidance.txt"
        ),
        version="1.0",
        effective_date="2026-01-01",
        status="Active",
    ),

    "DOC-014": DocumentMetadata(
        document_id="DOC-014",
        title="Draft Emergency Pressure Framework",
        document_type="Draft Framework",
        source_type="Synthetic",
        source_location=(
            "data/raw/"
            "DOC-014_draft_emergency_pressure_framework.txt"
        ),
        version="0.1",
        effective_date="2026-06-01",
        status="Draft",
    ),
}


def validate_document_id(
    document_id: str,
) -> None:
    """
    Validate the basic document identifier.
    """

    if not isinstance(document_id, str):
        raise TypeError(
            "document_id must be a string"
        )

    if not document_id.strip():
        raise ValueError(
            "document_id must not be blank"
        )


def validate_document_metadata(
    metadata: DocumentMetadata,
) -> None:
    """
    Validate canonical document-level metadata.
    """

    if not isinstance(
        metadata,
        DocumentMetadata,
    ):
        raise TypeError(
            "metadata must be DocumentMetadata"
        )

    required_values = {
        "document_id": metadata.document_id,
        "title": metadata.title,
        "document_type": metadata.document_type,
        "source_type": metadata.source_type,
        "source_location": metadata.source_location,
        "version": metadata.version,
        "effective_date": metadata.effective_date,
        "status": metadata.status,
    }

    for field_name, value in required_values.items():
        if (
            not isinstance(value, str)
            or not value.strip()
        ):
            raise ValueError(
                f"{field_name} must be a non-empty string"
            )

    allowed_statuses = {
        "Active",
        "Superseded",
        "Draft",
        "Archived",
    }

    if metadata.status not in allowed_statuses:
        raise ValueError(
            "status must be one of: "
            "Active, Superseded, Draft, Archived"
        )


def get_document_metadata(
    document_id: str,
) -> DocumentMetadata:
    """
    Retrieve canonical metadata for a registered document.
    """

    validate_document_id(
        document_id
    )

    normalised_document_id = (
        document_id.strip().upper()
    )

    try:
        metadata = DOCUMENT_REGISTER[
            normalised_document_id
        ]

    except KeyError as exc:
        raise KeyError(
            "No metadata found for "
            f"document_id {normalised_document_id!r}."
        ) from exc

    validate_document_metadata(
        metadata
    )

    return metadata


def is_document_registered(
    document_id: str,
) -> bool:
    """
    Return True when the document exists in the register.
    """

    if (
        not isinstance(document_id, str)
        or not document_id.strip()
    ):
        return False

    return (
        document_id.strip().upper()
        in DOCUMENT_REGISTER
    )


def list_registered_documents(
) -> list[DocumentMetadata]:
    """
    Return all registered documents.
    """

    return list(
        DOCUMENT_REGISTER.values()
    )


def get_documents_by_status(
    status: str,
) -> list[DocumentMetadata]:
    """
    Return registered documents matching a lifecycle status.
    """

    if (
        not isinstance(status, str)
        or not status.strip()
    ):
        raise ValueError(
            "status must be a non-empty string"
        )

    target_status = status.strip()

    return [
        metadata
        for metadata
        in DOCUMENT_REGISTER.values()
        if metadata.status
        == target_status
    ]


def is_document_retrieval_eligible(
    document_id: str,
) -> bool:
    """
    Normal retrieval currently permits Active documents only.

    Draft, Superseded and Archived documents remain registered
    for governance/audit purposes but are not approved evidence.
    """

    metadata = get_document_metadata(
        document_id
    )

    return (
        metadata.status
        == "Active"
    )

  
