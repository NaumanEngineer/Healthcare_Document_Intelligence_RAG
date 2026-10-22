"""Week 28 Day 3 — manager-facing response safety and contract tests."""

from __future__ import annotations

from copy import deepcopy

from src.application.manager_response import (
    MANAGER_RESPONSE_VERSION,
    OUTCOME_ABSTAIN,
    OUTCOME_ANSWER,
    OUTCOME_REVIEW_REQUIRED,
    build_manager_response,
)
from src.application.week28_demo_runner import (
    run_week28_three_outcome_demo,
)


def _demo_results() -> dict[str, dict]:
    report = (
        run_week28_three_outcome_demo()
    )

    return {
        result[
            "actual_outcome"
        ]: result[
            "result"
        ]
        for result in report[
            "results"
        ]
    }


def _required_fields() -> set[str]:
    return {
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


def test_answer_manager_response_contract():
    governed = (
        _demo_results()[
            OUTCOME_ANSWER
        ]
    )

    response = (
        build_manager_response(
            governed
        )
    )

    assert (
        _required_fields()
        <= set(
            response
        )
    )

    assert (
        response[
            "presentation_version"
        ]
        == MANAGER_RESPONSE_VERSION
    )

    assert (
        response[
            "outcome"
        ]
        == OUTCOME_ANSWER
    )

    assert (
        response[
            "answer"
        ]
        is not None
    )

    assert (
        response[
            "human_review_required"
        ]
        is False
    )

    assert (
        response[
            "authority_preserved"
        ]
        is True
    )


def test_review_manager_response_contract():
    governed = (
        _demo_results()[
            OUTCOME_REVIEW_REQUIRED
        ]
    )

    response = (
        build_manager_response(
            governed
        )
    )

    assert (
        _required_fields()
        <= set(
            response
        )
    )

    assert (
        response[
            "outcome"
        ]
        == OUTCOME_REVIEW_REQUIRED
    )

    assert (
        response[
            "answer"
        ]
        is None
    )

    assert (
        response[
            "human_review_required"
        ]
        is True
    )

    assert (
        response[
            "authority_preserved"
        ]
        is True
    )


def test_abstain_manager_response_contract():
    governed = (
        _demo_results()[
            OUTCOME_ABSTAIN
        ]
    )

    response = (
        build_manager_response(
            governed
        )
    )

    assert (
        _required_fields()
        <= set(
            response
        )
    )

    assert (
        response[
            "outcome"
        ]
        == OUTCOME_ABSTAIN
    )

    assert (
        response[
            "answer"
        ]
        is None
    )

    assert (
        response[
            "human_review_required"
        ]
        is True
    )

    assert (
        response[
            "authority_preserved"
        ]
        is True
    )


def test_answer_preserves_existing_citation():
    governed = (
        _demo_results()[
            OUTCOME_ANSWER
        ]
    )

    response = (
        build_manager_response(
            governed
        )
    )

    assert (
        len(
            response[
                "citations"
            ]
        )
        == 1
    )

    citation = (
        response[
            "citations"
        ][
            0
        ]
    )

    assert (
        citation[
            "citation_id"
        ]
        == "E1"
    )

    assert (
        citation[
            "document_id"
        ]
        == "W28-DEMO-DOC-A001"
    )


def test_answer_does_not_modify_governed_result():
    governed = deepcopy(
        _demo_results()[
            OUTCOME_ANSWER
        ]
    )

    original = deepcopy(
        governed
    )

    build_manager_response(
        governed
    )

    assert (
        governed
        == original
    )


def test_review_does_not_release_hidden_answer():
    governed = deepcopy(
        _demo_results()[
            OUTCOME_REVIEW_REQUIRED
        ]
    )

    governed[
        "response"
    ][
        "answer"
    ] = (
        "This text must never be "
        "released as authoritative."
    )

    response = (
        build_manager_response(
            governed
        )
    )

    assert (
        response[
            "outcome"
        ]
        == OUTCOME_REVIEW_REQUIRED
    )

    assert (
        response[
            "answer"
        ]
        is None
    )


def test_abstain_does_not_release_hidden_answer():
    governed = deepcopy(
        _demo_results()[
            OUTCOME_ABSTAIN
        ]
    )

    governed[
        "response"
    ][
        "answer"
    ] = (
        "Unsafe hidden substantive answer."
    )

    response = (
        build_manager_response(
            governed
        )
    )

    assert (
        response[
            "outcome"
        ]
        == OUTCOME_ABSTAIN
    )

    assert (
        response[
            "answer"
        ]
        is None
    )


def test_abstain_does_not_manufacture_citations():
    governed = (
        _demo_results()[
            OUTCOME_ABSTAIN
        ]
    )

    response = (
        build_manager_response(
            governed
        )
    )

    assert (
        response[
            "citations"
        ]
        == []
    )


def test_review_does_not_manufacture_citations():
    governed = (
        _demo_results()[
            OUTCOME_REVIEW_REQUIRED
        ]
    )

    response = (
        build_manager_response(
            governed
        )
    )

    assert (
        response[
            "citations"
        ]
        == []
    )


def test_invalid_input_fails_closed():
    response = (
        build_manager_response(
            "not-a-dictionary"
        )
    )

    assert (
        response[
            "outcome"
        ]
        == OUTCOME_ABSTAIN
    )

    assert (
        response[
            "answer"
        ]
        is None
    )

    assert (
        response[
            "authority_preserved"
        ]
        is True
    )

    assert (
        response[
            "presentation_fallback_used"
        ]
        is True
    )


def test_missing_outcome_fails_closed():
    response = (
        build_manager_response(
            {
                "response": {},
            }
        )
    )

    assert (
        response[
            "outcome"
        ]
        == OUTCOME_ABSTAIN
    )

    assert (
        response[
            "answer"
        ]
        is None
    )

    assert (
        response[
            "presentation_fallback_used"
        ]
        is True
    )


def test_unknown_outcome_fails_closed():
    response = (
        build_manager_response(
            {
                "final_outcome": (
                    "UNKNOWN"
                ),
                "response": {},
            }
        )
    )

    assert (
        response[
            "outcome"
        ]
        == OUTCOME_ABSTAIN
    )

    assert (
        response[
            "answer"
        ]
        is None
    )

    assert (
        response[
            "original_outcome"
        ]
        == "UNKNOWN"
    )


def test_missing_response_fails_closed():
    response = (
        build_manager_response(
            {
                "final_outcome": (
                    OUTCOME_ANSWER
                ),
            }
        )
    )

    assert (
        response[
            "outcome"
        ]
        == OUTCOME_ABSTAIN
    )

    assert (
        response[
            "answer"
        ]
        is None
    )

    assert (
        response[
            "presentation_fallback_used"
        ]
        is True
    )


def test_answer_manager_response_uses_existing_sections():
    governed = (
        _demo_results()[
            OUTCOME_ANSWER
        ]
    )

    response = (
        build_manager_response(
            governed
        )
    )

    assert isinstance(
        response[
            "answer"
        ],
        dict,
    )

    assert (
        "management_summary"
        in response[
            "answer"
        ]
    )

    assert (
        "evidence_based_explanation"
        in response[
            "answer"
        ]
    )

    assert (
        "sources"
        in response[
            "answer"
        ]
    )


def test_answer_citations_are_copied_not_shared():
    governed = deepcopy(
        _demo_results()[
            OUTCOME_ANSWER
        ]
    )

    response = (
        build_manager_response(
            governed
        )
    )

    response[
        "citations"
    ][
        0
    ][
        "document_id"
    ] = "MUTATED"

    original_sources = (
        governed[
            "response"
        ][
            "sections"
        ][
            "sources"
        ]
    )

    assert (
        original_sources[
            0
        ][
            "document_id"
        ]
        == "W28-DEMO-DOC-A001"
    )


def test_three_real_demo_outcomes_preserve_authority():
    report = (
        run_week28_three_outcome_demo()
    )

    for case in report[
        "results"
    ]:
        manager_response = (
            build_manager_response(
                case[
                    "result"
                ]
            )
        )

        assert (
            manager_response[
                "authority_preserved"
            ]
            is True
        )

        if (
            case[
                "actual_outcome"
            ]
            == OUTCOME_ANSWER
        ):
            assert (
                manager_response[
                    "outcome"
                ]
                == OUTCOME_ANSWER
            )

        elif (
            case[
                "actual_outcome"
            ]
            == OUTCOME_REVIEW_REQUIRED
        ):
            assert (
                manager_response[
                    "outcome"
                ]
                == OUTCOME_REVIEW_REQUIRED
            )

            assert (
                manager_response[
                    "answer"
                ]
                is None
            )

        else:
            assert (
                manager_response[
                    "outcome"
                ]
                == OUTCOME_ABSTAIN
            )

            assert (
                manager_response[
                    "answer"
                ]
                is None
            )


def test_presentation_layer_does_not_change_canonical_result():
    report = (
        run_week28_three_outcome_demo()
    )

    for case in report[
        "results"
    ]:
        governed = deepcopy(
            case[
                "result"
            ]
        )

        snapshot = deepcopy(
            governed
        )

        build_manager_response(
            governed
        )

        assert (
            governed
            == snapshot
        )