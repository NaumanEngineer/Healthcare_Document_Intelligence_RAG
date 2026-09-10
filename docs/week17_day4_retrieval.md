# Week 17 Day 4 — Embeddings, DuckDB and Governed Retrieval

## Objective

Build the retrieval layer for the Healthcare Document Intelligence RAG project.

The Day 4 work transforms validated healthcare document chunks into semantically searchable evidence while preserving provenance, lifecycle metadata and retrieval-quality controls.

---

## What Was Built

### 1. Embedding Layer

Implemented:

`src/retrieval/embeddings.py`

The embedding layer:

- validates chunks before embedding
- generates local semantic vectors
- preserves all chunk metadata
- records embedding model identity
- records embedding dimensions
- creates deterministic text hashes
- rejects invalid, non-finite or zero vectors
- surfaces batch failures with the failing chunk ID

The current prototype uses:

`sentence-transformers/all-MiniLM-L6-v2`

This is a local prototype model and is not treated as the final production healthcare embedding model.

---

## 2. Embedding Contract

Each embedded chunk preserves its original retrieval metadata and adds:

- vector
- embedding_model
- embedding_dimensions
- text_hash

The text hash supports stale-embedding detection if chunk text changes.

Query and chunk vectors must use compatible embedding configurations and dimensions.

---

## 3. DuckDB + Parquet Knowledge Catalogue

Implemented:

`src/storage/duckdb_catalogue.py`

Validated chunk metadata can be persisted to Parquet and queried using DuckDB.

DuckDB is used as a local analytical catalogue for:

- chunk metadata
- document lifecycle analysis
- chunk counts
- ingestion lineage
- QA inspection
- retrieval evaluation preparation

The vector itself is intentionally excluded from the first analytical catalogue.

DuckDB is not used as the embedding model and is not currently the primary vector-search engine.

---

## 4. Local Lakehouse Learning Pattern

The current local architecture is:

Validated Chunks
→ Parquet
→ DuckDB
→ SQL Inspection / QA

This introduces local lakehouse-style concepts before later Microsoft Fabric implementation.

Future progression:

Python + Parquet + DuckDB
→ Fabric OneLake + Lakehouse
→ enterprise orchestration and analytics

---

## 5. Semantic Retrieval

Implemented:

`src/retrieval/semantic_search.py`

The semantic retrieval flow is:

User Query
→ Query Validation
→ Active-Only Eligible Chunk Set
→ Query Embedding
→ Embedding Compatibility Validation
→ Cosine Similarity
→ Candidate Ranking
→ Final Evidence Selection

The retrieval layer preserves:

- chunk ID
- document ID
- document title
- version
- lifecycle status
- source file
- page
- chunk number
- text
- embedding metadata
- similarity score

---

## 6. Lifecycle-Aware Filtering

Semantic similarity alone is not sufficient for evidence selection.

Prototype lifecycle policy:

- Active → eligible
- Superseded → excluded
- Draft → excluded
- Archived → excluded

Hard eligibility filtering occurs before final candidate selection.

This prevents obsolete guidance from being selected simply because it has a stronger similarity score.

---

## 7. Candidate vs Final Retrieval

The system distinguishes:

- `candidate_k`
- `final_k`

`candidate_k` controls the number of initial semantic candidates.

`final_k` controls the number of final evidence records returned.

This prepares the architecture for later reranking.

---

## 8. Deterministic Reranking Baseline

Implemented:

`src/retrieval/reranker.py`

The current reranker is intentionally simple.

It prioritises:

1. lifecycle eligibility
2. semantic similarity
3. deterministic chunk-ID tie-breaking

This is treated as a baseline rather than a sophisticated AI reranker.

Future evaluation may compare this baseline against a learned or cross-encoder reranking approach.

---

## 9. Retrieval Quality Evaluation

Implemented:

`src/evaluation/retrieval_qa.py`

Initial retrieval metrics include:

- Top-1 chunk success
- Top-3 chunk success
- Top-1 document success
- Top-3 document success
- Top-3 page success
- reciprocal rank
- Active-only retrieval compliance

Retrieval is evaluated independently from answer generation.

---

## 10. Retrieval Evaluation Cases

Defined in:

`docs/retrieval_evaluation_cases.md`

Evaluation cases include:

- direct escalation queries
- workforce queries
- capacity queries
- governance queries
- Superseded-vs-Active conflicts
- insufficient-evidence questions

This creates a controlled basis for later retrieval benchmarking.

---

## 11. Insufficient Evidence Behaviour

The retrieval layer does not assume that every query has useful evidence.

If there are no eligible chunks or no appropriate evidence, the retrieval layer can return an empty result.

Later, the generation layer will convert this into an explicit insufficient-evidence response rather than fabricating an answer.

---

## 12. QA Boundaries

Different validation and QA layers remain separate.

### Ingestion QA

Checks document extraction and page-level processing.

### Chunk Metadata Validation

Checks whether one chunk satisfies the canonical retrieval schema.

### Chunk QA

Checks chunk health, such as duplicate IDs, empty chunks and abnormal sizes.

### Embedding QA

Checks vector validity, model identity, dimensions and text-hash consistency.

### Retrieval QA

Checks whether the correct evidence is actually retrieved.

This separation improves debugging and system transparency.

---

## Governance Principles Applied

### Evidence Before Generation

The system first proves that relevant evidence can be retrieved before any LLM answer-generation layer is introduced.

### Lifecycle Awareness

Obsolete or inappropriate document states are excluded from normal retrieval.

### Provenance Preservation

Every retrieval result remains traceable to a source document, version and page.

### Embedding Compatibility

Vectors from incompatible configurations must not be compared.

### Insufficient Evidence

The system is allowed to return no evidence rather than force a weak semantic match.

### Retrieval Evaluation

Retrieval quality is measured independently from language-model performance.

---

## Cross-Pollination With Earlier Work

Day 4 combines several previously learned skills:

- Python engineering
- SQL thinking
- data quality
- metadata modelling
- PostgreSQL-style governance concepts
- Parquet
- DuckDB
- semantic embeddings
- retrieval evaluation

The project is evolving from a standalone RAG exercise into a broader healthcare intelligence platform.

---

## Future Microsoft Fabric Mapping

The current architecture can later evolve toward:

Healthcare Documents
→ Fabric / OneLake
→ Lakehouse
→ governed chunk layer
→ Azure AI embeddings
→ metadata-aware retrieval
→ retrieval evaluation
→ Power BI monitoring
→ grounded AI assistant

The current local implementation provides the conceptual and engineering foundation for that migration.

---

## Current Limitations

The current prototype does not yet include:

- production vector database
- hybrid keyword + semantic retrieval
- learned reranking
- retrieval-score thresholds
- grounded answer generation
- citation rendering
- LLM-based evidence synthesis
- production access control
- Microsoft Fabric implementation
- Azure deployment

These will be added incrementally after retrieval quality is proven.

---

## Reflection

The main lesson from Day 4 is that a RAG system should not begin with the language model.

Reliable RAG depends on governed evidence preparation, embedding compatibility, metadata-aware retrieval, lifecycle control and measurable retrieval quality.

The system therefore evaluates retrieval independently before introducing answer generation.
