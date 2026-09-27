from src.governance.high_risk_claim_guard import (
    detect_high_risk_mismatch,
)


def test_supported_paraphrase_has_no_guard():
    result = detect_high_risk_mismatch(
        (
            "Essential services should be kept running "
            "when usual arrangements are disrupted."
        ),
        (
            "Business continuity arrangements maintain "
            "essential services when routine services "
            "are disrupted."
        ),
    )

    assert result["guard_triggered"] is False
    assert result["reasons"] == []


def test_unsupported_number_triggers_guard():
    result = detect_high_risk_mismatch(
        (
            "Bed occupancy above 92 percent requires "
            "immediate executive escalation."
        ),
        (
            "Operational teams should review hospital "
            "bed capacity and occupancy."
        ),
    )

    assert result["guard_triggered"] is True
    assert "unsupported_number" in result["reasons"]


def test_unsupported_mandatory_wording_triggers_guard():
    result = detect_high_risk_mismatch(
        (
            "Managers must immediately redeploy all "
            "available staff."
        ),
        (
            "Operational teams should review workforce "
            "pressure and staffing gaps."
        ),
    )

    assert result["guard_triggered"] is True
    assert "unsupported_mandatory_wording" in result["reasons"]


def test_unsupported_actor_triggers_guard():
    result = detect_high_risk_mismatch(
        (
            "The chief executive must personally manage "
            "every ambulance handover delay."
        ),
        (
            "Operational teams should monitor ambulance "
            "handover delays."
        ),
    )

    assert result["guard_triggered"] is True
    assert "unsupported_actor" in result["reasons"]


def test_unsupported_action_triggers_guard():
    result = detect_high_risk_mismatch(
        (
            "Teams should prepare for severe weather and "
            "suspend all outpatient clinics."
        ),
        (
            "The severe weather operational plan supports "
            "preparation before disruption."
        ),
    )

    assert result["guard_triggered"] is True
    assert "unsupported_action" in result["reasons"]


def test_negation_flip_triggers_guard():
    result = detect_high_risk_mismatch(
        (
            "Operational teams should not monitor "
            "ambulance handover delays."
        ),
        (
            "Operational teams should monitor ambulance "
            "handover delays."
        ),
    )

    assert result["guard_triggered"] is True
    assert "negation_mismatch" in result["reasons"]


def test_unsupported_prohibition_triggers_guard():
    result = detect_high_risk_mismatch(
        (
            "The severe weather plan prohibits use of "
            "business continuity arrangements."
        ),
        (
            "The severe weather operational plan "
            "complements wider business continuity "
            "arrangements."
        ),
    )

    assert result["guard_triggered"] is True
    assert "unsupported_prohibition" in result["reasons"]


def test_document_ids_do_not_count_as_numbers():
    result = detect_high_risk_mismatch(
        (
            "The available evidence does not establish "
            "that DOC-003 and DOC-011 conflict."
        ),
        (
            "DOC-003 describes staffing escalation actions."
        ),
    )

    assert "unsupported_number" not in result["reasons"]


def test_grounded_workforce_paraphrase_has_no_guard():
    result = detect_high_risk_mismatch(
        (
            "Teams should assess staffing shortages and "
            "available escalation options."
        ),
        (
            "Operational teams should review workforce "
            "pressure, staffing gaps and available "
            "escalation options."
        ),
    )

    assert result["guard_triggered"] is False


def test_blank_claim_rejected():
    try:
        detect_high_risk_mismatch(
            "",
            "Some evidence",
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for blank claim_text"
        )