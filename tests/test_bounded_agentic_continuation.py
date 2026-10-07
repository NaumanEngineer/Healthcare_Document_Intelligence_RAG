from src.retrieval.bounded_agentic_retrieval import (
    continue_bounded_agentic_retrieval,
)


def _active_result(
    *,
    chunk_id="DOC-003::P1",
    document_id="DOC-003",
    text="Workforce escalation staffing pressure response.",
    status="Active",
):
    """Return a retrieval-ready synthetic chunk."""

    return {
        "chunk_id": chunk_id,
        "document_id": document_id,
        "title": f"Policy {document_id}",
        "document_type": "Policy",
        "source_type": "Synthetic",
        "version": "1.0",
        "effective_date": "2026-01-01",
        "status": status,
        "source_file": f"{document_id}.txt",
        "page": 1,
        "chunk_number": 1,
        "text": text,
        "rrf_score": 0.03,
        "rank": 1,
    }


class DummyModel:
    pass


def test_reuses_initial_results_when_evidence_is_sufficient(
    monkeypatch,
):
    initial_results = [
        _active_result()
    ]

    monkeypatch.setattr(
        "src.retrieval.bounded_agentic_retrieval."
        "assess_evidence_sufficiency",
        lambda query, results: {
            "sufficient": True,
            "decision": "SUFFICIENT",
            "matched_query_terms": [
                "staffing"
            ],
            "evidence_terms": [
                "staffing"
            ],
            "result_count": len(results),
            "topic_sufficient": True,
            "claim_sufficient": True,
            "claim_requirements": [],
            "unsupported_claims": [],
        },
    )

    monkeypatch.setattr(
        "src.retrieval.bounded_agentic_retrieval."
        "get_evidence_topic_diagnostics",
        lambda query, results: {
            "query_topics": [
                "staffing"
            ],
            "matched_topics": [
                "staffing"
            ],
            "missing_topics": [],
            "evidence_terms": [
                "staffing"
            ],
        },
    )

    def fail_if_called(**kwargs):
        raise AssertionError(
            "Hybrid retrieval should not run"
        )

    monkeypatch.setattr(
        "src.retrieval.bounded_agentic_retrieval."
        "hybrid_search",
        fail_if_called,
    )

    result = continue_bounded_agentic_retrieval(
        query="Explain staffing escalation",
        initial_results=initial_results,
        chunks=[],
        embedded_chunks=[],
        model=DummyModel(),
        embedding_model="dummy",
    )

    assert result["audit"][
        "initial_retrieval_reused"
    ] is True

    assert result["audit"][
        "additional_retrieval_call_count"
    ] == 0

    assert result["audit"][
        "stop_reason"
    ] == "INITIAL_EVIDENCE_SUFFICIENT"


def test_hard_block_does_not_run_second_retrieval(
    monkeypatch,
):
    initial_results = [
        _active_result()
    ]

    monkeypatch.setattr(
        "src.retrieval.bounded_agentic_retrieval."
        "assess_evidence_sufficiency",
        lambda query, results: {
            "sufficient": False,
            "decision": "INSUFFICIENT",
            "matched_query_terms": [
                "staffing"
            ],
            "evidence_terms": [
                "staffing"
            ],
            "result_count": len(results),
            "topic_sufficient": False,
            "claim_sufficient": False,
            "claim_requirements": [],
            "unsupported_claims": [
                {
                    "claim_id": (
                        "current_external_requirement"
                    ),
                    "type": (
                        "current_external_claim"
                    ),
                    "supported": False,
                }
            ],
        },
    )

    monkeypatch.setattr(
        "src.retrieval.bounded_agentic_retrieval."
        "get_evidence_topic_diagnostics",
        lambda query, results: {
            "query_topics": [
                "staffing",
                "pressure",
            ],
            "matched_topics": [
                "staffing"
            ],
            "missing_topics": [
                "pressure"
            ],
            "evidence_terms": [
                "staffing"
            ],
        },
    )

    def fail_if_called(**kwargs):
        raise AssertionError(
            "Hybrid retrieval should not run"
        )

    monkeypatch.setattr(
        "src.retrieval.bounded_agentic_retrieval."
        "hybrid_search",
        fail_if_called,
    )

    result = continue_bounded_agentic_retrieval(
        query="Explain staffing escalation pressure",
        initial_results=initial_results,
        chunks=[],
        embedded_chunks=[],
        model=DummyModel(),
        embedding_model="dummy",
    )

    assert result["audit"][
        "additional_retrieval_call_count"
    ] == 0

    assert result["audit"][
        "stop_reason"
    ] == "NO_RECOVERABLE_GAP"


