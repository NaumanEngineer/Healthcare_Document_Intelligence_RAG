"""Deterministic query refinement for bounded retrieval.

This module creates one focused follow-up query from deterministic
evidence-topic diagnostics.

The refinement strategy deliberately searches for the missing evidence
topic rather than repeating the entire original question.

It does not:
- use an LLM;
- retrieve evidence;
- assess evidence sufficiency;
- alter lifecycle status;
- make governance decisions;
- approve answers.

Only recognised concepts from the shared evidence-sufficiency
vocabulary are eligible for refinement.

Fallback lexical words such as "exact", "applied" or "explicitly" are
not treated as reliable refinement targets.
"""

from __future__ import annotations

from src.retrieval.evidence_sufficiency import (
    CONCEPT_ALIASES,
)


# Deterministic retrieval-oriented phrases for concepts where the
# document family is operationally meaningful.
#
# These are search hints only. They do not establish evidence,
# lifecycle validity, sufficiency or governance approval.
CONCEPT_QUERY_HINTS = {
    "operational_escalation": (
        "operational escalation policy"
    ),
    "operational_leadership": (
        "operational leadership guidance"
    ),
    "workforce": (
        "workforce operational procedure"
    ),
    "bed_capacity": (
        "bed capacity management procedure"
    ),
    "winter_pressure": (
        "winter pressure plan"
    ),
    "severe_weather": (
        "severe weather operational plan"
    ),
    "business_continuity": (
        "business continuity procedure"
    ),
    "ambulance_handover": (
        "ambulance handover escalation guidance"
    ),
    "emergency_department": (
        "emergency department escalation procedure"
    ),
    "infection_surge": (
        "infection surge operational response plan"
    ),
    "site_flow": (
        "site flow coordination procedure"
    ),
    "operational_pressure": (
        "operational pressure coordination guidance"
    ),
    "cybersecurity": (
        "cyber-security operational procedure"
    ),
    "electronic_patient_record": (
        "electronic patient record system failure"
    ),
    "oxygen_supply": (
        "medical oxygen supply failure"
    ),
}


def _validate_original_query(
    original_query: str,
) -> str:
    """Validate and normalise the original query."""

    if not isinstance(
        original_query,
        str,
    ):
        raise TypeError(
            "original_query must be a string"
        )

    cleaned = " ".join(
        original_query.split()
    )

    if not cleaned:
        raise ValueError(
            "original_query must not be blank"
        )

    return cleaned


def _validate_diagnostics(
    diagnostics: dict,
) -> list[str]:
    """Validate diagnostics and return deterministic missing topics."""

    if not isinstance(
        diagnostics,
        dict,
    ):
        raise TypeError(
            "diagnostics must be a dictionary"
        )

    missing_topics = diagnostics.get(
        "missing_topics"
    )

    if missing_topics is None:
        raise ValueError(
            "diagnostics must contain missing_topics"
        )

    if not isinstance(
        missing_topics,
        list,
    ):
        raise TypeError(
            "missing_topics must be a list"
        )

    validated_topics = []

    for topic in missing_topics:
        if not isinstance(
            topic,
            str,
        ):
            raise TypeError(
                "each missing topic must be a string"
            )

        cleaned_topic = topic.strip()

        if not cleaned_topic:
            raise ValueError(
                "missing topics must not contain blank values"
            )

        validated_topics.append(
            cleaned_topic
        )

    return sorted(
        set(
            validated_topics
        )
    )


def _recognised_missing_topics(
    missing_topics: list[str],
) -> list[str]:
    """Keep only topics from the controlled concept vocabulary."""

    return [
        topic
        for topic in missing_topics
        if topic in CONCEPT_ALIASES
    ]


def _topic_search_phrase(
    topic: str,
) -> str:
    """Return a deterministic retrieval-oriented concept query."""

    configured_hint = (
        CONCEPT_QUERY_HINTS.get(
            topic
        )
    )

    if configured_hint:
        return configured_hint

    aliases = CONCEPT_ALIASES.get(
        topic
    )

    if aliases:
        return aliases[0]

    raise ValueError(
        f"unknown refinement topic: {topic}"
    )


def refine_query_for_missing_topic(
    original_query: str,
    diagnostics: dict,
) -> str | None:
    """Create one focused query for a recognised missing topic.

    The original query is validated but is intentionally NOT copied
    into the refined search query.

    Why:
    repeating a long multi-topic question can cause already-covered
    concepts to dominate the second retrieval round.

    Instead, round two searches specifically for one missing controlled
    concept.

    Evidence returned by this focused query must still be assessed
    later against the ORIGINAL question by the bounded retrieval
    controller.

    Returns None when:
    - there is no missing topic; or
    - missing items are only uncontrolled lexical fallback terms.
    """

    _validate_original_query(
        original_query
    )

    missing_topics = (
        _validate_diagnostics(
            diagnostics
        )
    )

    if not missing_topics:
        return None

    recognised_topics = (
        _recognised_missing_topics(
            missing_topics
        )
    )

    if not recognised_topics:
        return None

    selected_topic = (
        recognised_topics[0]
    )

    refined_query = (
        _topic_search_phrase(
            selected_topic
        )
    )

    cleaned_refined_query = " ".join(
        refined_query.split()
    )

    if not cleaned_refined_query:
        return None

    return cleaned_refined_query