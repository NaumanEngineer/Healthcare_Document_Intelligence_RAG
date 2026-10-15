from src.evaluation.groundedness_audit import (
    ABSTAIN,
    GROUNDED,
    NOT_APPLICABLE,
    PARTIALLY_GROUNDED,
    PASS,
    REVIEW_REQUIRED,
    UNGROUNDED,
    audit_answer_groundedness,
    audit_claim_groundedness,
)


def _evidence(
    text=(
        "Operational teams should review "
        "staffing pressure daily."
    ),
):
    return [
        {
            "document_id": "DOC-A",
            "chunk_id": "DOC-A-C001",
            "status": "Active",
            "text": text,
        }
    ]


def test_supported_claim_is_grounded():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "Operational teams should review "
            "staffing pressure daily."
        ),
    }

    result = audit_claim_groundedness(
        claim,
        _evidence(),
    )

    assert result[
        "status"
    ] == GROUNDED


def test_no_evidence_is_ungrounded():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "Operational teams should review "
            "staffing pressure."
        ),
    }

    result = audit_claim_groundedness(
        claim,
        [],
    )

    assert result[
        "status"
    ] == UNGROUNDED


def test_unrelated_claim_is_ungrounded():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "Hospital kitchens should replace "
            "all refrigeration equipment."
        ),
    }

    result = audit_claim_groundedness(
        claim,
        _evidence(),
    )

    assert result[
        "status"
    ] == UNGROUNDED


def test_unsupported_number_is_not_grounded():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "Operational teams should review "
            "staffing pressure every 30 minutes."
        ),
    }

    result = audit_claim_groundedness(
        claim,
        _evidence(),
    )

    assert result[
        "status"
    ] in {
        PARTIALLY_GROUNDED,
        UNGROUNDED,
    }

    assert result[
        "high_risk_guard_triggered"
    ] is True


def test_unsupported_mandatory_wording_is_not_grounded():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "Operational teams must review "
            "staffing pressure daily."
        ),
    }

    result = audit_claim_groundedness(
        claim,
        _evidence(),
    )

    assert result[
        "status"
    ] == PARTIALLY_GROUNDED

    assert result[
        "high_risk_guard_triggered"
    ] is True


def test_unsupported_actor_is_not_grounded():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "The chief executive should review "
            "staffing pressure daily."
        ),
    }

    result = audit_claim_groundedness(
        claim,
        _evidence(),
    )

    assert result[
        "status"
    ] == PARTIALLY_GROUNDED

    assert result[
        "high_risk_guard_triggered"
    ] is True


def test_unsupported_action_is_not_grounded():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "Operational teams should cancel "
            "elective activity during staffing pressure."
        ),
    }

    result = audit_claim_groundedness(
        claim,
        _evidence(),
    )

    assert result[
        "status"
    ] == PARTIALLY_GROUNDED

    assert result[
        "high_risk_guard_triggered"
    ] is True


def test_unsupported_prohibition_is_not_grounded():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "Operational teams must not use "
            "agency staff during staffing pressure."
        ),
    }

    result = audit_claim_groundedness(
        claim,
        _evidence(),
    )

    assert result[
        "status"
    ] in {
        PARTIALLY_GROUNDED,
        UNGROUNDED,
    }

    assert result[
        "high_risk_guard_triggered"
    ] is True


def test_non_substantive_claim_is_not_applicable():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "Human review is required before use."
        ),
    }

    result = audit_claim_groundedness(
        claim,
        [],
        material=False,
    )

    assert result[
        "status"
    ] == NOT_APPLICABLE


def test_answer_passes_when_all_material_claims_grounded():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "Operational teams should review "
                "staffing pressure daily."
            ),
        }
    ]

    result = audit_answer_groundedness(
        claims,
        {
            "C1": _evidence()
        },
    )

    assert result[
        "decision"
    ] == PASS


def test_answer_requires_review_for_partial_claim():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "Operational teams must review "
                "staffing pressure daily."
            ),
        }
    ]

    result = audit_answer_groundedness(
        claims,
        {
            "C1": _evidence()
        },
    )

    assert result[
        "decision"
    ] == REVIEW_REQUIRED


def test_answer_requires_review_for_ungrounded_claim():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "Hospital kitchens should replace "
                "all refrigeration equipment."
            ),
        }
    ]

    result = audit_answer_groundedness(
        claims,
        {
            "C1": _evidence()
        },
    )

    assert result[
        "decision"
    ] == REVIEW_REQUIRED


def test_abstain_without_material_claims_is_preserved():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "There is insufficient evidence "
                "to answer safely."
            ),
        }
    ]

    result = audit_answer_groundedness(
        claims,
        {},
        non_substantive_claim_ids=[
            "C1"
        ],
        upstream_governance_decision=(
            "ABSTAIN"
        ),
    )

    assert result[
        "decision"
    ] == ABSTAIN


def test_duplicate_claim_id_fails_closed():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "Operational teams should review "
                "staffing pressure daily."
            ),
        },
        {
            "claim_id": "C1",
            "claim_text": (
                "Operational teams should review "
                "staffing pressure daily."
            ),
        },
    ]

    try:
        audit_answer_groundedness(
            claims,
            {
                "C1": _evidence()
            },
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected duplicate claim IDs to fail closed."
        )