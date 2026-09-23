from copy import deepcopy
import importlib
from unittest.mock import Mock

import pytest

module = importlib.import_module("src.retrieval.hybrid_search_evidence_rescue")


def evidence(doc, title, suffix="1"):
    return {"document_id": doc, "chunk_id": doc + "-" + suffix,
            "title": title, "status": "Active"}


def run(monkeypatch, question, initial, pool, final_k=3):
    normal = Mock(return_value=initial)
    rescue = Mock(return_value=pool)
    monkeypatch.setattr(module, "hybrid_search", normal)
    monkeypatch.setattr(module, "hybrid_search_rrf_only", rescue)
    output = module.hybrid_search_evidence_rescue(
        question, [], [], None, "test", final_k=final_k,
    )
    normal.assert_called_once()
    return output, rescue


@pytest.mark.parametrize("question,title", [
    ("Escalation when bed capacity is under pressure", "Bed capacity escalation"),
    ("Summarise operational escalation", "Operational escalation"),
    ("Operational leadership guidance", "Operational leadership"),
    ("Workforce and site flow", "Workforce and site flow"),
    ("Emergency transport delays with crews", "Ambulance handover"),
], ids=["Q003-style", "Q010-style", "Q011-style", "Q026-style", "Q038-style"])
def test_sufficient_results_unchanged(monkeypatch, question, title):
    initial = [evidence("DOC-001", title), evidence("DOC-002", title)]
    output, rescue = run(monkeypatch, question, initial, [])
    assert output["results"] is initial
    assert not output["audit"]["rescue_attempted"]
    rescue.assert_not_called()


def test_q027_rescue_preserves_strongest_original_and_audit(monkeypatch):
    initial = [evidence("DOC-008", "Ambulance handover", str(i)) for i in range(3)]
    pool = [evidence("DOC-005", "Business continuity"),
            evidence("DOC-009", "Severe weather")]
    before = deepcopy((initial, pool))
    question = "How should severe weather pressure and ambulance handover disruption be considered together?"
    output, rescue = run(monkeypatch, question, initial, pool)
    assert output["results"] == initial[:2] + [pool[1]]
    assert output["audit"]["initial_evidence"]["decision"] == "INSUFFICIENT"
    assert output["audit"]["final_evidence"]["decision"] == "SUFFICIENT"
    assert output["audit"]["rescued_chunk_ids"] == ["DOC-009-1"]
    assert output["audit"]["rescued_document_ids"] == ["DOC-009"]
    assert rescue.call_args.kwargs["final_k"] == 20
    assert (initial, pool) == before
    assert run(monkeypatch, question, initial, pool)[0] == output


@pytest.mark.parametrize("question", [
    "Cyber-security incident procedure", "Electronic patient record failure",
    "Medical oxygen supply failure",
], ids=["Q029", "Q030", "Q031"])
def test_unsupported_subjects_remain_insufficient(monkeypatch, question):
    initial = [evidence("DOC-001", "Operational escalation")]
    output, rescue = run(monkeypatch, question, initial, [evidence("DOC-005", "Business continuity")])
    assert output["results"] == initial
    assert output["audit"]["rescue_attempted"]
    assert not output["audit"]["final_evidence"]["sufficient"]
    assert output["audit"]["rescued_chunk_ids"] == []
    rescue.assert_called_once()


@pytest.mark.parametrize("final_k", [1, 2])
def test_capacity_never_drops_an_existing_topic(monkeypatch, final_k):
    initial = [evidence("DOC-008", "Ambulance handover")]
    weather = evidence("DOC-009", "Severe weather")
    output, _ = run(monkeypatch, "Severe weather and ambulance handover", initial, [initial[0], weather], final_k)
    assert len(output["results"]) <= final_k
    assert output["results"][0] == initial[0]
    assert output["audit"]["final_evidence"]["sufficient"] is (final_k == 2)