def test_missing_topics_trigger_one_additional_retrieval(
    monkeypatch,
):
    initial_results = [
        _active_result(
            chunk_id="DOC-003::P1",
            document_id="DOC-003",
            text=(
                "Staffing escalation procedure."
            ),
        )
    ]

    refined_result = _active_result(
        chunk_id="DOC-011::P2",
        document_id="DOC-011",
        text=(
            "Severe weather contingency procedure "
            "supports staffing resilience."
        ),
    )

    def fake_assessment(
        query,
        results,
    ):
        chunk_ids = {
            result["chunk_id"]
            for result in results
        }

        if "DOC-011::P2" in chunk_ids:
            return {
                "sufficient": True,
                "decision": "SUFFICIENT",
                "matched_query_terms": [
                    "staffing",
                    "weather",
                ],
                "evidence_terms": [
                    "staffing",
                    "weather",
                ],
                "result_count": len(results),
                "topic_sufficient": True,
                "claim_sufficient": True,
                "claim_requirements": [],
                "unsupported_claims": [],
            }

        return {
            "sufficient": False,
            "decision": "INSUFFICIENT",
            "matched_query_terms": [
                "staffing"
            ],
            "evidence_terms": [
                "staffing"
            ],
            "result_count": len(results),
            "topic_sufficient": False,
            "claim_sufficient": True,
            "claim_requirements": [],
            "unsupported_claims": [],
        }

    monkeypatch.setattr(
        "src.retrieval.bounded_agentic_retrieval."
        "assess_evidence_sufficiency",
        fake_assessment,
    )

    def fake_diagnostics(
        query,
        results,
    ):
        chunk_ids = {
            result["chunk_id"]
            for result in results
        }

        recovered = (
            "DOC-011::P2"
            in chunk_ids
        )

        return {
            "query_topics": [
                "staffing",
                "weather",
            ],
            "matched_topics": (
                [
                    "staffing",
                    "weather",
                ]
                if recovered
                else [
                    "staffing"
                ]
            ),
            "missing_topics": (
                []
                if recovered
                else [
                    "weather"
                ]
            ),
            "evidence_terms": (
                [
                    "staffing",
                    "weather",
                ]
                if recovered
                else [
                    "staffing"
                ]
            ),
        }

    monkeypatch.setattr(
        "src.retrieval.bounded_agentic_retrieval."
        "get_evidence_topic_diagnostics",
        fake_diagnostics,
    )

    hybrid_calls = []

    def fake_hybrid_search(
        **kwargs,
    ):
        hybrid_calls.append(
            kwargs["query"]
        )

        return [
            refined_result
        ]

    monkeypatch.setattr(
        "src.retrieval.bounded_agentic_retrieval."
        "hybrid_search",
        fake_hybrid_search,
    )

    result = continue_bounded_agentic_retrieval(
        query=(
            "What should happen during severe "
            "weather staffing pressure?"
        ),
        initial_results=initial_results,
        chunks=[],
        embedded_chunks=[],
        model=DummyModel(),
        embedding_model="dummy",
        query_refiner=(
            lambda query, diagnostics:
            "severe weather staffing contingency"
        ),
    )

    assert len(
        hybrid_calls
    ) == 1

    assert hybrid_calls == [
        "severe weather staffing contingency"
    ]

    assert result["audit"][
        "initial_retrieval_reused"
    ] is True

    assert result["audit"][
        "additional_retrieval_call_count"
    ] == 1

    assert result["audit"][
        "stop_reason"
    ] == "EVIDENCE_SUFFICIENT_AFTER_REFINEMENT"

    assert {
        item["chunk_id"]
        for item in result["results"]
    } == {
        "DOC-003::P1",
        "DOC-011::P2",
    }


def test_invalid_refined_query_does_not_retrieve(
    monkeypatch,
):
    initial_results = [
        _active_result()
    ]

    monkeypatch.setattr(
        "src.retrieval.bounded_agentic_retrieval."
        "assess_evidence_sufficiency",
        lambda query, results: {
            "sufficient": False,
            "decision": "INSUFFICIENT",
            "matched_query_terms": [
                "staffing"
            ],
            "evidence_terms": [
                "staffing"
            ],
            "result_count": len(results),
            "topic_sufficient": False,
            "claim_sufficient": True,
            "claim_requirements": [],
            "unsupported_claims": [],
        },
    )

    monkeypatch.setattr(
        "src.retrieval.bounded_agentic_retrieval."
        "get_evidence_topic_diagnostics",
        lambda query, results: {
            "query_topics": [
                "staffing",
                "weather",
            ],
            "matched_topics": [
                "staffing"
            ],
            "missing_topics": [
                "weather"
            ],
            "evidence_terms": [
                "staffing"
            ],
        },
    )

    def fail_if_called(**kwargs):
        raise AssertionError(
            "Hybrid retrieval should not run"
        )

    monkeypatch.setattr(
        "src.retrieval.bounded_agentic_retrieval."
        "hybrid_search",
        fail_if_called,
    )

    result = continue_bounded_agentic_retrieval(
        query=(
            "Explain weather staffing escalation"
        ),
        initial_results=initial_results,
        chunks=[],
        embedded_chunks=[],
        model=DummyModel(),
        embedding_model="dummy",
        query_refiner=(
            lambda query, diagnostics:
            None
        ),
    )

    assert result["audit"][
        "additional_retrieval_call_count"
    ] == 0

    assert result["audit"][
        "stop_reason"
    ] == "REFINED_QUERY_INVALID"


