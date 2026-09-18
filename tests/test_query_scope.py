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
