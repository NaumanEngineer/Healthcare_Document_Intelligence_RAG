from src.evidence.evidence_precedence import (
    BLOCK_COMBINATION,
    REVIEW_BEFORE_COMBINATION,
    SAFE_TO_COMBINE,
    assess_evidence_precedence,
)


def _evidence(
    *,
    document_id: str,
    status: str = "Active",
    text: str,
) -> dict:
    return {
        "document_id": document_id,
        "status": status,
        "evidence_text": text,
    }


def test_single_active_document_is_safe_at_this_layer():
    result = assess_evidence_precedence(
        [
            _evidence(
                document_id="DOC-008",
                text=(
                    "Ambulance handover delays "
                    "should be monitored."
                ),
            ),
        ]
    )

    assert result[
        "decision"
    ] == SAFE_TO_COMBINE


def test_draft_document_requires_review():
    result = assess_evidence_precedence(
        [
            _evidence(
                document_id="DOC-014",
                status="Draft",
                text=(
                    "Draft emergency pressure "
                    "framework."
                ),
            ),
        ]
    )

    assert result[
        "decision"
    ] == REVIEW_BEFORE_COMBINATION

    assert "DOC-014" in result[
        "lifecycle"
    ][
        "risky_documents"
    ]


def test_superseded_document_requires_review():
    result = assess_evidence_precedence(
        [
            _evidence(
                document_id="DOC-001",
                status="Superseded",
                text=(
                    "Superseded operational "
                    "escalation policy."
                ),
            ),
        ]
    )

    assert result[
        "decision"
    ] == REVIEW_BEFORE_COMBINATION


def test_archived_document_requires_review():
    result = assess_evidence_precedence(
        [
            _evidence(
                document_id="DOC-999",
                status="Archived",
                text="Archived material.",
            ),
        ]
    )

    assert result[
        "decision"
    ] == REVIEW_BEFORE_COMBINATION


def test_mixed_status_for_same_document_requires_review():
    result = assess_evidence_precedence(
        [
            _evidence(
                document_id="DOC-001",
                status="Active",
                text="Current policy.",
            ),
            _evidence(
                document_id="DOC-001",
                status="Superseded",
                text="Older policy.",
            ),
        ]
    )

    assert result[
        "decision"
    ] == REVIEW_BEFORE_COMBINATION


def test_two_active_documents_without_established_conflict_are_safe():
    result = assess_evidence_precedence(
        [
            _evidence(
                document_id="DOC-008",
                text=(
                    "Ambulance handover delays "
                    "should be monitored."
                ),
            ),
            _evidence(
                document_id="DOC-009",
                text=(
                    "Severe weather pressure should "
                    "be reviewed alongside existing "
                    "organisational pressure."
                ),
            ),
        ]
    )

    assert result[
        "decision"
    ] == SAFE_TO_COMBINE


def test_explicit_conflict_blocks_combination():
    result = assess_evidence_precedence(
        [
            _evidence(
                document_id="DOC-A",
                text=(
                    "DOC-A conflicts with DOC-B."
                ),
            ),
            _evidence(
                document_id="DOC-B",
                text=(
                    "DOC-B is in conflict with DOC-A."
                ),
            ),
        ]
    )

    assert result[
        "decision"
    ] == BLOCK_COMBINATION

    assert result[
        "blocking_relationships"
    ]


def test_explicit_replacement_requires_review():
    result = assess_evidence_precedence(
        [
            _evidence(
                document_id="DOC-A",
                text=(
                    "DOC-A replaces DOC-B."
                ),
            ),
            _evidence(
                document_id="DOC-B",
                text="Older guidance.",
            ),
        ]
    )

    assert result[
        "decision"
    ] == REVIEW_BEFORE_COMBINATION


def test_explicit_precedence_requires_review():
    result = assess_evidence_precedence(
        [
            _evidence(
                document_id="DOC-A",
                text=(
                    "DOC-A takes precedence over DOC-B."
                ),
            ),
            _evidence(
                document_id="DOC-B",
                text="Supporting guidance.",
            ),
        ]
    )

    assert result[
        "decision"
    ] == REVIEW_BEFORE_COMBINATION


def test_empty_evidence_requires_review():
    result = assess_evidence_precedence(
        []
    )

    assert result[
        "decision"
    ] == REVIEW_BEFORE_COMBINATION


def test_missing_required_field_fails_closed():
    evidence = {
        "document_id": "DOC-008",
        "status": "Active",
    }

    try:
        assess_evidence_precedence(
            [evidence]
        )

    except ValueError as error:
        assert "evidence_text" in str(
            error
        )

    else:
        raise AssertionError(
            "Expected missing evidence_text to fail"
        )


def test_non_list_input_fails_closed():
    try:
        assess_evidence_precedence(
            {}
        )

    except TypeError as error:
        assert "list" in str(
            error
        )

    else:
        raise AssertionError(
            "Expected non-list evidence input to fail"
        )