def test_same_query_refinement_is_rejected(
    monkeypatch,
):
    initial_results = [
        _active_result()
    ]

    monkeypatch.setattr(
        "src.retrieval.bounded_agentic_retrieval."
        "assess_evidence_sufficiency",
        lambda query, results: {
            "sufficient": False,
            "decision": "INSUFFICIENT",
            "matched_query_terms": [
                "staffing"
            ],
            "evidence_terms": [
                "staffing"
            ],
            "result_count": len(results),
            "topic_sufficient": False,
            "claim_sufficient": True,
            "claim_requirements": [],
            "unsupported_claims": [],
        },
    )

    monkeypatch.setattr(
        "src.retrieval.bounded_agentic_retrieval."
        "get_evidence_topic_diagnostics",
        lambda query, results: {
            "query_topics": [
                "staffing",
                "weather",
            ],
            "matched_topics": [
                "staffing"
            ],
            "missing_topics": [
                "weather"
            ],
            "evidence_terms": [
                "staffing"
            ],
        },
    )

    def fail_if_called(**kwargs):
        raise AssertionError(
            "Hybrid retrieval should not run"
        )

    monkeypatch.setattr(
        "src.retrieval.bounded_agentic_retrieval."
        "hybrid_search",
        fail_if_called,
    )

    result = continue_bounded_agentic_retrieval(
        query="Explain weather staffing escalation",
        initial_results=initial_results,
        chunks=[],
        embedded_chunks=[],
        model=DummyModel(),
        embedding_model="dummy",
        query_refiner=(
            lambda query, diagnostics:
            "  Explain   weather staffing escalation  "
        ),
    )

    assert result["audit"][
        "additional_retrieval_call_count"
    ] == 0

    assert result["audit"][
        "stop_reason"
    ] == "REFINED_QUERY_INVALID"


def test_out_of_scope_query_stops_before_continuation(
    monkeypatch,
):
    initial_results = [
        _active_result()
    ]

    def fail_if_called(*args, **kwargs):
        raise AssertionError(
            "Evidence or retrieval logic should not run "
            "for an out-of-scope query"
        )

    monkeypatch.setattr(
        "src.retrieval.bounded_agentic_retrieval."
        "assess_evidence_sufficiency",
        fail_if_called,
    )

    monkeypatch.setattr(
        "src.retrieval.bounded_agentic_retrieval."
        "hybrid_search",
        fail_if_called,
    )

    result = continue_bounded_agentic_retrieval(
        query="What is the current NHS England performance?",
        initial_results=initial_results,
        chunks=[],
        embedded_chunks=[],
        model=DummyModel(),
        embedding_model="dummy",
    )

    assert result["results"] == []

    assert result["audit"][
        "additional_retrieval_call_count"
    ] == 0

    assert result["audit"][
        "stop_reason"
    ] == "ORIGINAL_QUERY_OUT_OF_SCOPE"


def test_audit_explicitly_marks_initial_retrieval_reused(
    monkeypatch,
):
    initial_results = [
        _active_result()
    ]

    monkeypatch.setattr(
        "src.retrieval.bounded_agentic_retrieval."
        "assess_evidence_sufficiency",
        lambda query, results: {
            "sufficient": True,
            "decision": "SUFFICIENT",
            "matched_query_terms": [
                "staffing"
            ],
            "evidence_terms": [
                "staffing"
            ],
            "result_count": len(results),
            "topic_sufficient": True,
            "claim_sufficient": True,
            "claim_requirements": [],
            "unsupported_claims": [],
        },
    )

    monkeypatch.setattr(
        "src.retrieval.bounded_agentic_retrieval."
        "get_evidence_topic_diagnostics",
        lambda query, results: {
            "query_topics": [
                "staffing"
            ],
            "matched_topics": [
                "staffing"
            ],
            "missing_topics": [],
            "evidence_terms": [
                "staffing"
            ],
        },
    )

    result = continue_bounded_agentic_retrieval(
        query="Explain staffing escalation",
        initial_results=initial_results,
        chunks=[],
        embedded_chunks=[],
        model=DummyModel(),
        embedding_model="dummy",
    )

    assert (
        result["audit"][
            "initial_retrieval_reused"
        ]
        is True
    )