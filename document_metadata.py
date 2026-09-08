DOCUMENT_REGISTER = {
    "DOC-001": DocumentMetadata(
        document_id="DOC-001",
        title="Operational Escalation Policy",
        document_type="Operational Policy",
        source_type="Synthetic",
        version="1.0",
        effective_date="2026-01-01",
        status="Active",
        source_file="DOC-001_operational_escalation_policy.pdf",
    ),
    "DOC-002": DocumentMetadata(
        document_id="DOC-002",
        title="Winter Pressure Plan",
        document_type="Operational Plan",
        source_type="Synthetic",
        version="1.0",
        effective_date="2026-01-01",
        status="Active",
        source_file="DOC-002_winter_pressure_plan.pdf",
    ),
    "DOC-003": DocumentMetadata(
        document_id="DOC-003",
        title="Workforce Escalation Procedure",
        document_type="Procedure",
        source_type="Synthetic",
        version="1.0",
        effective_date="2026-01-01",
        status="Active",
        source_file="DOC-003_workforce_escalation_procedure.pdf",
    ),
}


def get_document_metadata(document_id: str) -> DocumentMetadata:
    """
    Return metadata for a known document ID.
    """
    try:
        return DOCUMENT_REGISTER[document_id]
    except KeyError as exc:
        raise KeyError(
            f"No metadata found for document_id '{document_id}'."
        ) from exc


def enrich_page_record(page_record: dict, metadata: DocumentMetadata) -> dict:
    """
    Combine page-level extraction data with document-level metadata.
    """
    return {
        **metadata.to_dict(),
        **page_record,
    }

ALLOWED_DOCUMENT_STATUSES = {
    "Active",
    "Superseded",
    "Draft",
    "Archived",
}


def validate_document_status(status: str) -> None:
    if status not in ALLOWED_DOCUMENT_STATUSES:
        raise ValueError(
            f"Unsupported document status '{status}'."
        )

metadata = DOCUMENT_REGISTER[document_id]
validate_document_status(metadata.status)
return metadata
