from src.governance.corrective_false_premise import (
    CORRECTION_NOT_SUPPORTED,
    CORRECTION_SUPPORTED,
    validate_corrective_false_premise,
)
from src.governance.evidence_set_relationship import (
    REVIEW_REQUIRED,
)


def test_cit010_fabricated_conflict_supports_correction():
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

    result = validate_corrective_false_premise(
        "CONFLICT",
        evidence,
    )

    assert result["decision"] == CORRECTION_SUPPORTED
    assert result["may_return_correction"] is True
    assert result["requires_human_review"] is False


def test_real_conflict_does_not_support_correction():
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

    result = validate_corrective_false_premise(
        "CONFLICT",
        evidence,
    )

    assert result["decision"] == CORRECTION_NOT_SUPPORTED
    assert result["may_return_correction"] is False


def test_no_precedence_supports_correction():
    evidence = [
        {
            "document_id": "DOC-A",
            "status": "Active",
            "text": (
                "This procedure describes workforce escalation."
            ),
        },
        {
            "document_id": "DOC-B",
            "status": "Active",
            "text": (
                "This procedure describes staffing resilience."
            ),
        },
    ]

    result = validate_corrective_false_premise(
        "TAKES_PRECEDENCE",
        evidence,
    )

    assert result["decision"] == CORRECTION_SUPPORTED


def test_explicit_precedence_does_not_support_correction():
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

    result = validate_corrective_false_premise(
        "TAKES_PRECEDENCE",
        evidence,
    )

    assert result["decision"] == CORRECTION_NOT_SUPPORTED


def test_draft_document_requires_review():
    evidence = [
        {
            "document_id": "DOC-A",
            "status": "Active",
            "text": (
                "This procedure describes operational escalation."
            ),
        },
        {
            "document_id": "DOC-B",
            "status": "Draft",
            "text": (
                "Draft procedure."
            ),
        },
    ]

    result = validate_corrective_false_premise(
        "CONFLICT",
        evidence,
    )

    assert result["decision"] == REVIEW_REQUIRED
    assert result["requires_human_review"] is True
    assert result["may_return_correction"] is False


def test_single_document_requires_review():
    evidence = [
        {
            "document_id": "DOC-A",
            "status": "Active",
            "text": (
                "This procedure describes operational escalation."
            ),
        }
    ]

    result = validate_corrective_false_premise(
        "CONFLICT",
        evidence,
    )

    assert result["decision"] == REVIEW_REQUIRED
    assert result["requires_human_review"] is True


def test_blank_relationship_rejected():
    try:
        validate_corrective_false_premise(
            "",
            [],
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for blank alleged_relationship"
        )


def test_non_list_evidence_rejected():
    try:
        validate_corrective_false_premise(
            "CONFLICT",
            "not-a-list",
        )
    except TypeError:
        pass
    else:
        raise AssertionError(
            "Expected TypeError for invalid evidence_items"
        )