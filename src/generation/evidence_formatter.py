from __future__ import annotations


REQUIRED_EVIDENCE_FIELDS = (
    "chunk_id",
    "document_id",
    "title",
    "version",
    "status",
    "page",
    "text",
)


def validate_evidence_record(
    evidence: dict,
) -> None:
    """
    Validate one retrieved evidence record before it is
    supplied to the answer-generation layer.
    """

    if not isinstance(evidence, dict):
        raise TypeError(
            "evidence must be a dictionary"
        )

    for field in REQUIRED_EVIDENCE_FIELDS:
        if field not in evidence:
            raise ValueError(
                f"Missing required evidence field: {field}"
            )

    for field in (
        "chunk_id",
        "document_id",
        "title",
        "version",
        "status",
        "text",
    ):
        value = evidence.get(field)

        if (
            not isinstance(value, str)
            or not value.strip()
        ):
            raise ValueError(
                f"{field} must be a non-empty string"
            )

    page = evidence.get("page")

    if (
        not isinstance(page, int)
        or isinstance(page, bool)
        or page <= 0
    ):
        raise ValueError(
            "page must be a positive integer"
        )

    if evidence.get("status") != "Active":
        raise ValueError(
            "Only Active evidence may enter generation"
        )


def build_citation_metadata(
    evidence: dict,
) -> dict:
    """
    Extract the citation fields allowed to flow
    into the generation layer.
    """

    validate_evidence_record(
        evidence
    )

    citation = {
        "chunk_id": evidence["chunk_id"],
        "document_id": evidence["document_id"],
        "title": evidence["title"],
        "version": evidence["version"],
        "page": evidence["page"],
    }

    source_file = evidence.get(
        "source_file"
    )

    if (
        isinstance(source_file, str)
        and source_file.strip()
    ):
        citation["source_file"] = (
            source_file
        )

    return citation


def format_evidence_record(
    evidence: dict,
    evidence_number: int,
) -> str:
    """
    Convert one retrieved chunk into a controlled
    text block for the grounded prompt.
    """

    validate_evidence_record(
        evidence
    )

    if (
        not isinstance(evidence_number, int)
        or isinstance(evidence_number, bool)
        or evidence_number <= 0
    ):
        raise ValueError(
            "evidence_number must be a positive integer"
        )

    lines = [
        f"[EVIDENCE {evidence_number}]",
        f"Document ID: {evidence['document_id']}",
        f"Title: {evidence['title']}",
        f"Version: {evidence['version']}",
        f"Status: {evidence['status']}",
        f"Page: {evidence['page']}",
        f"Chunk ID: {evidence['chunk_id']}",
    ]

    source_file = evidence.get(
        "source_file"
    )

    if (
        isinstance(source_file, str)
        and source_file.strip()
    ):
        lines.append(
            f"Source File: {source_file}"
        )

    lines.extend(
        [
            "Text:",
            evidence["text"].strip(),
            f"[/EVIDENCE {evidence_number}]",
        ]
    )

    return "\n".join(lines)


def format_evidence_context(
    evidence_results: list[dict],
) -> str:
    """
    Format all retrieved evidence into one controlled
    evidence context for the prompt builder.

    An empty result returns an empty string so the
    caller can trigger abstention behaviour.
    """

    if not isinstance(
        evidence_results,
        list,
    ):
        raise TypeError(
            "evidence_results must be a list"
        )

    if not evidence_results:
        return ""

    formatted_records = []

    for evidence_number, evidence in enumerate(
        evidence_results,
        start=1,
    ):
        formatted_records.append(
            format_evidence_record(
                evidence=evidence,
                evidence_number=evidence_number,
            )
        )

    return "\n\n".join(
        formatted_records
    )


def build_evidence_packet(
    evidence_results: list[dict],
) -> dict:
    """
    Build the structured evidence package used by
    the prompt-generation layer.

    The packet contains:

    - formatted evidence text
    - citation metadata
    - evidence count
    - has_evidence flag
    """

    if not isinstance(
        evidence_results,
        list,
    ):
        raise TypeError(
            "evidence_results must be a list"
        )

    if not evidence_results:
        return {
            "has_evidence": False,
            "evidence_count": 0,
            "formatted_context": "",
            "citations": [],
        }

    citations = []

    for evidence in evidence_results:
        citations.append(
            build_citation_metadata(
                evidence
            )
        )

    formatted_context = (
        format_evidence_context(
            evidence_results
        )
    )

    return {
        "has_evidence": True,
        "evidence_count": len(
            evidence_results
        ),
        "formatted_context": formatted_context,
        "citations": citations,
    }
