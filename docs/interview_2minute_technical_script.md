# Two-Minute Technical Explanation

I built a governed healthcare document-intelligence RAG prototype with deliberately separated processing, retrieval, generation and evaluation layers.

Documents are ingested, cleaned and chunked while preserving provenance including document ID, version, page and lifecycle status.

Validated chunks are embedded locally and include model identity, dimensions and deterministic text hashes.

The retrieval layer applies hard lifecycle eligibility, embedding compatibility checks, stale-vector detection, semantic similarity, candidate ranking, deterministic reranking and a configurable evidence threshold.

Only final eligible evidence is passed into the generation layer.

The generation layer formats evidence into controlled blocks and constructs an evidence-only prompt.

If no sufficient evidence exists, the language model is not called and the system returns a controlled abstention.

Generated answers are then checked against an allow-list of retrieved document and chunk identifiers.

I also implemented a benchmark framework covering retrieval quality, cross-document queries, abstention, lifecycle conflicts, prompt injection and lightweight claim-level faithfulness.

The architecture is provider-independent so the local prototype can later evolve toward Azure AI Search, Azure OpenAI and Microsoft Fabric without rewriting the core governance logic.
