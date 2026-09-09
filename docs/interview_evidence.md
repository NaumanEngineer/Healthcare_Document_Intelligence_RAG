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

## Week 17 Day 2 — Document Ingestion and Provenance

### Interview Example

I built the ingestion layer for a healthcare document-intelligence RAG system.

Rather than simply extracting PDF text, I designed the pipeline around provenance, document lifecycle and data-quality controls.

The loader validates source files, extracts text at page level and preserves the source filename and page number so downstream answers can remain traceable to evidence.

I then introduced a separate metadata layer containing document ID, document type, version, effective date and lifecycle status such as Active or Superseded.

This was important because a semantically relevant document may still be unsafe to retrieve if it has been superseded.

I also created an ingestion QA layer that classifies ingestion runs as passed, review or failed based on extraction quality.

The design reused governance patterns from my earlier NHS Operational Data Platform, including lineage, quality status and batch traceability.

The architecture is currently local and deliberately simple, but the Python components are designed so the storage and orchestration layer can later migrate to Microsoft Fabric or Azure without rewriting the core ingestion logic.


## Week 17 Day 3 — Chunking and Retrieval Metadata

I designed the chunking layer for a governed healthcare RAG system.

Rather than using blind fixed-length splitting, I used a paragraph-first approach with word-boundary-aware fallback splitting and controlled overlap.

Each chunk preserves document provenance and receives a version-aware identifier containing document ID, version, page and chunk ordinal.

I also introduced a canonical metadata contract covering document lifecycle, source, version, effective date and page provenance.

Chunks are validated before they are considered retrieval-ready, and a separate QA layer checks for empty chunks, duplicates, invalid provenance and abnormal chunk sizes.

This reused data modelling and quality principles from my earlier NHS Operational Data Platform and prepared the architecture for later Microsoft Fabric and Azure deployment.
