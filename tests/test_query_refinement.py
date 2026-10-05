from __future__ import annotations

import pytest

from src.retrieval.query_refinement import (
    refine_query_for_missing_topic,
)


def test_refiner_returns_none_when_no_topics_missing():
    result = refine_query_for_missing_topic(
        "How should staffing pressure be managed?",
        {
            "missing_topics": [],
        },
    )

    assert result is None


def test_refiner_creates_focused_workforce_query():
    result = refine_query_for_missing_topic(
        "How should staffing and bed capacity pressure be managed?",
        {
            "missing_topics": [
                "workforce",
            ],
        },
    )

    assert result == (
        "workforce operational procedure"
    )


def test_refiner_does_not_repeat_original_long_query():
    original = (
        "How should staffing and bed capacity "
        "pressure be managed?"
    )

    result = refine_query_for_missing_topic(
        original,
        {
            "missing_topics": [
                "workforce",
            ],
        },
    )

    assert result is not None

    assert not result.startswith(
        original
    )

    assert result == (
        "workforce operational procedure"
    )


def test_refiner_selects_recognised_topic_deterministically():
    result = refine_query_for_missing_topic(
        "How should operational pressure be managed?",
        {
            "missing_topics": [
                "workforce",
                "bed_capacity",
            ],
        },
    )

    # Missing topics are sorted.
    # bed_capacity therefore wins deterministically.
    assert result == (
        "bed capacity management procedure"
    )


def test_refiner_creates_severe_weather_operational_query():
    result = refine_query_for_missing_topic(
        (
            "How should severe weather and ambulance "
            "handover disruption be considered together?"
        ),
        {
            "missing_topics": [
                "severe_weather",
            ],
        },
    )

    assert result == (
        "severe weather operational plan"
    )


def test_refiner_creates_ambulance_handover_query():
    result = refine_query_for_missing_topic(
        (
            "How should severe weather and ambulance "
            "handover disruption be considered together?"
        ),
        {
            "missing_topics": [
                "ambulance_handover",
            ],
        },
    )

    assert result == (
        "ambulance handover escalation guidance"
    )


def test_refiner_creates_cybersecurity_query():
    result = refine_query_for_missing_topic(
        (
            "What approved operational procedure "
            "covers cyber-security incidents?"
        ),
        {
            "missing_topics": [
                "cybersecurity",
            ],
        },
    )

    assert result == (
        "cyber-security operational procedure"
    )


def test_refiner_creates_epr_query():
    result = refine_query_for_missing_topic(
        (
            "What guidance covers an electronic "
            "patient record system failure?"
        ),
        {
            "missing_topics": [
                "electronic_patient_record",
            ],
        },
    )

    assert result == (
        "electronic patient record system failure"
    )


def test_refiner_creates_oxygen_supply_query():
    result = refine_query_for_missing_topic(
        (
            "What procedure covers a medical "
            "oxygen supply failure?"
        ),
        {
            "missing_topics": [
                "oxygen_supply",
            ],
        },
    )

    assert result == (
        "medical oxygen supply failure"
    )


@pytest.mark.parametrize(
    "lexical_topic",
    [
        "exact",
        "applied",
        "advance",
        "explicitly",
    ],
)
def test_refiner_does_not_search_uncontrolled_lexical_terms(
    lexical_topic,
):
    result = refine_query_for_missing_topic(
        "Some operational question",
        {
            "missing_topics": [
                lexical_topic,
            ],
        },
    )

    assert result is None


def test_refiner_ignores_lexical_topic_when_controlled_topic_exists():
    result = refine_query_for_missing_topic(
        "Some operational question",
        {
            "missing_topics": [
                "exact",
                "severe_weather",
            ],
        },
    )

    assert result == (
        "severe weather operational plan"
    )


def test_refiner_rejects_non_string_query():
    with pytest.raises(TypeError):
        refine_query_for_missing_topic(
            123,
            {
                "missing_topics": [
                    "workforce",
                ],
            },
        )


def test_refiner_rejects_blank_query():
    with pytest.raises(ValueError):
        refine_query_for_missing_topic(
            "   ",
            {
                "missing_topics": [
                    "workforce",
                ],
            },
        )


def test_refiner_rejects_non_dictionary_diagnostics():
    with pytest.raises(TypeError):
        refine_query_for_missing_topic(
            "How should staffing be managed?",
            [
                "workforce",
            ],
        )


def test_refiner_requires_missing_topics():
    with pytest.raises(ValueError):
        refine_query_for_missing_topic(
            "How should staffing be managed?",
            {},
        )


def test_refiner_rejects_non_list_missing_topics():
    with pytest.raises(TypeError):
        refine_query_for_missing_topic(
            "How should staffing be managed?",
            {
                "missing_topics": "workforce",
            },
        )


def test_refiner_rejects_blank_missing_topic():
    with pytest.raises(ValueError):
        refine_query_for_missing_topic(
            "How should staffing be managed?",
            {
                "missing_topics": [
                    "",
                ],
            },
        )