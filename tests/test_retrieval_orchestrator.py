from src.retrieval.retrieval_orchestrator import (
    orchestrate_retrieval,
)


class DummyModel:
    pass


def _result(
    *,
    chunk_id="DOC-003::P1",
    document_id="DOC-003",
    text="Staffing escalation procedure.",
):
    return {
        "chunk_id": chunk_id,
        "document_id": document_id,
        "title": f"Policy {document_id}",
        "document_type": "Policy",
        "source_type": "Synthetic",
        "version": "1.0",
        "effective_date": "2026-01-01",
        "status": "Active",
        "source_file": f"{document_id}.txt",
        "page": 1,
        "chunk_number": 1,
        "text": text,
        "rrf_score": 0.03,
        "rank": 1,
    }


def _evidence(
    *,
    sufficient,
    unsupported_claims=None,
):
    if unsupported_claims is None:
        unsupported_claims = []

    return {
        "sufficient": sufficient,
        "decision": (
            "SUFFICIENT"
            if sufficient
            else "INSUFFICIENT"
        ),
        "matched_query_terms": (
            ["staffing"]
            if sufficient
            else []
        ),
        "evidence_terms": (
            ["staffing"]
            if sufficient
            else []
        ),
        "result_count": 1,
        "topic_sufficient": sufficient,
        "claim_sufficient": sufficient,
        "claim_requirements": [],
        "unsupported_claims": (
            unsupported_claims
        ),
    }


def test_out_of_scope_stops_before_retrieval(
    monkeypatch,
):
    def fail_if_called(**kwargs):
        raise AssertionError(
            "Hybrid should not run"
        )

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "hybrid_search",
        fail_if_called,
    )

    result = orchestrate_retrieval(
        query=(
            "What is the current NHS England performance?"
        ),
        chunks=[],
        embedded_chunks=[],
        model=DummyModel(),
        embedding_model="dummy",
    )

    assert result["results"] == []

    assert result["audit"][
        "selected_route"
    ] == "STOP_OUT_OF_SCOPE"

    assert result["audit"][
        "total_hybrid_retrieval_calls"
    ] == 0


def test_return_initial_route(
    monkeypatch,
):
    initial = [
        _result()
    ]

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "hybrid_search",
        lambda **kwargs: initial,
    )

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "assess_evidence_sufficiency",
        lambda query, results: _evidence(
            sufficient=True
        ),
    )

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "diagnose_retrieval_route",
        lambda *args, **kwargs: {
            "route": "RETURN_INITIAL",
            "reason": "sufficient",
        },
    )

    result = orchestrate_retrieval(
        query="Explain staffing escalation",
        chunks=[],
        embedded_chunks=[],
        model=DummyModel(),
        embedding_model="dummy",
    )

    assert result["results"] == initial

    assert result["audit"][
        "selected_route"
    ] == "RETURN_INITIAL"

    assert result["audit"][
        "total_hybrid_retrieval_calls"
    ] == 1

    assert result["audit"][
        "stop_reason"
    ] == "INITIAL_EVIDENCE_SUFFICIENT"


def test_stop_insufficient_route(
    monkeypatch,
):
    initial = [
        _result()
    ]

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "hybrid_search",
        lambda **kwargs: initial,
    )

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "assess_evidence_sufficiency",
        lambda query, results: _evidence(
            sufficient=False
        ),
    )

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "diagnose_retrieval_route",
        lambda *args, **kwargs: {
            "route": "STOP_INSUFFICIENT",
            "reason": "no safe route",
        },
    )

    result = orchestrate_retrieval(
        query="Explain staffing escalation",
        chunks=[],
        embedded_chunks=[],
        model=DummyModel(),
        embedding_model="dummy",
    )

    assert result["results"] == initial

    assert result["audit"][
        "selected_route"
    ] == "STOP_INSUFFICIENT"

    assert result["audit"][
        "total_hybrid_retrieval_calls"
    ] == 1

    assert result["audit"][
        "stop_reason"
    ] == "NO_SAFE_RETRIEVAL_EXPANSION"


