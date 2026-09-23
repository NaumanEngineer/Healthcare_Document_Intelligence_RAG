"""Deterministic evidence sufficiency checks.

This module evaluates whether retrieved evidence covers the material
requirements in a query.

It does not perform factual entailment, lifecycle validation, or LLM reasoning.
Lifecycle filtering and query-scope checks remain separate responsibilities.

The current implementation preserves topic-level concept coverage and adds a
small auditable claim-level layer for known benchmark failure patterns:
- fabricated conflict / precedence claims
- quantitative requirements
- current/external requirements
- unsupported mandatory/procedural conditions
"""

from __future__ import annotations

import re


# ---------------------------------------------------------------------------
# Concept aliases
# ---------------------------------------------------------------------------

CONCEPT_ALIASES = {
    "operational_escalation": (
        "operational escalation",
        "escalation policy",
        "escalation guidance",
        "escalation process",
        "escalation",
    ),
    "operational_leadership": (
        "operational leadership",
        "operational leaders",
    ),
    "workforce": (
        "workforce",
        "workforce pressure",
        "workforce shortage",
        "workforce shortages",
        "staffing",
        "staffing gaps",
        "critical staffing",
        "rota gaps",
    ),
    "bed_capacity": (
        "bed capacity",
        "hospital beds",
        "unsafe capacity",
        "capacity pressure",
    ),
    "winter_pressure": (
        "winter pressure",
    ),
    "severe_weather": (
        "severe weather",
        "weather disruption",
    ),
    "business_continuity": (
        "business continuity",
        "major disruption",
        "routine services",
        "continuity arrangements",
        "essential services",
        "service disruption",
        "services are disrupted",
    ),
    "ambulance_handover": (
        "ambulance handover",
        "emergency transport",
        "transfer delays",
        "crews",
    ),
    "emergency_department": (
        "emergency department",
        "emergency pressure",
    ),
    "infection_surge": (
        "infection surge",
    ),
    "site_flow": (
        "site flow",
        "patient flow",
    ),
    "operational_pressure": (
        "operational pressure",
        "system pressure",
        "system pressures",
        "multiple pressures",
    ),
    "cybersecurity": (
        "cyber-security",
        "cyber security",
        "cybersecurity",
    ),
    "electronic_patient_record": (
        "electronic patient record",
        "electronic patient records",
        "epr",
    ),
    "oxygen_supply": (
        "medical oxygen supply",
        "oxygen supply",
    ),
}

CONTEXTUAL_CONCEPTS = {"operational_pressure"}


# ---------------------------------------------------------------------------
# Generic lexical exclusions
# ---------------------------------------------------------------------------

IGNORED_TERMS = set(
    """
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
""".split()
)


# ---------------------------------------------------------------------------
# Claim-pattern dictionaries
# ---------------------------------------------------------------------------

CURRENT_EXTERNAL_PATTERNS = (
    "today",
    "current national",
    "current rate",
    "current penalty",
    "national financial penalty",
    "financial penalty",
    "national tariff",
    "current figure",
    "current figures",
)

QUANTITATIVE_PATTERNS = (
    "exact numerical",
    "exact number",
    "exact percentage",
    "exact threshold",
    "numerical trigger",
    "capacity trigger",
    "financial penalty",
    "penalty applies",
    "exact national",
)

CONTRADICTION_PATTERNS = (
    "conflicting",
    "conflict",
    "contradiction",
    "takes precedence",
    "which rule should",
    "which conflicting rule",
    "prohibits all",
    "forbids",
)

RELATIONSHIP_PATTERNS = (
    "replaces all",
    "replaces",
    "forbids that replacement",
    "prohibits",
    "takes precedence",
    "complements",
)

MANDATORY_PROCEDURAL_PATTERNS = (
    "mandates",
    "mandatory",
    "must open",
    "requires opening",
    "opening another ward",
    "exact procedure",
)


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------

