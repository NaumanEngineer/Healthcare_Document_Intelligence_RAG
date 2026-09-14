# Week 18 Baseline

## Purpose

Freeze the Week 17 Healthcare Document Intelligence RAG prototype before introducing Week 18 retrieval upgrades.

This baseline will be used to compare later:

- semantic-only retrieval
- keyword / BM25 retrieval
- hybrid retrieval

The goal is to measure whether new retrieval techniques genuinely improve the system rather than assuming that additional complexity is beneficial.

---

## Baseline System

The current Week 17 system includes:

### Document Processing

- PDF ingestion
- text cleaning
- document metadata enrichment
- chunking
- chunk metadata validation
- chunk QA

### Embedding Layer

- local sentence-transformer embeddings
- vector validation
- embedding-dimension validation
- embedding model tracking
- text hashing
- stale-embedding detection

### Analytical Knowledge Layer

- Parquet outputs
- DuckDB catalogue
- metadata analysis
- lifecycle analysis

### Retrieval Layer

- semantic retrieval
- cosine similarity
- Active-only eligibility
- embedding compatibility checks
- stale-vector checks
- candidate ranking
- deterministic reranking
- configurable evidence threshold
- final evidence selection

### Generation Layer

- evidence formatting
- grounded prompt construction
- provider-independent LLM interface
- controlled abstention
- citation preservation

### Answer QA

- citation allow-list
- unsupported document ID detection
- unsupported chunk ID detection
- answer-result validation
- lightweight claim-support screening

### Evaluation

- structured benchmark dataset
- retrieval evaluation framework
- abstention testing
- cross-document evaluation
- lifecycle-conflict scenarios
- prompt-injection scenarios
- out-of-scope clinical cases
- failure analysis

---

## Baseline Retrieval Approach

The current retrieval system is primarily semantic.

Flow:

Question
→ Query Embedding
→ Active-Only Eligible Chunks
→ Embedding Compatibility Validation
→ Stale-Embedding Validation
→ Cosine Similarity
→ Candidate Ranking
→ Deterministic Reranking
→ Evidence Threshold
→ Final Evidence Set

---

## Current Embedding Model

Model:

`sentence-transformers/all-MiniLM-L6-v2`

Purpose:

Local prototype semantic embedding model.

This model is used for learning and evaluation and is not claimed to be the final production healthcare embedding model.

---

## Baseline Retrieval Controls

Current controls include:

- lifecycle eligibility
- model compatibility
- dimension compatibility
- stale-embedding detection
- candidate_k
- final_k
- configurable similarity threshold
- final lifecycle validation

---

## Baseline Evaluation Dataset

The current benchmark includes cases covering:

- operational escalation
- workforce pressure
- bed capacity
- governance
- business continuity
- winter pressure
- insufficient evidence
- clinical out-of-scope questions
- lifecycle conflicts
- prompt injection
- cross-document retrieval
- unsupported general knowledge

---

## Baseline Test Status

Record final Week 17 regression result here:

- Tests passed:
- Tests failed:
- Errors:

Example:

`XXX passed, 0 failed, 0 errors`

Replace XXX with the actual result.

---

## Known Baseline Limitations

The current system does not yet include:

- keyword retrieval
- BM25
- hybrid retrieval
- reciprocal-rank fusion
- document-diversity controls
- learned reranking
- production vector infrastructure
- production Azure deployment
- Fabric deployment
- production authentication

---

## Week 18 Comparison Goal

Week 18 will compare:

### Configuration A

Semantic retrieval only

### Configuration B

Keyword / BM25 retrieval only

### Configuration C

Hybrid semantic + keyword retrieval

Each configuration should be evaluated against the same benchmark where possible.

---

## Baseline Principle

New technology will only be retained if evaluation shows that it improves retrieval quality, governance behaviour, explainability, or operational usefulness.
