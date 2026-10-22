"""Week 28 Day 3 — deterministic manager-facing response presentation.

This module converts a final governed RAG application result into a concise,
management-friendly presentation object.

It is deliberately downstream of retrieval, evidence construction, generation,
assurance, and final governance.

It does not:
- retrieve evidence
- call an LLM
- perform assurance
- resolve evidence conflicts
- manufacture citations
- change the governed outcome
- increase application authority

Core principle:

    Improve presentation, not authority.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


OUTCOME_ANSWER = "ANSWER"
OUTCOME_REVIEW_REQUIRED = "REVIEW_REQUIRED"
OUTCOME_ABSTAIN = "ABSTAIN"

ALLOWED_OUTCOMES = {
    OUTCOME_ANSWER,
    OUTCOME_REVIEW_REQUIRED,
    OUTCOME_ABSTAIN,
}

MANAGER_RESPONSE_VERSION = "week28-day3-v1"


def _require_mapping(
    value: Any,
    field_name: str,
) -> dict:
    """Require a dictionary value."""

    if not isinstance(
        value,
        dict,
    ):
        raise ValueError(
            f"{field_name} must be a dictionary."
        )

    return value


def _require_non_empty_string(
    value: Any,
    field_name: str,
) -> str:
    """Require a non-empty string."""

    if not isinstance(
        value,
        str,
    ):
        raise ValueError(
            f"{field_name} must be a string."
        )

    cleaned = value.strip()

    if not cleaned:
        raise ValueError(
            f"{field_name} must not be blank."
        )

    return cleaned


def _safe_string(
    value: Any,
) -> str | None:
    """Return a cleaned string or None."""

    if not isinstance(
        value,
        str,
    ):
        return None

    cleaned = value.strip()

    return (
        cleaned
        if cleaned
        else None
    )


def _safe_list(
    value: Any,
) -> list:
    """Return a deep-copied list or an empty list."""

    if not isinstance(
        value,
        list,
    ):
        return []

    return deepcopy(
        value
    )


def _safe_mapping(
    value: Any,
) -> dict:
    """Return a deep-copied mapping or an empty mapping."""

    if not isinstance(
        value,
        dict,
    ):
        return {}

    return deepcopy(
        value
    )


def _extract_sections(
    response: dict,
) -> dict:
    """Return structured response sections when present."""

    sections = response.get(
        "sections"
    )

    return _safe_mapping(
        sections
    )


def _extract_citations(
    response: dict,
) -> list:
    """Preserve citations or sources already present in the governed response.

    Citation identity is never created or inferred by the presentation layer.

    Mature deterministic responses may expose source records inside:
        response["sections"]["sources"]

    Provider-backed responses may expose:
        response["citations"]

    Both are already-governed representations and may therefore be preserved.
    """

    citations = response.get(
        "citations"
    )

    if isinstance(
        citations,
        list,
    ) and citations:
        return deepcopy(
            citations
        )

    sections = (
        _extract_sections(
            response
        )
    )

    sources = sections.get(
        "sources"
    )

    if isinstance(
        sources,
        list,
    ) and sources:
        return deepcopy(
            sources
        )

    direct_sources = response.get(
        "sources"
    )

    if isinstance(
        direct_sources,
        list,
    ) and direct_sources:
        return deepcopy(
            direct_sources
        )

    return []


def _extract_answer_payload(
    response: dict,
) -> Any:
    """Extract an already-governed answer payload without rewriting it."""

    if (
        "answer"
        in response
        and response[
            "answer"
        ] is not None
    ):
        return deepcopy(
            response[
                "answer"
            ]
        )

    if (
        "sections"
        in response
        and response[
            "sections"
        ] is not None
    ):
        return deepcopy(
            response[
                "sections"
            ]
        )

    return deepcopy(
        response
    )


def _extract_evidence_count(
    governed_result: dict,
) -> int | None:
    """Extract a safe evidence count when already present."""

    evidence_summary = (
        governed_result.get(
            "evidence_summary"
        )
    )

    if not isinstance(
        evidence_summary,
        dict,
    ):
        return None

    for key in (
        "evidence_count",
        "total_evidence",
        "approved_evidence_count",
        "item_count",
    ):
        value = (
            evidence_summary.get(
                key
            )
        )

        if (
            isinstance(
                value,
                int,
            )
            and not isinstance(
                value,
                bool,
            )
            and value >= 0
        ):
            return value

    return None


def _build_evidence_basis(
    governed_result: dict,
    *,
    default_message: str,
) -> str:
    """Build a safe evidence-basis sentence from existing metadata."""

    evidence_count = (
        _extract_evidence_count(
            governed_result
        )
    )

    if evidence_count is None:
        return default_message

    if evidence_count == 0:
        return (
            "No approved evidence items were available "
            "to support an answer."
        )

    if evidence_count == 1:
        return (
            "The governed application used 1 approved "
            "evidence item in reaching this outcome."
        )

    return (
        "The governed application used "
        f"{evidence_count} approved evidence items "
        "in reaching this outcome."
    )


def _extract_limitations(
    response: dict,
) -> list:
    """Return limitations already represented by the governed response."""

    limitations = []

    for container in (
        response,
        _extract_sections(
            response
        ),
    ):
        for key in (
            "limitations",
            "safety_notes",
            "uncertainty",
            "evidence_gaps_or_uncertainty",
            "missing_information",
            "missing_evidence",
        ):
            value = container.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                limitations.extend(
                    deepcopy(
                        value
                    )
                )

            elif isinstance(
                value,
                str,
            ):
                cleaned = (
                    value.strip()
                )

                if cleaned:
                    limitations.append(
                        cleaned
                    )

    unique = []

    for item in limitations:
        if item not in unique:
            unique.append(
                item
            )

    return unique


def _build_answer_response(
    governed_result: dict,
) -> dict:
    """Build manager presentation for a governed ANSWER."""

    response = _safe_mapping(
        governed_result.get(
            "response"
        )
    )

    return {
        "presentation_version": (
            MANAGER_RESPONSE_VERSION
        ),
        "outcome": (
            OUTCOME_ANSWER
        ),
        "headline": (
            "Supported guidance found"
        ),
        "summary": (
            "The available approved evidence was "
            "sufficient for the governed application "
            "to release an answer."
        ),
        "answer": (
            _extract_answer_payload(
                response
            )
        ),
        "evidence_basis": (
            _build_evidence_basis(
                governed_result,
                default_message=(
                    "The released answer is based on "
                    "evidence that passed the governed "
                    "application path."
                ),
            )
        ),
        "confidence_message": (
            "The available evidence was sufficient "
            "for a governed answer. Use the cited "
            "source material where further detail "
            "or confirmation is required."
        ),
        "next_action": (
            "Use the supported response together with "
            "its existing citations and retain the "
            "underlying source material for reference."
        ),
        "human_review_required": False,
        "citations": (
            _extract_citations(
                response
            )
        ),
        "limitations": (
            _extract_limitations(
                response
            )
        ),
        "authority_preserved": True,
    }


def _build_review_response(
    governed_result: dict,
) -> dict:
    """Build manager presentation for REVIEW_REQUIRED."""

    response = _safe_mapping(
        governed_result.get(
            "response"
        )
    )

    review_reason = (
        _safe_string(
            response.get(
                "why_human_review_is_required"
            )
        )
        or (
            "The available evidence requires human "
            "judgement before an authoritative "
            "operational answer can be released."
        )
    )

    review_focus = (
        _safe_string(
            response.get(
                "review_focus"
            )
        )
        or (
            "Review the relevant evidence, governance "
            "restrictions and any source relationships "
            "before operational use."
        )
    )

    evidence_summary = (
        _safe_string(
            response.get(
                "evidence_summary"
            )
        )
    )

    evidence_basis = (
        evidence_summary
        or _build_evidence_basis(
            governed_result,
            default_message=(
                "Relevant governed evidence exists, "
                "but it is not authorised for release "
                "as a combined operational answer."
            ),
        )
    )

    return {
        "presentation_version": (
            MANAGER_RESPONSE_VERSION
        ),
        "outcome": (
            OUTCOME_REVIEW_REQUIRED
        ),
        "headline": (
            "Human review required before using "
            "this information"
        ),
        "summary": (
            "Relevant evidence was identified, but "
            "the governed application did not permit "
            "release of an authoritative answer."
        ),
        "answer": None,
        "evidence_basis": (
            evidence_basis
        ),
        "confidence_message": (
            review_reason
        ),
        "next_action": (
            review_focus
        ),
        "human_review_required": True,
        "citations": (
            _extract_citations(
                response
            )
        ),
        "limitations": (
            _extract_limitations(
                response
            )
        ),
        "authority_preserved": True,
    }


def _build_abstain_response(
    governed_result: dict,
) -> dict:
    """Build manager presentation for a governed ABSTAIN."""

    response = _safe_mapping(
        governed_result.get(
            "response"
        )
    )

    reason = (
        _safe_string(
            response.get(
                "reason"
            )
        )
        or (
            "The available approved evidence does "
            "not permit a safe answer."
        )
    )

    next_action = (
        _safe_string(
            response.get(
                "what_is_needed_to_continue"
            )
        )
        or (
            "Provide sufficient approved evidence "
            "or route the question for appropriate "
            "human review."
        )
    )

    return {
        "presentation_version": (
            MANAGER_RESPONSE_VERSION
        ),
        "outcome": (
            OUTCOME_ABSTAIN
        ),
        "headline": (
            "Insufficient evidence for a safe answer"
        ),
        "summary": (
            _safe_string(
                response.get(
                    "unable_to_answer_safely"
                )
            )
            or (
                "The governed application cannot "
                "provide a safe answer from the "
                "available evidence."
            )
        ),
        "answer": None,
        "evidence_basis": (
            _build_evidence_basis(
                governed_result,
                default_message=reason,
            )
        ),
        "confidence_message": (
            reason
        ),
        "next_action": (
            next_action
        ),
        "human_review_required": True,
        "citations": [],
        "limitations": (
            _extract_limitations(
                response
            )
        ),
        "authority_preserved": True,
    }


def _build_fail_closed_response(
    governed_result: dict,
) -> dict:
    """Build a non-authoritative fallback presentation."""

    original_outcome = (
        governed_result.get(
            "final_outcome"
        )
        if isinstance(
            governed_result,
            dict,
        )
        else None
    )

    return {
        "presentation_version": (
            MANAGER_RESPONSE_VERSION
        ),
        "outcome": (
            OUTCOME_ABSTAIN
        ),
        "headline": (
            "Unable to present a safe response"
        ),
        "summary": (
            "The governed application result could "
            "not be safely converted into the "
            "manager-facing response format."
        ),
        "answer": None,
        "evidence_basis": (
            "No additional evidence interpretation "
            "has been performed by the presentation "
            "layer."
        ),
        "confidence_message": (
            "The presentation layer failed closed "
            "and has not increased application "
            "authority."
        ),
        "next_action": (
            "Use the underlying governed application "
            "result or route the case for technical "
            "review."
        ),
        "human_review_required": True,
        "citations": [],
        "limitations": [
            (
                "Manager-facing presentation could "
                "not be safely completed."
            )
        ],
        "authority_preserved": True,
        "original_outcome": (
            original_outcome
        ),
        "presentation_fallback_used": True,
    }


def _validate_authority_preservation(
    governed_result: dict,
    manager_response: dict,
) -> None:
    """Ensure presentation never increases governed authority."""

    original_outcome = (
        governed_result[
            "final_outcome"
        ]
    )

    presented_outcome = (
        manager_response[
            "outcome"
        ]
    )

    if (
        original_outcome
        == OUTCOME_REVIEW_REQUIRED
        and presented_outcome
        == OUTCOME_ANSWER
    ):
        raise ValueError(
            "Presentation increased authority from "
            "REVIEW_REQUIRED to ANSWER."
        )

    if (
        original_outcome
        == OUTCOME_ABSTAIN
        and presented_outcome
        != OUTCOME_ABSTAIN
    ):
        raise ValueError(
            "Presentation increased authority from "
            "ABSTAIN."
        )

    if (
        original_outcome
        != OUTCOME_ANSWER
        and manager_response.get(
            "answer"
        )
        is not None
    ):
        raise ValueError(
            "Non-answer outcome exposed answer content."
        )


def _validate_manager_response(
    manager_response: dict,
) -> None:
    """Validate the stable manager-facing response contract."""

    required_fields = {
        "presentation_version",
        "outcome",
        "headline",
        "summary",
        "answer",
        "evidence_basis",
        "confidence_message",
        "next_action",
        "human_review_required",
        "citations",
        "limitations",
        "authority_preserved",
    }

    missing = (
        required_fields
        - set(
            manager_response
        )
    )

    if missing:
        raise ValueError(
            "Manager response missing required fields: "
            + ", ".join(
                sorted(
                    missing
                )
            )
        )

    if (
        manager_response[
            "outcome"
        ]
        not in ALLOWED_OUTCOMES
    ):
        raise ValueError(
            "Manager response contains unsupported outcome."
        )

    for field_name in (
        "headline",
        "summary",
        "evidence_basis",
        "confidence_message",
        "next_action",
    ):
        _require_non_empty_string(
            manager_response[
                field_name
            ],
            field_name,
        )

    if not isinstance(
        manager_response[
            "human_review_required"
        ],
        bool,
    ):
        raise ValueError(
            "human_review_required must be boolean."
        )

    if not isinstance(
        manager_response[
            "citations"
        ],
        list,
    ):
        raise ValueError(
            "citations must be a list."
        )

    if not isinstance(
        manager_response[
            "limitations"
        ],
        list,
    ):
        raise ValueError(
            "limitations must be a list."
        )

    if (
        manager_response[
            "authority_preserved"
        ]
        is not True
    ):
        raise ValueError(
            "authority_preserved must be True."
        )


def build_manager_response(
    governed_result: dict,
) -> dict:
    """Build a deterministic manager-facing presentation."""

    try:
        result = _require_mapping(
            governed_result,
            "governed_result",
        )

        outcome = (
            _require_non_empty_string(
                result.get(
                    "final_outcome"
                ),
                "final_outcome",
            )
        )

        if outcome not in (
            ALLOWED_OUTCOMES
        ):
            raise ValueError(
                "Unsupported governed outcome."
            )

        response = result.get(
            "response"
        )

        if not isinstance(
            response,
            dict,
        ):
            raise ValueError(
                "governed_result.response must be a dictionary."
            )

        if (
            outcome
            == OUTCOME_ANSWER
        ):
            manager_response = (
                _build_answer_response(
                    result
                )
            )

        elif (
            outcome
            == OUTCOME_REVIEW_REQUIRED
        ):
            manager_response = (
                _build_review_response(
                    result
                )
            )

        else:
            manager_response = (
                _build_abstain_response(
                    result
                )
            )

        _validate_manager_response(
            manager_response
        )

        _validate_authority_preservation(
            result,
            manager_response,
        )

        return manager_response

    except Exception:
        fallback = (
            _build_fail_closed_response(
                governed_result
                if isinstance(
                    governed_result,
                    dict,
                )
                else {}
            )
        )

        _validate_manager_response(
            fallback
        )

        return fallback