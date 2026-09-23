import json
from unittest.mock import Mock

import pytest

from src.evaluation import run_week18_benchmark as runner


METHODS = {
    "semantic": "semantic_search",
    "keyword": "keyword_search",
    "hybrid": "hybrid_search",
    "rrf_only": "hybrid_search_rrf_only",
}


@pytest.fixture
def run_case(monkeypatch, tmp_path):
    # No real corpus, models, retrieval calls or benchmark outputs are used.
    monkeypatch.setattr(runner, "build_benchmark_corpus", lambda: [])
    monkeypatch.setattr(runner, "get_raw_corpus_files", lambda: [])
    monkeypatch.setattr(runner, "load_embedding_model", lambda: object())
    monkeypatch.setattr(runner, "get_model_identifier", lambda model: "test-model")
    monkeypatch.setattr(runner, "embed_chunks", lambda **kwargs: [])
    monkeypatch.setattr(runner, "OUTPUT_FILE", tmp_path / "benchmark.json")

    def run(question, method_results, expected_abstention=False, rescue_output=None):
        monkeypatch.setattr(runner, "load_evaluation_cases", lambda: [{
            "query_id": "TEST", "question": question,
            "expected_document_id": "DOC-001",
            "expected_abstention": expected_abstention,
        }])
        mocks = {}
        for method, function in METHODS.items():
            mocks[method] = Mock(return_value=method_results[method])
            monkeypatch.setattr(runner, function, mocks[method])
        mocks["hybrid_rescue"] = Mock(return_value=rescue_output or {
            "results": [], "audit": {"final_evidence": {"decision": "SUFFICIENT"}},
        })
        monkeypatch.setattr(runner, "hybrid_search_evidence_rescue", mocks["hybrid_rescue"])
        output = runner.run_benchmark()
        saved = json.loads(runner.OUTPUT_FILE.read_text(encoding="utf-8"))
        assert saved == output
        assert "hybrid_rescue" in saved["summary"]
        assert saved["summary"]["hybrid_rescue"]["evaluated_cases"] == 1
        return saved["case_results"][0], mocks

    return run


@pytest.mark.parametrize("blocked_method", METHODS)
def test_evidence_gates_each_method_independently(run_case, blocked_method, capsys):
    raw = {
        method: [{"document_id": "DOC-001", "status": "Active",
                  "title": "Workforce guidance"}]
        for method in METHODS
    }
    raw[blocked_method] = [{"document_id": "DOC-002", "status": "Active",
                            "title": "Bed capacity guidance"}]
    case, mocks = run_case("What guidance covers workforce?", raw, True)
    assert case["scope_assessment"]["allowed"] is True
    assert {m: case["raw_results"][m] for m in METHODS} == raw
    for method in METHODS:
        mocks[method].assert_called_once()
        assessment = case["evidence_sufficiency"][method]
        assert assessment["result_count"] == 1
        assert assessment["sufficient"] is (method != blocked_method)
        assert case[method]["result_count"] == (0 if method == blocked_method else 1)
        assert case[method]["abstention_success"] is (method == blocked_method)
    assert capsys.readouterr().out.count("evidence: INSUFFICIENT -> ABSTAIN") == 1


def test_scope_abstention_skips_retrieval_and_evidence(run_case, monkeypatch, capsys):
    assessor = Mock(side_effect=AssertionError("Evidence check must be skipped"))
    monkeypatch.setattr(runner, "assess_evidence_sufficiency", assessor)
    case, mocks = run_case(
        "What medication should be prescribed?", {method: [] for method in METHODS}, True,
    )
    assert case["scope_assessment"]["allowed"] is False
    assessor.assert_not_called()
    mocks["hybrid_rescue"].assert_not_called()
    assert case["hybrid_rescue_audit"] is None
    assert case["raw_results"]["hybrid_rescue"] == []
    assert case["hybrid_rescue"]["abstention_success"] is True
    for method in METHODS:
        mocks[method].assert_not_called()
        assert case["raw_results"][method] == []
        assert case["evidence_sufficiency"][method] is None
        assert case[method]["abstention_success"] is True
    assert "evidence: INSUFFICIENT" not in capsys.readouterr().out


@pytest.mark.parametrize("question, title, sufficient", [
    ("What is the approved operational procedure for managing hospital "
     "cyber-security incidents?", "Business Continuity Procedure", False),
    ("What approved operational guidance covers a complete failure of the "
     "hospital's electronic patient record system?", "Operational Escalation Policy", False),
    ("Which approved policy defines the operational response to a major "
     "medical oxygen supply failure?", "Operational Escalation Policy", False),
    ("How should severe weather pressure and ambulance handover disruption "
     "be considered together?", "Ambulance Handover Guidance", False),
    ("Which procedure coordinates operational site flow during periods of "
     "system pressure?", "Site Flow Coordination Procedure", True),
    ("Which procedure describes escalation within the emergency department "
     "during operational pressure?", "Emergency Department Escalation Procedure", True),
], ids=["Q029", "Q030", "Q031", "Q027", "Q018", "Q019"])
def test_real_gates_control_scoring_with_fixture_retrieval(run_case, question, title, sufficient):
    raw = {method: [{"title": title, "document_id": "DOC-001", "status": "Active"}]
           for method in METHODS}
    case, _ = run_case(question, raw, not sufficient)
    assert case["scope_assessment"]["allowed"] is True
    for method in METHODS:
        assert case["evidence_sufficiency"][method]["sufficient"] is sufficient
        assert case[method]["result_count"] == int(sufficient)
        assert case["raw_results"][method] == raw[method]


@pytest.mark.parametrize("decision", ["SUFFICIENT", "INSUFFICIENT"])
def test_rescue_uses_own_final_decision_and_preserves_audit(run_case, monkeypatch, decision):
    # Deliberately use results that the ordinary gate would reject. The benchmark
    # must trust the rescue module's final decision, not run that gate twice.
    returned = [{"document_id": "DOC-009", "status": "Active", "title": "Weather"}]
    audit = {"final_evidence": {"decision": decision}, "rescue_attempted": True,
             "rescued_chunk_ids": ["DOC-009-C001"]}
    checker = Mock(wraps=runner.assess_evidence_sufficiency)
    monkeypatch.setattr(runner, "assess_evidence_sufficiency", checker)
    case, mocks = run_case(
        "Workforce guidance", {m: [] for m in METHODS}, True,
        rescue_output={"results": returned, "audit": audit},
    )
    assert checker.call_count == 4
    mocks["hybrid_rescue"].assert_called_once()
    kwargs = mocks["hybrid_rescue"].call_args.kwargs
    assert kwargs["final_k"] == runner.FINAL_K
    assert kwargs["semantic_k"] == runner.SEMANTIC_K
    assert kwargs["keyword_k"] == runner.KEYWORD_K
    assert kwargs["semantic_min_similarity"] == runner.SEMANTIC_MIN_SIMILARITY
    assert kwargs["keyword_min_score"] == runner.KEYWORD_MIN_SCORE
    assert kwargs["min_rrf_score"] == runner.MIN_RRF_SCORE
    assert case["raw_results"]["hybrid_rescue"] == returned
    assert case["hybrid_rescue_audit"] == audit
    assert case["evidence_sufficiency"]["hybrid_rescue"] == audit["final_evidence"]
    assert case["hybrid_rescue"]["result_count"] == int(decision == "SUFFICIENT")
    assert case["hybrid_rescue"]["abstention_success"] is (decision == "INSUFFICIENT")
    assert case["hybrid"]["result_count"] == 0
