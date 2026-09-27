from src.governance.evidence_set_relationship import (
    RELATIONSHIP_NOT_ESTABLISHED,
    RELATIONSHIP_SUPPORTED,
    REVIEW_REQUIRED,
    validate_evidence_set_relationship,
)


def test_explicit_complements_relationship_is_supported():
    evidence = [
        {
            "document_id": "DOC-009",
            "status": "Active",
            "title": "Severe Weather Operational Plan",
            "text": (
                "The severe weather operational plan complements "
                "business continuity arrangements."
            ),
        },
        {
            "document_id": "DOC-005",
            "status": "Active",
            "title": "Business Continuity Procedure",
            "text": (
                "Business continuity arrangements maintain "
                "essential services during disruption."
            ),
        },
    ]

    result = validate_evidence_set_relationship(
        "COMPLEMENTS",
        evidence,
    )

    assert result["decision"] == RELATIONSHIP_SUPPORTED
    assert "complements" in result["matched_relationship_terms"]


def test_fabricated_conflict_is_not_established():
    evidence = [
        {
            "document_id": "DOC-003",
            "status": "Active",
            "title": "Workforce Escalation Procedure",
            "text": (
                "The workforce escalation procedure describes "
                "staffing escalation actions."
            ),
        },
        {
            "document_id": "DOC-011",
            "status": "Active",
            "title": "Critical Staffing Contingency Procedure",
            "text": (
                "The critical staffing contingency procedure "
                "describes short-term staffing resilience actions."
            ),
        },
    ]

    result = validate_evidence_set_relationship(
        "CONFLICT",
        evidence,
    )

    assert result["decision"] == RELATIONSHIP_NOT_ESTABLISHED


def test_explicit_conflict_language_is_supported():
    evidence = [
        {
            "document_id": "DOC-A",
            "status": "Active",
            "text": (
                "This instruction conflicts with the staffing "
                "requirement defined in DOC-B."
            ),
        },
        {
            "document_id": "DOC-B",
            "status": "Active",
            "text": (
                "DOC-B defines a separate staffing requirement."
            ),
        },
    ]

    result = validate_evidence_set_relationship(
        "CONFLICT",
        evidence,
    )

    assert result["decision"] == RELATIONSHIP_SUPPORTED


def test_explicit_replacement_relationship_is_supported():
    evidence = [
        {
            "document_id": "DOC-A",
            "status": "Active",
            "text": (
                "This procedure replaces the previous "
                "operational escalation procedure."
            ),
        },
        {
            "document_id": "DOC-B",
            "status": "Active",
            "text": (
                "Previous operational escalation procedure."
            ),
        },
    ]

    result = validate_evidence_set_relationship(
        "REPLACES",
        evidence,
    )

    assert result["decision"] == RELATIONSHIP_SUPPORTED


def test_explicit_precedence_relationship_is_supported():
    evidence = [
        {
            "document_id": "DOC-A",
            "status": "Active",
            "text": (
                "During a major incident this procedure "
                "takes precedence over DOC-B."
            ),
        },
        {
            "document_id": "DOC-B",
            "status": "Active",
            "text": (
                "Routine operational procedure."
            ),
        },
    ]

    result = validate_evidence_set_relationship(
        "TAKES_PRECEDENCE",
        evidence,
    )

    assert result["decision"] == RELATIONSHIP_SUPPORTED


def test_draft_evidence_requires_review():
    evidence = [
        {
            "document_id": "DOC-A",
            "status": "Active",
            "text": (
                "This procedure complements DOC-B."
            ),
        },
        {
            "document_id": "DOC-B",
            "status": "Draft",
            "text": (
                "Draft supporting procedure."
            ),
        },
    ]

    result = validate_evidence_set_relationship(
        "COMPLEMENTS",
        evidence,
    )

    assert result["decision"] == REVIEW_REQUIRED
    assert result["evidence_status"] == "LIFECYCLE_RISK"


def test_superseded_evidence_requires_review():
    evidence = [
        {
            "document_id": "DOC-A",
            "status": "Superseded",
            "text": (
                "This procedure replaces DOC-B."
            ),
        },
        {
            "document_id": "DOC-B",
            "status": "Active",
            "text": (
                "Active procedure."
            ),
        },
    ]

    result = validate_evidence_set_relationship(
        "REPLACES",
        evidence,
    )

    assert result["decision"] == REVIEW_REQUIRED


def test_missing_status_requires_review():
    evidence = [
        {
            "document_id": "DOC-A",
            "text": (
                "This procedure complements DOC-B."
            ),
        },
        {
            "document_id": "DOC-B",
            "status": "Active",
            "text": (
                "Active procedure."
            ),
        },
    ]

    result = validate_evidence_set_relationship(
        "COMPLEMENTS",
        evidence,
    )

    assert result["decision"] == REVIEW_REQUIRED
    assert result["evidence_status"] == "NOT_CONFIRMED_ACTIVE"


def test_single_document_requires_review():
    evidence = [
        {
            "document_id": "DOC-A",
            "status": "Active",
            "text": (
                "This procedure complements another process."
            ),
        }
    ]

    result = validate_evidence_set_relationship(
        "COMPLEMENTS",
        evidence,
    )

    assert result["decision"] == REVIEW_REQUIRED
    assert result["evidence_status"] == "INSUFFICIENT_DOCUMENT_SET"


def test_unsupported_relationship_type_raises_value_error():
    evidence = [
        {
            "document_id": "DOC-A",
            "status": "Active",
            "text": "Some evidence.",
        },
        {
            "document_id": "DOC-B",
            "status": "Active",
            "text": "More evidence.",
        },
    ]

    try:
        validate_evidence_set_relationship(
            "OVERRULES_EVERYTHING",
            evidence,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for unsupported relationship type"
        )