from copy import deepcopy
import importlib
from unittest.mock import Mock

import pytest

from src.retrieval.reranker import rerank_relevance


def test_scores_preserve_fields_and_inputs():
    candidates = [
        {"text": "semantic", "chunk_id": "A", "document_id": "DOC-A",
         "status": "Active", "similarity_score": 0.9, "keyword_score": 2,
         "semantic_rank": 1, "keyword_rank": 2, "rrf_score": 0.03,
         "hybrid_rank": 1, "candidate_rank": 1, "rerank_rank": 1,
         "page": 2, "source_file": "a.pdf", "metadata": {"owner": "team"}},
        {"text": "keyword only", "chunk_id": "B", "keyword_score": 3},
        {"text": "semantic only", "chunk_id": "C", "similarity_score": 0.8},
    ]
    before = deepcopy(candidates)
    scorer = Mock(return_value=[0.1, 0.9, 0.5])
    results = rerank_relevance("question", candidates, scorer=scorer)
    scorer.assert_called_once_with([("question", c["text"]) for c in candidates])
    assert results == [
        {**before[i], "relevance_score": score, "relevance_rank": rank}
        for rank, (i, score) in enumerate([(1, 0.9), (2, 0.5), (0, 0.1)], 1)
    ]
    assert candidates == before
    assert results is not candidates
    assert all(result is not candidates[i] for result in results for i in range(3))


def test_ties_preserve_input_order():
    candidates = [{"text": "a", "chunk_id": "A"}, {"text": "z", "chunk_id": "Z"}]
    scorer = lambda pairs: [1, 1]
    first = rerank_relevance("q", candidates, scorer=scorer)
    assert [r["chunk_id"] for r in first] == ["A", "Z"]
    assert rerank_relevance("q", candidates, scorer=scorer) == first


def test_empty_does_not_call_scorer():
    scorer = Mock()
    assert rerank_relevance("q", [], scorer=scorer) == []
    scorer.assert_not_called()


@pytest.mark.parametrize("scores", [[], [1, 2]])
def test_wrong_score_count(scores):
    with pytest.raises(ValueError, match="one score"):
        rerank_relevance("q", [{"text": "a"}], scorer=lambda pairs: scores)


@pytest.mark.parametrize("score", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_score(score):
    with pytest.raises(ValueError, match="finite"):
        rerank_relevance("q", [{"text": "a"}], scorer=lambda pairs: [score])


@pytest.mark.parametrize("score", ["1", None, True, 1j])
def test_non_numeric_score(score):
    with pytest.raises(TypeError, match="real numbers"):
        rerank_relevance("q", [{"text": "a"}], scorer=lambda pairs: [score])


@pytest.mark.parametrize("candidate", [{}, {"text": None}, {"text": 1}, {"text": " "}])
def test_invalid_text(candidate):
    scorer = Mock()
    with pytest.raises(ValueError, match="text"):
        rerank_relevance("q", [candidate], scorer=scorer)
    scorer.assert_not_called()


@pytest.mark.parametrize("query", [None, 1, "", " \t"])
def test_invalid_query(query):
    with pytest.raises(ValueError, match="query"):
        rerank_relevance(query, [], scorer=Mock())


@pytest.mark.parametrize("candidates", [None, {}, [None], ["text"]])
def test_invalid_candidates(candidates):
    with pytest.raises(TypeError):
        rerank_relevance("q", candidates, scorer=Mock())


def test_invalid_scorer_and_failure_propagation():
    with pytest.raises(TypeError, match="callable"):
        rerank_relevance("q", [], scorer=None)
    with pytest.raises(RuntimeError, match="scoring failed"):
        rerank_relevance("q", [{"text": "a"}], scorer=Mock(side_effect=RuntimeError("scoring failed")))


def test_reranker_does_not_make_lifecycle_decisions():
    results = rerank_relevance("q", [{"text": "draft", "status": "Draft"}], scorer=lambda pairs: [1])
    assert results[0]["status"] == "Draft"


def record(name, status="Active"):
    return dict(chunk_id=name, document_id=name, title=name,
                document_type="Policy", source_type="Synthetic", version="1.0",
                effective_date="2026-01-01", status=status, source_file="test.pdf",
                page=1, chunk_number=1, text=name)


def test_hybrid_lifecycle_before_and_after_scorer(monkeypatch):
    module = importlib.import_module("src.retrieval.hybrid_search")
    pool = [record("active"), record("draft", "Draft"),
            record("old", "Superseded"), record("archived", "Archived")]
    monkeypatch.setattr(module, "semantic_search", lambda **kwargs: pool)
    monkeypatch.setattr(module, "keyword_search", lambda **kwargs: [])
    original_filter = module.filter_hybrid_eligible_results
    events = []

    def tracked_filter(results):
        events.append("filter")
        return original_filter(results)

    def scorer(pairs):
        events.append("score")
        assert pairs == [("q", "active")]
        return [1]

    monkeypatch.setattr(module, "filter_hybrid_eligible_results", tracked_filter)
    results = module.hybrid_search("q", [], [], None, "test", relevance_scorer=scorer)
    assert events == ["filter", "score", "filter"]
    assert [r["chunk_id"] for r in results] == ["active"]
    assert results[0]["rank"] == 1


def test_hybrid_threshold_and_top_k_remain_after_reranking(monkeypatch):
    module = importlib.import_module("src.retrieval.hybrid_search")
    a, b, c = record("A"), record("B"), record("C")
    monkeypatch.setattr(module, "semantic_search", lambda **kwargs: [a, b])
    monkeypatch.setattr(module, "keyword_search", lambda **kwargs: [a, b, c])
    scorer = Mock(side_effect=lambda pairs: [{"A": 1, "B": 2, "C": 3}[text] for _, text in pairs])
    results = module.hybrid_search("q", [], [], None, "test", final_k=1,
                                   min_rrf_score=0.02, relevance_scorer=scorer)
    assert len(scorer.call_args.args[0]) == 3
    # C ranks highest by relevance but fails the RRF threshold. B must survive.
    assert [r["chunk_id"] for r in results] == ["B"]
    assert results[0]["relevance_rank"] == 2
    assert results[0]["rank"] == 1
    assert results[0]["rrf_score"] == 2 / 62
