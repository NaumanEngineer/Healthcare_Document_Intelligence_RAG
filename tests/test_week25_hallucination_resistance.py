from src.evaluation.hallucination_resistance import (
    ABSTAIN,
    ABSTENTION_VIOLATION,
    CLEAR,
    HALLUCINATION_RISK,
    NOT_APPLICABLE,
    PASS,
    REVIEW_AUTHORITY_INCREASE,
    REVIEW_REQUIRED,
    audit_answer_hallucination_resistance,
)


def _evidence(
    text,
):
    return [
        {
            "document_id": "DOC-A",
            "chunk_id": "DOC-A-C001",
            "status": "Active",
            "text": text,
        }
    ]


def test_clean_auto_answer_passes():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "Operational teams should review "
                "staffing pressure daily."
            ),
        }
    ]

    result = (
        audit_answer_hallucination_resistance(
            claims,
            {
                "C1": _evidence(
                    "Operational teams should review "
                    "staffing pressure daily."
                )
            },
            upstream_governance_decision=(
                "AUTO_ANSWER"
            ),
        )
    )

    assert result[
        "decision"
    ] == PASS

    assert result[
        "claim_results"
    ][0][
        "status"
    ] == CLEAR


def test_unsupported_number_requires_review():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "Operational teams should review "
                "staffing pressure every 30 minutes."
            ),
        }
    ]

    result = (
        audit_answer_hallucination_resistance(
            claims,
            {
                "C1": _evidence(
                    "Operational teams should review "
                    "staffing pressure daily."
                )
            },
            upstream_governance_decision=(
                "AUTO_ANSWER"
            ),
        )
    )

    assert result[
        "decision"
    ] == REVIEW_REQUIRED

    assert result[
        "claim_results"
    ][0][
        "status"
    ] == HALLUCINATION_RISK


def test_hidden_uncertainty_requires_review():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "Staffing pressure contributes "
                "to delays."
            ),
        }
    ]

    result = (
        audit_answer_hallucination_resistance(
            claims,
            {
                "C1": _evidence(
                    "Staffing pressure may contribute "
                    "to delays."
                )
            },
            upstream_governance_decision=(
                "AUTO_ANSWER"
            ),
        )
    )

    assert result[
        "decision"
    ] == REVIEW_REQUIRED

    assert result[
        "claim_results"
    ][0][
        "status"
    ] == HALLUCINATION_RISK


def test_causal_overstatement_requires_review():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "Staffing pressure causes delays."
            ),
        }
    ]

    result = (
        audit_answer_hallucination_resistance(
            claims,
            {
                "C1": _evidence(
                    "Staffing pressure may be "
                    "associated with delays."
                )
            },
            upstream_governance_decision=(
                "AUTO_ANSWER"
            ),
        )
    )

    assert result[
        "decision"
    ] == REVIEW_REQUIRED


def test_review_required_can_never_upgrade_to_pass():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "The evidence identifies "
                "operational pressure."
            ),
        }
    ]

    result = (
        audit_answer_hallucination_resistance(
            claims,
            {
                "C1": _evidence(
                    "The evidence identifies "
                    "operational pressure."
                )
            },
            upstream_governance_decision=(
                "REVIEW_REQUIRED"
            ),
        )
    )

    assert result[
        "decision"
    ] == REVIEW_REQUIRED

    assert (
        result[
            "review_authority_increase_detected"
        ]
        is False
    )


def test_review_required_mandatory_instruction_is_flagged():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "Managers must review "
                "the operational response."
            ),
        }
    ]

    result = (
        audit_answer_hallucination_resistance(
            claims,
            {
                "C1": _evidence(
                    "Managers must review "
                    "the operational response."
                )
            },
            upstream_governance_decision=(
                "REVIEW_REQUIRED"
            ),
        )
    )

    assert result[
        "decision"
    ] == REVIEW_REQUIRED

    assert (
        result[
            "review_authority_increase_detected"
        ]
        is True
    )

    assert result[
        "claim_results"
    ][0][
        "status"
    ] == REVIEW_AUTHORITY_INCREASE


