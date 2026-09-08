from dataclasses import dataclass, asdict
from typing import Optional
from uuid import uuid4


@dataclass(frozen=True)
class DocumentMetadata:
    document_id: str
    title: str
    document_type: str
    source_type: str
    version: str
    effective_date: str
    status: str
    source_file: str
    source_location: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


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


def is_active_document(metadata: DocumentMetadata) -> bool:
    return metadata.status == "Active"


def create_ingestion_batch_id() -> str:
    return str(uuid4())

  
