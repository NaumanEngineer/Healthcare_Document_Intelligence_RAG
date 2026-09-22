"""Deterministic topic-coverage checks, not entailment or lifecycle validation.

Similarity scores and document IDs do not affect the decision. Every extracted
required topic must occur in retrieved title/text; coverage may span documents.
Lifecycle filtering and query-scope checks remain separate responsibilities.
"""
from __future__ import annotations

import re


# Aliases are matched independently as whole phrases after normalisation.
# Multiple aliases for one concept count as a single required topic.
CONCEPT_ALIASES = {
    "operational_escalation": (
        "operational escalation", "escalation policy", "escalation guidance",
        "escalation process", "escalation",
    ),
    "operational_leadership": ("operational leadership", "operational leaders"),
    "workforce": (
        "workforce", "workforce pressure", "workforce shortage",
        "workforce shortages", "staffing", "staffing gaps", "critical staffing",
        "rota gaps",
    ),
    "bed_capacity": (
        "bed capacity", "hospital beds", "unsafe capacity", "capacity pressure",
    ),
    "winter_pressure": ("winter pressure",),
    "severe_weather": ("severe weather", "weather disruption"),
    "business_continuity": (
        "business continuity", "major disruption", "routine services",
        "continuity arrangements", "essential services", "service disruption",
        "services are disrupted",
    ),
    "ambulance_handover": (
        "ambulance handover", "emergency transport", "transfer delays", "crews",
    ),
    "emergency_department": ("emergency department", "emergency pressure"),
    "infection_surge": ("infection surge",),
    "site_flow": ("site flow", "patient flow"),
    "operational_pressure": (
        "operational pressure", "system pressure", "system pressures",
        "multiple pressures",
    ),
    "cybersecurity": ("cyber-security", "cyber security", "cybersecurity"),
    "electronic_patient_record": (
        "electronic patient record", "electronic patient records", "epr",
    ),
    "oxygen_supply": ("medical oxygen supply", "oxygen supply"),
}

# Contextual framing is optional when a more-specific query concept is present.
CONTEXTUAL_CONCEPTS = {"operational_pressure"}

# Query boilerplate, generic operational terms and lifecycle-manipulation words
# are not evidence topics. Their exclusion does not authorise those requests.
IGNORED_TERMS = set("""
what which where when how who why is are was were be been being the a an
and or of to for from in on at by with as into after during through
should would could can cannot must do does did not no that this these those
it its their there any all both together instead than then
operational policy policies procedure procedures guidance approved hospital
response managing management managers manager staff look covers cover defines
define consider considered use using follow process processes framework
major complete system systems incident incidents pressure pressures
shortage shortages delays delay patients patient remain transferring promptly
care normally normal continue services service delivery incoming causing
ignore document documents status draft authoritative superseded mention
newer version exists
followed used severe under applies describes threaten deteriorating same time
belong period periods responsibilities disrupted if summarise summarize create
coordinates within approaching unsafe begin gaps rota different increase
managed occur actions becomes operations teams across plan
""".split())


def _normalise(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _concept_terms(text: str) -> set[str]:
    normalised = _normalise(text)
    return {
        concept for concept, aliases in CONCEPT_ALIASES.items()
        if any(
            re.search(r"\b" + re.escape(_normalise(alias)) + r"\b", normalised)
            for alias in aliases
        )
    }


def _lexical_terms(text: str) -> set[str]:
    return {
        term for term in _normalise(text).split()
        if len(term) > 1 and not term.isdigit() and term not in IGNORED_TERMS
    }


def assess_evidence_sufficiency(
    question: str,
    results: list[dict],
) -> dict:
    """Require specific query concepts across retrieved titles/text.

    Contextual concepts are required only when no more-specific concept exists.

    Only when no concept is recognised, require all remaining lexical topics.
    Evidence extraction uses the same mode as the question, so a concept in
    evidence cannot hide lexical terms needed by a fallback query.

    Reasons report missing topics. This conservative lexical heuristic cannot
    establish factual support, detect negation, or verify source authority.
    """
    if not isinstance(question, str):
        raise TypeError("question must be a string")
    if not question.strip():
        raise ValueError("question must not be blank")
    if not isinstance(results, list) or any(
        not isinstance(result, dict) for result in results
    ):
        raise TypeError("results must be a list of dictionaries")

    query_concepts = _concept_terms(question)
    extract_terms = _concept_terms if query_concepts else _lexical_terms
    specific_concepts = query_concepts - CONTEXTUAL_CONCEPTS
    query_terms = specific_concepts or query_concepts or _lexical_terms(question)
    evidence_terms: set[str] = set()
    for result in results:
        for field in ("title", "text"):
            value = result.get(field)
            if isinstance(value, str):
                evidence_terms.update(extract_terms(value))

    matched = query_terms & evidence_terms
    missing = query_terms - evidence_terms
    sufficient = bool(results and query_terms and not missing)
    if not results:
        reason = "No retrieved evidence."
    elif not query_terms:
        reason = "No specific query topic could be identified."
    elif missing:
        reason = "Retrieved evidence lacks query topics: " + ", ".join(sorted(missing))
    else:
        reason = "Retrieved titles/text cover all specific query topics."

    return {
        "sufficient": sufficient,
        "decision": "SUFFICIENT" if sufficient else "INSUFFICIENT",
        "reason": reason,
        "matched_query_terms": sorted(matched),
        "evidence_terms": sorted(evidence_terms),
        "result_count": len(results),
    }