def test_relationship_route_does_not_add_hybrid_call(
    monkeypatch,
):
    initial = [
        _result(
            chunk_id="DOC-011::P1",
            document_id="DOC-011",
        )
    ]

    expanded = [
        initial[0],
        _result(
            chunk_id="DOC-003::P1",
            document_id="DOC-003",
        ),
    ]

    evidence_calls = []

    def fake_evidence(
        query,
        results,
    ):
        evidence_calls.append(
            len(results)
        )

        return _evidence(
            sufficient=(
                len(results) > 1
            )
        )

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "hybrid_search",
        lambda **kwargs: initial,
    )

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "assess_evidence_sufficiency",
        fake_evidence,
    )

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "diagnose_retrieval_route",
        lambda *args, **kwargs: {
            "route": "RELATIONSHIP_AWARE",
            "reason": "relationship claim",
        },
    )

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "expand_results_with_relationships",
        lambda *args, **kwargs: {
            "results": expanded,
            "audit": {
                "expansion_count": 1,
                "stop_reason": (
                    "RELATED_EVIDENCE_ADDED"
                ),
            },
        },
    )

    result = orchestrate_retrieval(
        query="Explain staffing escalation relationship",
        chunks=[],
        embedded_chunks=[],
        model=DummyModel(),
        embedding_model="dummy",
    )

    assert result["results"] == expanded

    assert result["audit"][
        "selected_route"
    ] == "RELATIONSHIP_AWARE"

    assert result["audit"][
        "total_hybrid_retrieval_calls"
    ] == 1

    assert result["audit"][
        "stop_reason"
    ] == (
        "EVIDENCE_SUFFICIENT_AFTER_RELATIONSHIP_EXPANSION"
    )


def test_agentic_route_reuses_initial_retrieval(
    monkeypatch,
):
    initial = [
        _result()
    ]

    final_results = [
        initial[0],
        _result(
            chunk_id="DOC-011::P2",
            document_id="DOC-011",
        ),
    ]

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "hybrid_search",
        lambda **kwargs: initial,
    )

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "assess_evidence_sufficiency",
        lambda query, results: _evidence(
            sufficient=False
        ),
    )

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "diagnose_retrieval_route",
        lambda *args, **kwargs: {
            "route": "BOUNDED_AGENTIC",
            "reason": "recoverable missing topic",
        },
    )

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "continue_bounded_agentic_retrieval",
        lambda **kwargs: {
            "results": final_results,
            "audit": {
                "initial_retrieval_reused": True,
                "additional_retrieval_call_count": 1,
                "stop_reason": (
                    "EVIDENCE_SUFFICIENT_AFTER_REFINEMENT"
                ),
                "final_evidence": (
                    _evidence(
                        sufficient=True
                    )
                ),
            },
        },
    )

    result = orchestrate_retrieval(
        query="Explain weather staffing pressure",
        chunks=[],
        embedded_chunks=[],
        model=DummyModel(),
        embedding_model="dummy",
    )

    assert result["results"] == final_results

    assert result["audit"][
        "selected_route"
    ] == "BOUNDED_AGENTIC"

    assert result["audit"][
        "total_hybrid_retrieval_calls"
    ] == 2

    assert result["audit"][
        "route_audit"
    ][
        "initial_retrieval_reused"
    ] is True


