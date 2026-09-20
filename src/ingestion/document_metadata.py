from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import PureWindowsPath
from uuid import uuid4


VALID_DOCUMENT_STATUSES = {
    "Active",
    "Superseded",
    "Draft",
    "Archived",
}


@dataclass(frozen=True)
class DocumentMetadata:
    """
    Canonical document-level metadata.

    Page-level and chunk-level metadata are added later in the
    ingestion and preprocessing pipeline.
    """

    document_id: str
    title: str
    document_type: str
    source_type: str
    source_location: str
    version: str
    effective_date: str
    status: str
    source_file: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.status, str) or self.status not in VALID_DOCUMENT_STATUSES:
            raise ValueError(f"Unsupported document status: {self.status!r}")
        if self.source_file is None:
            if not isinstance(self.source_location, str) or not self.source_location.strip():
                raise ValueError("source_location must be a non-empty string")
            object.__setattr__(self, "source_file", PureWindowsPath(self.source_location).name)
        if not isinstance(self.source_file, str) or not self.source_file.strip():
            raise ValueError("source_file must be a non-empty string")

    def to_dict(self) -> dict:
        return asdict(self)


def create_ingestion_batch_id() -> str:
    """Create one traceable identifier for an ingestion run."""
    return str(uuid4())


def is_active_document(metadata: DocumentMetadata) -> bool:
    """Compatibility helper for callers holding a metadata record."""
    return metadata.status == "Active"


def enrich_page_record(page_record: dict, metadata: DocumentMetadata) -> dict:
    """Attach canonical metadata without changing or overwriting provenance."""
    validate_document_metadata(metadata)
    if not isinstance(page_record, dict):
        raise TypeError("page_record must be a dictionary")
    for field in ("document_id", "source_file"):
        if page_record.get(field) != getattr(metadata, field):
            raise ValueError(f"Page {field} does not match document metadata")
    fields = metadata.to_dict()
    for field, value in fields.items():
        if field in page_record and page_record[field] != value:
            raise ValueError(f"Page {field} conflicts with document metadata")
    return {**fields, **page_record}


def validate_document_status(
    status: str,
) -> None:
    """
    Validate a document lifecycle status.

    Supported lifecycle states:

    - Active
    - Superseded
    - Draft
    - Archived
    """

    if not isinstance(status, str):
        raise TypeError(
            "status must be a string"
        )

    if not status.strip():
        raise ValueError(
            "status must not be blank"
        )

    if status not in VALID_DOCUMENT_STATUSES:
        raise ValueError(
            "status must be one of: "
            "Active, Superseded, Draft, Archived"
        )


