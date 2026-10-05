"""Local cross-encoder adapter; no retrieval or governance decisions."""
import math
from numbers import Real
from time import perf_counter

DEFAULT_RERANKER = "cross-encoder/ms-marco-MiniLM-L6-v2"


class CrossEncoderScorer:
    def __init__(self, model=None, *, model_name=DEFAULT_RERANKER):
        if model is None:
            from sentence_transformers import CrossEncoder
            model = CrossEncoder(model_name, device="cpu")
        self.model = model
        self.model_name = model_name
        self.calls = 0
        self.candidates = 0
        self.seconds = 0.0

    def __call__(self, pairs):
        if not pairs:
            return []
        start = perf_counter()
        values = self.model.predict(pairs, batch_size=16, show_progress_bar=False)
        values = values.tolist() if hasattr(values, "tolist") else list(values)
        if len(values) != len(pairs):
            raise ValueError("expected one cross-encoder score per pair")
        scores = []
        for value in values:
            if isinstance(value, bool) or not isinstance(value, Real):
                raise TypeError("cross-encoder scores must be scalar real numbers")
            if not math.isfinite(value):
                raise ValueError("cross-encoder scores must be finite")
            scores.append(float(value))
        self.calls += 1
        self.candidates += len(pairs)
        self.seconds += perf_counter() - start
        return scores