def test_rescue_route_reuses_initial_hybrid(
    monkeypatch,
):
    initial = [
        _result()
    ]

    rescued = [
        initial[0],
        _result(
            chunk_id="DOC-011::P2",
            document_id="DOC-011",
        ),
    ]

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "hybrid_search",
        lambda **kwargs: initial,
    )

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "assess_evidence_sufficiency",
        lambda query, results: _evidence(
            sufficient=False
        ),
    )

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "diagnose_retrieval_route",
        lambda *args, **kwargs: {
            "route": "HYBRID_RESCUE",
            "reason": "same-query evidence gap",
        },
    )

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "continue_hybrid_search_evidence_rescue",
        lambda **kwargs: {
            "results": rescued,
            "audit": {
                "initial_retrieval_reused": True,
                "additional_hybrid_retrieval_call_count": 0,
                "additional_rrf_pool_call_count": 1,
                "final_evidence": (
                    _evidence(
                        sufficient=True
                    )
                ),
            },
        },
    )

    result = orchestrate_retrieval(
        query="Explain staffing pressure",
        chunks=[],
        embedded_chunks=[],
        model=DummyModel(),
        embedding_model="dummy",
    )

    assert result["results"] == rescued

    assert result["audit"][
        "selected_route"
    ] == "HYBRID_RESCUE"

    assert result["audit"][
        "total_hybrid_retrieval_calls"
    ] == 1

    assert result["audit"][
        "route_audit"
    ][
        "additional_rrf_pool_call_count"
    ] == 1

    assert result["audit"][
        "stop_reason"
    ] == "EVIDENCE_SUFFICIENT_AFTER_RESCUE"


def test_only_one_enhancement_route_runs(
    monkeypatch,
):
    initial = [
        _result()
    ]

    agentic_calls = []
    rescue_calls = []
    relationship_calls = []

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "hybrid_search",
        lambda **kwargs: initial,
    )

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "assess_evidence_sufficiency",
        lambda query, results: _evidence(
            sufficient=False
        ),
    )

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "diagnose_retrieval_route",
        lambda *args, **kwargs: {
            "route": "BOUNDED_AGENTIC",
            "reason": "recoverable missing topic",
        },
    )

    def fake_agentic(
        **kwargs,
    ):
        agentic_calls.append(
            True
        )

        return {
            "results": initial,
            "audit": {
                "initial_retrieval_reused": True,
                "additional_retrieval_call_count": 0,
                "stop_reason": (
                    "NO_COVERAGE_IMPROVEMENT"
                ),
                "final_evidence": (
                    _evidence(
                        sufficient=False
                    )
                ),
            },
        }

    def fake_rescue(
        **kwargs,
    ):
        rescue_calls.append(
            True
        )
        raise AssertionError(
            "Rescue must not run"
        )

    def fake_relationship(
        *args,
        **kwargs,
    ):
        relationship_calls.append(
            True
        )
        raise AssertionError(
            "Relationship route must not run"
        )

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "continue_bounded_agentic_retrieval",
        fake_agentic,
    )

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "continue_hybrid_search_evidence_rescue",
        fake_rescue,
    )

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "expand_results_with_relationships",
        fake_relationship,
    )

    result = orchestrate_retrieval(
        query="Explain weather staffing pressure",
        chunks=[],
        embedded_chunks=[],
        model=DummyModel(),
        embedding_model="dummy",
    )

    assert len(
        agentic_calls
    ) == 1

    assert rescue_calls == []
    assert relationship_calls == []

    assert result["audit"][
        "selected_route"
    ] == "BOUNDED_AGENTIC"


def test_unsupported_route_fails_closed(
    monkeypatch,
):
    initial = [
        _result()
    ]

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "hybrid_search",
        lambda **kwargs: initial,
    )

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "assess_evidence_sufficiency",
        lambda query, results: _evidence(
            sufficient=False
        ),
    )

    monkeypatch.setattr(
        "src.retrieval.retrieval_orchestrator."
        "diagnose_retrieval_route",
        lambda *args, **kwargs: {
            "route": "UNCONTROLLED_AGENT",
            "reason": "invalid route",
        },
    )

    try:
        orchestrate_retrieval(
            query="Explain staffing escalation",
            chunks=[],
            embedded_chunks=[],
            model=DummyModel(),
            embedding_model="dummy",
        )
    except RuntimeError as exc:
        assert (
            "Unsupported retrieval route"
            in str(exc)
        )
    else:
        raise AssertionError(
            "Unsupported route should fail closed"
        )