def validate_document_id(
    document_id: str,
) -> None:
    """
    Validate the basic document identifier.
    """

    if not isinstance(
        document_id,
        str,
    ):
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
    Validate one canonical metadata record.
    """

    if not isinstance(
        metadata,
        DocumentMetadata,
    ):
        raise TypeError(
            "metadata must be DocumentMetadata"
        )

    required_fields = {
        "document_id": metadata.document_id,
        "title": metadata.title,
        "document_type": metadata.document_type,
        "source_type": metadata.source_type,
        "source_location": metadata.source_location,
        "source_file": metadata.source_file,
        "version": metadata.version,
        "effective_date": metadata.effective_date,
        "status": metadata.status,
    }

    for field_name, value in required_fields.items():
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{field_name} must be a string"
            )

        if not value.strip():
            raise ValueError(
                f"{field_name} must not be blank"
            )

    validate_document_id(
        metadata.document_id
    )

    validate_document_status(
        metadata.status
    )


def build_document_register(
    documents: list[DocumentMetadata] | None = None,
) -> dict[str, DocumentMetadata]:
    """
    Build the canonical synthetic document register.

    The register deliberately contains lifecycle metadata so
    retrieval can distinguish approved Active documents from
    Draft, Superseded and Archived material.
    """

    if documents is not None:
        register = {}
        for metadata in documents:
            validate_document_metadata(metadata)
            if metadata.document_id in register:
                raise ValueError(f"Duplicate document_id: {metadata.document_id}")
            register[metadata.document_id] = metadata
        return register

    return {
        # -----------------------------------------------------
        # WEEK 17 CORE CORPUS
        # -----------------------------------------------------

        "DOC-001": DocumentMetadata(
            document_id="DOC-001",
            title=(
                "Operational Escalation Policy"
            ),
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
            title=(
                "Workforce Escalation Procedure"
            ),
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
            title=(
                "Bed Capacity Management Procedure"
            ),
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
            title=(
                "Business Continuity Procedure"
            ),
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
            title=(
                "Operational Governance Standard"
            ),
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

        # -----------------------------------------------------
        # WEEK 18 RETRIEVAL-STRESS CORPUS
        # -----------------------------------------------------

        "DOC-007": DocumentMetadata(
            document_id="DOC-007",
            title=(
                "Emergency Department Escalation Procedure"
            ),
            document_type="Procedure",
            source_type="Synthetic",
            source_location=(
                "data/raw/"
                "DOC-007_emergency_department_"
                "escalation_procedure.pdf"
            ),
            version="1.0",
            effective_date="2026-01-01",
            status="Active",
        ),

        "DOC-008": DocumentMetadata(
            document_id="DOC-008",
            title=(
                "Ambulance Handover Escalation Guidance"
            ),
            document_type="Operational Guidance",
            source_type="Synthetic",
            source_location=(
                "data/raw/"
                "DOC-008_ambulance_handover_"
                "escalation_guidance.pdf"
            ),
            version="1.0",
            effective_date="2026-01-01",
            status="Active",
        ),

        "DOC-009": DocumentMetadata(
            document_id="DOC-009",
            title=(
                "Severe Weather Operational Plan"
            ),
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
            title=(
                "Infection Surge Operational Response Plan"
            ),
            document_type="Operational Plan",
            source_type="Synthetic",
            source_location=(
                "data/raw/"
                "DOC-010_infection_surge_operational_"
                "response_plan.pdf"
            ),
            version="1.0",
            effective_date="2026-01-01",
            status="Active",
        ),

        "DOC-011": DocumentMetadata(
            document_id="DOC-011",
            title=(
                "Critical Staffing Contingency Procedure"
            ),
            document_type="Procedure",
            source_type="Synthetic",
            source_location=(
                "data/raw/"
                "DOC-011_critical_staffing_"
                "contingency_procedure.pdf"
            ),
            version="1.0",
            effective_date="2026-01-01",
            status="Active",
        ),

        "DOC-012": DocumentMetadata(
            document_id="DOC-012",
            title=(
                "Site Flow Coordination Procedure"
            ),
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
            title=(
                "Operational Pressure Coordination Guidance"
            ),
            document_type="Operational Guidance",
            source_type="Synthetic",
            source_location=(
                "data/raw/"
                "DOC-013_operational_pressure_"
                "coordination_guidance.txt"
            ),
            version="1.0",
            effective_date="2026-01-01",
            status="Active",
        ),

        "DOC-014": DocumentMetadata(
            document_id="DOC-014",
            title=(
                "Draft Emergency Pressure Framework"
            ),
            document_type="Draft Framework",
            source_type="Synthetic",
            source_location=(
                "data/raw/"
                "DOC-014_draft_emergency_"
                "pressure_framework.txt"
            ),
            version="0.1",
            effective_date="2026-06-01",
            status="Draft",
        ),
    }


DOCUMENT_REGISTER = build_document_register()


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
    Return True when a document ID is present in the register.
    """

    if not isinstance(
        document_id,
        str,
    ):
        return False

    if not document_id.strip():
        return False

    return (
        document_id.strip().upper()
        in DOCUMENT_REGISTER
    )


def list_registered_documents(
) -> list[DocumentMetadata]:
    """
    Return every registered metadata record.
    """

    return list(
        DOCUMENT_REGISTER.values()
    )


def get_documents_by_status(
    status: str,
) -> list[DocumentMetadata]:
    """
    Return documents with the requested lifecycle status.
    """

    validate_document_status(
        status
    )

    return [
        metadata
        for metadata
        in DOCUMENT_REGISTER.values()
        if metadata.status == status
    ]


def is_document_retrieval_eligible(
    document_id: str,
) -> bool:
    """
    Normal retrieval permits Active documents only.

    Draft, Superseded and Archived material remains available
    for governance/audit testing but is not approved evidence.
    """

    metadata = get_document_metadata(
        document_id
    )

    return (
        metadata.status
        == "Active"
    )