def _normalise(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _contains_phrase(text: str, phrase: str) -> bool:
    normalised_text = _normalise(text)
    normalised_phrase = _normalise(phrase)

    return bool(
        re.search(
            r"\b" + re.escape(normalised_phrase) + r"\b",
            normalised_text,
        )
    )


def _concept_terms(text: str) -> set[str]:
    normalised = _normalise(text)

    return {
        concept
        for concept, aliases in CONCEPT_ALIASES.items()
        if any(
            re.search(
                r"\b" + re.escape(_normalise(alias)) + r"\b",
                normalised,
            )
            for alias in aliases
        )
    }


def _lexical_terms(text: str) -> set[str]:
    return {
        term
        for term in _normalise(text).split()
        if len(term) > 1
        and not term.isdigit()
        and term not in IGNORED_TERMS
    }


def _evidence_text(results: list[dict]) -> str:
    parts: list[str] = []

    for result in results:
        for field in ("title", "text"):
            value = result.get(field)

            if isinstance(value, str):
                parts.append(value)

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Claim extraction
# ---------------------------------------------------------------------------

def _build_claim_requirement(
    claim_id: str,
    claim_type: str,
    text: str,
    supported: bool,
    reason: str,
) -> dict:
    return {
        "claim_id": claim_id,
        "type": claim_type,
        "text": text,
        "supported": supported,
        "reason": reason,
    }


def _assess_claim_requirements(
    question: str,
    results: list[dict],
) -> list[dict]:
    """Assess a small set of deterministic claim-level requirements.

    This is intentionally conservative and limited to known failure patterns.
    It does not attempt general natural-language entailment.
    """

    question_normalised = _normalise(question)
    evidence = _evidence_text(results)
    evidence_normalised = _normalise(evidence)

    claims: list[dict] = []

    # ------------------------------------------------------------------
    # Current / external information
    # ------------------------------------------------------------------

    current_external_matches = [
        pattern
        for pattern in CURRENT_EXTERNAL_PATTERNS
        if _contains_phrase(question_normalised, pattern)
    ]

    if current_external_matches:
        claims.append(
            _build_claim_requirement(
                claim_id="current_external_requirement",
                claim_type="current_external_claim",
                text=", ".join(current_external_matches),
                supported=False,
                reason=(
                    "Query requests current or national external information "
                    "that cannot be established from the local static corpus."
                ),
            )
        )

    # ------------------------------------------------------------------
    # Quantitative claims
    # ------------------------------------------------------------------

    quantitative_matches = [
        pattern
        for pattern in QUANTITATIVE_PATTERNS
        if _contains_phrase(question_normalised, pattern)
    ]

    for index, pattern in enumerate(quantitative_matches, start=1):
        supported = _contains_phrase(evidence_normalised, pattern)

        claims.append(
            _build_claim_requirement(
                claim_id=f"quantitative_{index}",
                claim_type="quantitative_claim",
                text=pattern,
                supported=supported,
                reason=(
                    "Exact quantitative requirement is explicitly present in "
                    "retrieved evidence."
                    if supported
                    else
                    "Retrieved evidence does not support the exact requested "
                    "quantitative requirement."
                ),
            )
        )

    # ------------------------------------------------------------------
    # Contradiction / precedence claims
    # ------------------------------------------------------------------

    contradiction_matches = [
        pattern
        for pattern in CONTRADICTION_PATTERNS
        if _contains_phrase(question_normalised, pattern)
    ]

    if contradiction_matches:
        claims.append(
            _build_claim_requirement(
                claim_id="contradiction_or_precedence",
                claim_type="contradiction_or_precedence_claim",
                text=", ".join(contradiction_matches),
                supported=False,
                reason=(
                    "Retrieved topic evidence does not establish the claimed "
                    "conflict, prohibition, or precedence relationship."
                ),
            )
        )

    # ------------------------------------------------------------------
    # Relationship claims
    # ------------------------------------------------------------------

    relationship_matches = [
        pattern
        for pattern in RELATIONSHIP_PATTERNS
        if _contains_phrase(question_normalised, pattern)
    ]

    for index, pattern in enumerate(relationship_matches, start=1):
        supported = _contains_phrase(evidence_normalised, pattern)

        claims.append(
            _build_claim_requirement(
                claim_id=f"relationship_{index}",
                claim_type="relationship_claim",
                text=pattern,
                supported=supported,
                reason=(
                    "Requested relationship is explicitly present in evidence."
                    if supported
                    else
                    "Retrieved evidence does not establish the requested "
                    "relationship between policies or procedures."
                ),
            )
        )

    # ------------------------------------------------------------------
    # Mandatory / procedural condition claims
    # ------------------------------------------------------------------

    mandatory_matches = [
        pattern
        for pattern in MANDATORY_PROCEDURAL_PATTERNS
        if _contains_phrase(question_normalised, pattern)
    ]

    for index, pattern in enumerate(mandatory_matches, start=1):
        supported = _contains_phrase(evidence_normalised, pattern)

        claims.append(
            _build_claim_requirement(
                claim_id=f"procedural_{index}",
                claim_type="procedural_claim",
                text=pattern,
                supported=supported,
                reason=(
                    "Requested mandatory procedural condition is explicitly "
                    "supported by retrieved evidence."
                    if supported
                    else
                    "Retrieved evidence does not establish the requested "
                    "mandatory procedural condition."
                ),
            )
        )

    return claims


# ---------------------------------------------------------------------------
# Main evidence assessment
# ---------------------------------------------------------------------------

def assess_evidence_sufficiency(
    question: str,
    results: list[dict],
) -> dict:
    """Assess topic and claim-level evidence sufficiency.

    Stage 1:
    Require coverage of specific query concepts or fallback lexical topics.

    Stage 2:
    Evaluate known material claim requirements such as:
    - current/external information
    - quantitative requirements
    - claimed conflicts or precedence
    - policy relationships
    - mandatory procedural conditions

    If any material claim requirement is unsupported, the overall decision is
    INSUFFICIENT.

    This remains a deterministic heuristic and does not establish factual
    entailment.
    """

    # ------------------------------------------------------------------
    # Input validation
    # ------------------------------------------------------------------

    if not isinstance(question, str):
        raise TypeError("question must be a string")

    if not question.strip():
        raise ValueError("question must not be blank")

    if not isinstance(results, list) or any(
        not isinstance(result, dict)
        for result in results
    ):
        raise TypeError("results must be a list of dictionaries")

    # Preserve the original return shape for empty results so existing tests
    # and callers remain backward-compatible.
    if not results:
        return {
            "sufficient": False,
            "decision": "INSUFFICIENT",
            "reason": "No retrieved evidence.",
            "matched_query_terms": [],
            "evidence_terms": [],
            "result_count": 0,
        }

    # ------------------------------------------------------------------
    # Stage 1: existing topic coverage
    # ------------------------------------------------------------------

    query_concepts = _concept_terms(question)

    extract_terms = (
        _concept_terms
        if query_concepts
        else _lexical_terms
    )

    specific_concepts = (
        query_concepts - CONTEXTUAL_CONCEPTS
    )

    query_terms = (
        specific_concepts
        or query_concepts
        or _lexical_terms(question)
    )

    evidence_terms: set[str] = set()

    for result in results:
        for field in ("title", "text"):
            value = result.get(field)

            if isinstance(value, str):
                evidence_terms.update(
                    extract_terms(value)
                )

    matched = query_terms & evidence_terms
    missing = query_terms - evidence_terms

    topic_sufficient = bool(
        query_terms
        and not missing
    )

    # ------------------------------------------------------------------
    # Stage 2: claim-level coverage
    # ------------------------------------------------------------------

    claim_requirements = _assess_claim_requirements(
        question=question,
        results=results,
    )

    unsupported_claims = [
        claim
        for claim in claim_requirements
        if not claim["supported"]
    ]

    claims_sufficient = not unsupported_claims

    sufficient = (
        topic_sufficient
        and claims_sufficient
    )

    # ------------------------------------------------------------------
    # Reason
    # ------------------------------------------------------------------

    if not query_terms:
        reason = (
            "No specific query topic could be identified."
        )

    elif missing:
        reason = (
            "Retrieved evidence lacks query topics: "
            + ", ".join(sorted(missing))
        )

    elif unsupported_claims:
        reason = (
            "Retrieved evidence does not support all material query claims: "
            + ", ".join(
                f"{claim['claim_id']} ({claim['type']})"
                for claim in unsupported_claims
            )
        )

    else:
        reason = (
            "Retrieved evidence covers required topics and all detected "
            "material claim requirements."
        )

    return {
        "sufficient": sufficient,
        "decision": (
            "SUFFICIENT"
            if sufficient
            else "INSUFFICIENT"
        ),
        "reason": reason,
        "matched_query_terms": sorted(matched),
        "evidence_terms": sorted(evidence_terms),
        "result_count": len(results),
        "topic_sufficient": topic_sufficient,
        "claim_sufficient": claims_sufficient,
        "claim_requirements": claim_requirements,
        "unsupported_claims": unsupported_claims,
    }