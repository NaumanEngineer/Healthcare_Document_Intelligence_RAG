from dataclasses import dataclass, asdict
from typing import Optional


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

  
