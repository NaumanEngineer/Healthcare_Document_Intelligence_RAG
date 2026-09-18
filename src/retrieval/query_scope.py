from __future__ import annotations


IN_SCOPE_TERMS = {
    "operational",
    "escalation",
    "staffing",
    "workforce",
    "bed",
    "capacity",
    "winter",
    "pressure",
    "business continuity",
    "continuity",
    "governance",
    "site flow",
    "ambulance handover",
    "handover",
    "emergency department",
    "incident",
    "service disruption",
}

OUT_OF_SCOPE_TERMS = {
    "medication",
    "medicine",
    "prescribe",
    "prescribed",
    "prescribing",
    "antibiotic",
    "dose",
    "dosage",
    "treatment",
    "diagnosis",
    "clinical advice",
    "current chief executive",
    "who is the current",
}


def normalise_query(
    query: str,
) -> str:
    """
    Return a lower-case, whitespace-normalised query.
    """

    if not isinstance(query, str):
        raise TypeError(
            "query must be a string"
        )

    cleaned = " ".join(
        query.lower().split()
    )

    if not cleaned:
        raise ValueError(
            "query must not be blank"
        )

    return cleaned


def find_matching_terms(
    query: str,
    terms: set[str],
) -> list[str]:
    """
    Return matching phrases/terms found in the query.
    """

    normalised = normalise_query(
        query
    )

    matches = [
        term
        for term in terms
        if term in normalised
    ]

    return sorted(
        matches
    )


def assess_query_scope(
    query: str,
) -> dict:
    """
    Classify a question as IN_SCOPE or OUT_OF_SCOPE.

    The first implementation is deliberately deterministic
    and transparent.

    Clinical/prescribing requests and questions requiring
    current external information are blocked even when the
    question also contains operational terminology.
    """

    normalised = normalise_query(
        query
    )

    blocked_matches = (
        find_matching_terms(
            normalised,
            OUT_OF_SCOPE_TERMS,
        )
    )

    if blocked_matches:
        return {
            "scope": "OUT_OF_SCOPE",
            "allowed": False,
            "reason": (
                "Question contains terms outside the approved "
                "operational-policy scope."
            ),
            "matched_out_of_scope_terms": (
                blocked_matches
            ),
            "matched_in_scope_terms": [],
        }

    allowed_matches = (
        find_matching_terms(
            normalised,
            IN_SCOPE_TERMS,
        )
    )

    if allowed_matches:
        return {
            "scope": "IN_SCOPE",
            "allowed": True,
            "reason": (
                "Question matches the approved operational "
                "policy and escalation domain."
            ),
            "matched_out_of_scope_terms": [],
            "matched_in_scope_terms": (
                allowed_matches
            ),
        }

    return {
        "scope": "OUT_OF_SCOPE",
        "allowed": False,
        "reason": (
            "Question does not contain enough evidence of an "
            "approved operational-policy topic."
        ),
        "matched_out_of_scope_terms": [],
        "matched_in_scope_terms": [],
    }


def is_query_in_scope(
    query: str,
) -> bool:
    """
    Convenience boolean wrapper.
    """

    return bool(
        assess_query_scope(
            query
        )["allowed"]
    )
