# Interview Evidence

## Week 17 Day 1 — Healthcare RAG Foundation

### 90-Second Explanation

I am building a governed healthcare document intelligence system using Retrieval-Augmented Generation.

The use case is an Operational Policy and Escalation Intelligence Assistant that retrieves relevant evidence from approved healthcare operational documents before generating an answer.

I deliberately separated retrieval from generation because a fluent answer is not evidence that the correct source was found.

The architecture includes document ingestion, cleaning, structure-aware chunking, metadata, embeddings, retrieval, reranking, grounded generation, citations and human review.

I also designed the corpus and governance model before implementation. Documents retain provenance, version and status metadata, and the prototype uses only synthetic or publicly available non-sensitive content.

I created an initial threat model covering prompt injection, corpus poisoning, superseded policies, retrieval failure, unsupported generation, citation mismatch and excessive agency.

The system is designed to abstain when sufficient evidence is unavailable rather than fabricate policy content.
