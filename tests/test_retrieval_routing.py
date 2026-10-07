from src.retrieval.retrieval_routing import (
    ROUTE_BOUNDED_AGENTIC,
    ROUTE_HYBRID_RESCUE,
    ROUTE_RELATIONSHIP_AWARE,
    ROUTE_RETURN_INITIAL,
    ROUTE_STOP_INSUFFICIENT,
    diagnose_retrieval_route,
)


def _result(
    *,
    chunk_id="DOC-003::P1",
    document_id="DOC-003",
):
    return {
        "chunk_id": chunk_id,
        "document_id": document_id,
        "status": "Active",
        "text": "Workforce escalation staffing pressure response.",
    }


def _assessment(
    *,
    sufficient=False,
    unsupported_claims=None,
):
    return {
        "sufficient": sufficient,
        "decision": (
            "SUFFICIENT"
            if sufficient
            else "INSUFFICIENT"
        ),
        "matched_query_terms": [],
        "evidence_terms": [],
        "result_count": 1,
        "topic_sufficient": sufficient,
        "claim_sufficient": sufficient,
        "claim_requirements": [],
        "unsupported_claims": (
            unsupported_claims or []
        ),
    }


def test_sufficient_evidence_returns_initial():
    decision = diagnose_retrieval_route(
        "What does the workforce escalation procedure say?",
        [_result()],
        _assessment(sufficient=True),
    )

    assert (
        decision["route"]
        == ROUTE_RETURN_INITIAL
    )


def test_current_external_claim_hard_stops():
    assessment = _assessment(
        unsupported_claims=[
            {
                "claim_id": "current_external_requirement",
                "type": "current_external_claim",
                "text": "current national guidance",
                "supported": False,
                "reason": "External current information required.",
            }
        ]
    )

    decision = diagnose_retrieval_route(
        "What is the current national guidance?",
        [_result()],
        assessment,
    )

    assert (
        decision["route"]
        == ROUTE_STOP_INSUFFICIENT
    )


def test_precedence_claim_hard_stops():
    assessment = _assessment(
        unsupported_claims=[
            {
                "claim_id": "contradiction_or_precedence",
                "type": "contradiction_or_precedence_claim",
                "text": "takes precedence",
                "supported": False,
                "reason": "Unsupported precedence claim.",
            }
        ]
    )

    decision = diagnose_retrieval_route(
        "Which policy takes precedence?",
        [_result()],
        assessment,
    )

    assert (
        decision["route"]
        == ROUTE_STOP_INSUFFICIENT
    )


def test_relationship_claim_routes_to_relationship_aware():
    assessment = _assessment(
        unsupported_claims=[
            {
                "claim_id": "relationship_1",
                "type": "relationship_claim",
                "text": "complements",
                "supported": False,
                "reason": "Relationship not yet established.",
            }
        ]
    )

    decision = diagnose_retrieval_route(
        "How does the workforce escalation procedure "
        "complement the contingency procedure?",
        [_result(document_id="DOC-003")],
        assessment,
        query_refiner=lambda query, diagnostics: None,
    )

    assert (
        decision["route"]
        == ROUTE_RELATIONSHIP_AWARE
    )

    assert (
        decision["relationship_available"]
        is True
    )


def test_relationship_claim_without_registry_edge_does_not_force_relationship_route():
    assessment = _assessment(
        unsupported_claims=[
            {
                "claim_id": "relationship_1",
                "type": "relationship_claim",
                "text": "complements",
                "supported": False,
                "reason": "Relationship not yet established.",
            }
        ]
    )

    decision = diagnose_retrieval_route(
        "How do these policies complement each other?",
        [_result(document_id="DOC-002")],
        assessment,
        query_refiner=lambda query, diagnostics: None,
    )

    assert (
        decision["route"]
        != ROUTE_RELATIONSHIP_AWARE
    )


def test_recoverable_missing_topic_routes_to_agentic():
    assessment = _assessment()

    decision = diagnose_retrieval_route(
        "What should happen during severe weather staffing pressure?",
        [_result()],
        assessment,
        query_refiner=(
            lambda query, diagnostics:
            "severe weather staffing escalation"
        ),
    )

    assert (
        decision["route"]
        == ROUTE_BOUNDED_AGENTIC
    )


def test_same_query_gap_routes_to_hybrid_rescue_when_refinement_unavailable():
    assessment = _assessment()

    decision = diagnose_retrieval_route(
        "Explain staffing escalation.",
        [_result()],
        assessment,
        query_refiner=lambda query, diagnostics: None,
    )

    assert (
        decision["route"]
        == ROUTE_HYBRID_RESCUE
    )


def test_empty_results_without_recovery_stop():
    assessment = {
        "sufficient": False,
        "decision": "INSUFFICIENT",
        "reason": "No retrieved evidence.",
        "matched_query_terms": [],
        "evidence_terms": [],
        "result_count": 0,
        "unsupported_claims": [],
    }

    decision = diagnose_retrieval_route(
        "Explain an unknown topic.",
        [],
        assessment,
        query_refiner=lambda query, diagnostics: None,
    )

    assert (
        decision["route"]
        == ROUTE_STOP_INSUFFICIENT
    )


