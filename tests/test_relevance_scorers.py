from unittest.mock import Mock
import numpy as np
import pytest
from src.retrieval.relevance_scorers import CrossEncoderScorer


def test_conversion_reuse_and_empty():
    model = Mock()
    model.predict.return_value = np.array([0.5, -2.0])
    scorer = CrossEncoderScorer(model)
    assert scorer([]) == []
    model.predict.assert_not_called()
    for _ in range(2):
        assert scorer([("q", "a"), ("q", "b")]) == [0.5, -2.0]
    assert scorer.model is model
    assert model.predict.call_count == scorer.calls == 2
    assert scorer.candidates == 4


@pytest.mark.parametrize("values,error", [([], ValueError), ([1,2], ValueError),
    ([float("nan")], ValueError), ([float("inf")], ValueError),
    ([float("-inf")], ValueError), (["1"], TypeError), ([True], TypeError), ([[1]], TypeError)])
def test_bad_scores(values, error):
    model = Mock()
    model.predict.return_value = values
    with pytest.raises(error):
        CrossEncoderScorer(model)([("q", "a")])
