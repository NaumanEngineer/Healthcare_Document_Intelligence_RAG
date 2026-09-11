# Technical Interview Demo

I built a governed healthcare document-intelligence RAG prototype.

The system begins with document ingestion, cleaning, metadata enrichment and chunking.

Every chunk preserves provenance including document ID, version, page and lifecycle status.

I then generate local semantic embeddings and maintain analytical metadata using Parquet and DuckDB.

Retrieval applies hard lifecycle filtering before semantic ranking, validates embedding compatibility, detects stale embeddings using text hashes, and supports configurable evidence thresholds.

The generation layer is deliberately separated from retrieval.

Only approved evidence enters the prompt, and the LLM is skipped entirely when evidence is insufficient.

After generation, a separate QA layer validates document and chunk citations against the approved evidence set.

I also implemented retrieval benchmarks, abstention cases, lifecycle-conflict tests, prompt-injection scenarios and a lightweight claim-support evaluator.

The architecture is provider-independent so the local components can later evolve toward Microsoft Fabric, Azure AI Search and Azure OpenAI without rewriting the core governance contracts.