def test_hard_block_priority_is_above_relationship_route():
    assessment = _assessment(
        unsupported_claims=[
            {
                "claim_id": "contradiction_or_precedence",
                "type": "contradiction_or_precedence_claim",
                "text": "takes precedence",
                "supported": False,
                "reason": "Unsupported precedence claim.",
            },
            {
                "claim_id": "relationship_1",
                "type": "relationship_claim",
                "text": "complements",
                "supported": False,
                "reason": "Relationship not established.",
            },
        ]
    )

    decision = diagnose_retrieval_route(
        "Does one procedure take precedence "
        "and complement the other?",
        [_result(document_id="DOC-003")],
        assessment,
        query_refiner=lambda query, diagnostics: (
            "workforce contingency relationship"
        ),
    )

    assert (
        decision["route"]
        == ROUTE_STOP_INSUFFICIENT
    )


def test_sufficient_evidence_has_priority_over_other_signals():
    assessment = _assessment(
        sufficient=True,
        unsupported_claims=[
            {
                "claim_id": "relationship_1",
                "type": "relationship_claim",
                "text": "complements",
                "supported": False,
                "reason": "Synthetic contradictory test state.",
            }
        ],
    )

    decision = diagnose_retrieval_route(
        "How do the procedures complement each other?",
        [_result(document_id="DOC-003")],
        assessment,
    )

    assert (
        decision["route"]
        == ROUTE_RETURN_INITIAL
    )


def test_query_must_be_string():
    try:
        diagnose_retrieval_route(
            123,
            [_result()],
            _assessment(),
        )
    except TypeError as exc:
        assert "query must be a string" in str(exc)
    else:
        raise AssertionError(
            "Expected TypeError"
        )


def test_empty_query_rejected():
    try:
        diagnose_retrieval_route(
            "   ",
            [_result()],
            _assessment(),
        )
    except ValueError as exc:
        assert "query must not be empty" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_initial_results_must_be_list():
    try:
        diagnose_retrieval_route(
            "test query",
            {"chunk_id": "X"},
            _assessment(),
        )
    except TypeError as exc:
        assert "initial_results must be a list" in str(exc)
    else:
        raise AssertionError(
            "Expected TypeError"
        )


def test_each_result_must_be_dict():
    try:
        diagnose_retrieval_route(
            "test query",
            ["not-a-dict"],
            _assessment(),
        )
    except TypeError as exc:
        assert (
            "each initial retrieval result must be a dictionary"
            in str(exc)
        )
    else:
        raise AssertionError(
            "Expected TypeError"
        )


def test_assessment_must_be_dict():
    try:
        diagnose_retrieval_route(
            "test query",
            [_result()],
            [],
        )
    except TypeError as exc:
        assert "assessment must be a dictionary" in str(exc)
    else:
        raise AssertionError(
            "Expected TypeError"
        )


def test_assessment_requires_sufficient():
    try:
        diagnose_retrieval_route(
            "test query",
            [_result()],
            {},
        )
    except ValueError as exc:
        assert "assessment must contain 'sufficient'" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_assessment_sufficient_must_be_boolean():
    try:
        diagnose_retrieval_route(
            "test query",
            [_result()],
            {
                "sufficient": "no",
            },
        )
    except TypeError as exc:
        assert (
            "assessment['sufficient'] must be a boolean"
            in str(exc)
        )
    else:
        raise AssertionError(
            "Expected TypeError"
        )


def test_unsupported_claims_must_be_list_when_present():
    try:
        diagnose_retrieval_route(
            "test query",
            [_result()],
            {
                "sufficient": False,
                "unsupported_claims": "bad",
            },
        )
    except TypeError as exc:
        assert "unsupported_claims must be a list" in str(exc)
    else:
        raise AssertionError(
            "Expected TypeError"
        )


def test_non_callable_query_refiner_rejected_when_needed():
    assessment = _assessment()

    try:
        diagnose_retrieval_route(
            "missing weather staffing evidence",
            [_result()],
            assessment,
            query_refiner="not-callable",
        )
    except TypeError as exc:
        assert "query_refiner must be callable" in str(exc)
    else:
        raise AssertionError(
            "Expected TypeError"
        )


def test_same_refined_query_is_not_treated_as_recoverable():
    assessment = _assessment()

    query = "Explain staffing escalation."

    decision = diagnose_retrieval_route(
        query,
        [_result()],
        assessment,
        query_refiner=(
            lambda original, diagnostics:
            "  Explain   staffing escalation. "
        ),
    )

    assert (
        decision["route"]
        == ROUTE_HYBRID_RESCUE
    )


def test_audit_contains_expected_fields():
    decision = diagnose_retrieval_route(
        "Explain staffing escalation.",
        [_result()],
        _assessment(),
        query_refiner=lambda query, diagnostics: None,
    )

    assert set(decision) == {
        "route",
        "reason",
        "initial_evidence_sufficient",
        "missing_topics",
        "unsupported_claim_types",
        "relationship_claim_unsupported",
        "relationship_available",
    }