def test_review_operational_action_is_flagged():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "The service should cancel "
                "elective activity."
            ),
        }
    ]

    result = (
        audit_answer_hallucination_resistance(
            claims,
            {
                "C1": _evidence(
                    "The service should cancel "
                    "elective activity."
                )
            },
            upstream_governance_decision=(
                "REVIEW_REQUIRED"
            ),
        )
    )

    assert (
        result[
            "review_authority_increase_detected"
        ]
        is True
    )


def test_abstain_with_only_non_substantive_text_is_safe():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "There is insufficient evidence "
                "to answer safely."
            ),
        }
    ]

    result = (
        audit_answer_hallucination_resistance(
            claims,
            {},
            non_substantive_claim_ids=[
                "C1"
            ],
            upstream_governance_decision=(
                "ABSTAIN"
            ),
        )
    )

    assert result[
        "decision"
    ] == ABSTAIN

    assert (
        result[
            "abstention_violation_detected"
        ]
        is False
    )

    assert result[
        "claim_results"
    ][0][
        "status"
    ] == NOT_APPLICABLE


def test_abstain_with_material_advice_is_violation():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "Operational teams should "
                "cancel elective activity."
            ),
        }
    ]

    result = (
        audit_answer_hallucination_resistance(
            claims,
            {
                "C1": _evidence(
                    "Operational teams should "
                    "cancel elective activity."
                )
            },
            upstream_governance_decision=(
                "ABSTAIN"
            ),
        )
    )

    assert result[
        "decision"
    ] == ABSTAIN

    assert (
        result[
            "abstention_violation_detected"
        ]
        is True
    )

    assert result[
        "claim_results"
    ][0][
        "status"
    ] == ABSTENTION_VIOLATION


def test_abstain_never_becomes_review_or_pass():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "Operational pressure exists."
            ),
        }
    ]

    result = (
        audit_answer_hallucination_resistance(
            claims,
            {
                "C1": _evidence(
                    "Operational pressure exists."
                )
            },
            upstream_governance_decision=(
                "ABSTAIN"
            ),
        )
    )

    assert result[
        "decision"
    ] == ABSTAIN


def test_non_substantive_claim_does_not_create_risk():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "Human review is required "
                "before use."
            ),
        }
    ]

    result = (
        audit_answer_hallucination_resistance(
            claims,
            {},
            non_substantive_claim_ids=[
                "C1"
            ],
            upstream_governance_decision=(
                "REVIEW_REQUIRED"
            ),
        )
    )

    assert result[
        "decision"
    ] == REVIEW_REQUIRED

    assert result[
        "claim_results"
    ][0][
        "status"
    ] == NOT_APPLICABLE


def test_policy_authority_overstatement_requires_review():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "The approved policy requires "
                "daily escalation review."
            ),
        }
    ]

    result = (
        audit_answer_hallucination_resistance(
            claims,
            {
                "C1": _evidence(
                    "Guidance recommends "
                    "daily escalation review."
                )
            },
            upstream_governance_decision=(
                "AUTO_ANSWER"
            ),
        )
    )

    assert result[
        "decision"
    ] == REVIEW_REQUIRED


def test_unrelated_claim_requires_review():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "Hospital kitchens should replace "
                "all refrigeration equipment."
            ),
        }
    ]

    result = (
        audit_answer_hallucination_resistance(
            claims,
            {
                "C1": _evidence(
                    "Operational teams should "
                    "review staffing pressure."
                )
            },
            upstream_governance_decision=(
                "AUTO_ANSWER"
            ),
        )
    )

    assert result[
        "decision"
    ] == REVIEW_REQUIRED


def test_unknown_governance_fails_closed():
    try:
        audit_answer_hallucination_resistance(
            [],
            {},
            upstream_governance_decision=(
                "UNKNOWN"
            ),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected unknown governance state "
            "to fail closed."
        )


def test_duplicate_claim_id_fails_closed():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "Operational pressure exists."
            ),
        },
        {
            "claim_id": "C1",
            "claim_text": (
                "Operational pressure exists."
            ),
        },
    ]

    try:
        audit_answer_hallucination_resistance(
            claims,
            {
                "C1": _evidence(
                    "Operational pressure exists."
                )
            },
            upstream_governance_decision=(
                "AUTO_ANSWER"
            ),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected duplicate claim IDs "
            "to fail closed."
        )