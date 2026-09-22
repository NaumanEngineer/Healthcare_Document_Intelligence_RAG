import pytest

from src.retrieval.query_scope import (
    assess_query_scope,
    is_query_in_scope,
)


def test_operational_escalation_is_in_scope():
    result = assess_query_scope(
        "What should operational leadership do during escalation?"
    )

    assert result["allowed"] is True
    assert result["scope"] == "IN_SCOPE"


def test_workforce_pressure_is_in_scope():
    assert (
        is_query_in_scope(
            "What actions should be considered when workforce pressure becomes severe?"
        )
        is True
    )


def test_bed_capacity_is_in_scope():
    assert (
        is_query_in_scope(
            "Which guidance covers escalation when bed capacity is under pressure?"
        )
        is True
    )


def test_medication_question_is_out_of_scope():
    result = assess_query_scope(
        "What medication should be prescribed during operational escalation?"
    )

    assert result["allowed"] is False
    assert result["scope"] == "OUT_OF_SCOPE"


def test_antibiotic_dose_is_out_of_scope():
    assert (
        is_query_in_scope(
            "What antibiotic dose should be used for a patient with sepsis?"
        )
        is False
    )


def test_current_external_leadership_is_out_of_scope():
    assert (
        is_query_in_scope(
            "Who is the current Chief Executive of NHS England?"
        )
        is False
    )


def test_unknown_topic_defaults_out_of_scope():
    assert (
        is_query_in_scope(
            "What colour should the office walls be?"
        )
        is False
    )


def test_clinical_block_wins_over_operational_wording():
    result = assess_query_scope(
        "During operational escalation, what antibiotic should be prescribed?"
    )

    assert result["allowed"] is False


@pytest.mark.parametrize(
    "question",
    [
        pytest.param(
            "Where should staff look for guidance when routine services "
            "cannot continue normally after a major disruption?",
            id="Q021",
        ),
        pytest.param(
            "Where should managers look when incoming emergency transport "
            "delays are causing patients to remain with crews instead of "
            "transferring promptly into hospital care?",
            id="Q038",
        ),
        pytest.param(
            "What is the approved operational procedure for managing "
            "hospital cyber-security incidents?",
            id="Q029-no-corpus-evidence",
        ),
        pytest.param(
            "What approved operational guidance covers a complete failure "
            "of the hospital's electronic patient record system?",
            id="Q030-no-corpus-evidence",
        ),
        pytest.param(
            "Which approved policy defines the operational response to "
            "a major medical oxygen supply failure?",
            id="Q031-no-corpus-evidence",
        ),
        pytest.param(
            "What is the current escalation process?",
            id="current-local-policy",
        ),
        pytest.param(
            "Which escalation policy should staff follow today?",
            id="today-local-policy",
        ),
    ],
)
def test_operational_paraphrases_and_local_policy_remain_in_scope(question):
    result = assess_query_scope(question)

    assert result["allowed"] is True
    assert result["scope"] == "IN_SCOPE"
    assert result["matched_out_of_scope_terms"] == []


@pytest.mark.parametrize(
    "question",
    [
        pytest.param(
            "What is the current national NHS England operational "
            "performance position today?",
            id="Q033",
        ),
        "What is the current performance of NHS England operational services?",
        "What is the current operational performance across NHS England?",
        "Show live NHS England operational information.",
        "Show current NHS England operational information.",
    ],
)
def test_current_external_information_overrides_operational_terms(question):
    result = assess_query_scope(question)

    assert result["allowed"] is False
    assert result["scope"] == "OUT_OF_SCOPE"
    assert result["matched_out_of_scope_terms"]
