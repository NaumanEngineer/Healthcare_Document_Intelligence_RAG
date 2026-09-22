from __future__ import annotations

import json
from pathlib import Path

from src.preprocessing.build_chunks import (
    build_document_chunks,
)

from src.retrieval.embeddings import (
    embed_chunks,
    get_model_identifier,
    load_embedding_model,
)

from src.retrieval.semantic_search import (
    semantic_search,
)

from src.retrieval.keyword_search import (
    keyword_search,
)

from src.retrieval.hybrid_search import (
    hybrid_search,
)

from src.retrieval.hybrid_search_rrf_only import (
    hybrid_search_rrf_only,
)

from src.retrieval.query_scope import (
    assess_query_scope,
)

from src.evaluation.retrieval_benchmark import (
    compare_methods_for_case,
    evaluate_retrieval_results,
    summarise_benchmark,
    summarise_method,
)