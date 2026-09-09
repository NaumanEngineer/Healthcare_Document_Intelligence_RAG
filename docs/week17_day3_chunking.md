# Week 17 Day 3 — Chunking and Metadata Engineering

## Objective

Transform cleaned healthcare document pages into retrieval-ready chunks while preserving meaning, provenance, document lifecycle metadata and quality controls.

---

## What Was Built

### 1. Chunking Strategy

The project uses a paragraph-first, structure-aware chunking approach.

The pipeline:

- preserves document boundaries
- preserves page boundaries
- prefers paragraph boundaries
- splits oversized paragraphs at word boundaries
- uses controlled word-aligned overlap
- avoids empty chunks
- preserves upstream metadata

Prototype parameters:

- target chunk size: approximately 1000 characters
- overlap: approximately 150 characters

These values are starting points and will later be tuned using retrieval evaluation.

---

## 2. Stable Chunk Identifiers

Each retrieval-ready chunk receives a stable identifier.

Example:

`DOC-001-V1.0-P003-C002`

The identifier contains:

- document ID
- document version
- page number
- chunk ordinal

This supports traceability, debugging and version-aware retrieval.

---

## 3. Retrieval Metadata

Canonical chunk metadata includes:

- chunk_id
- document_id
- title
- document_type
- source_type
- version
- effective_date
- status
- source_file
- page
- chunk_number
- text

Optional enrichment fields include:

- section
- topic
- source_location
- ingestion_batch_id

Metadata is treated as part of retrieval governance rather than as descriptive information only.

---

## 4. Lifecycle-Aware Retrieval

Prototype document lifecycle states include:

- Active
- Superseded
- Draft
- Archived

Retrieval-ready chunks must pass metadata validation.

The current eligibility rule allows only chunks belonging to Active documents to be considered retrieval eligible.

---

## 5. Complete Page-to-Chunk Pipeline

The canonical flow is:

PDF
→ page extraction
→ document metadata enrichment
→ ingestion batch lineage
→ text cleaning
→ chunking
→ metadata validation
→ retrieval-ready chunks

The orchestration layer is implemented in:

`src/preprocessing/build_chunks.py`

---

## 6. Chunk Quality Assurance

Implemented:

`src/evaluation/chunk_qa.py`

The QA layer checks:

- empty chunks
- duplicate chunk IDs
- short chunks
- long chunks
- missing or invalid provenance
- chunk-length distribution
- overall quality status

Prototype quality statuses:

- passed
- review
- failed

Canonical metadata validation handles structural correctness.

Chunk QA handles quality heuristics.

---

## 7. Testing

Automated tests cover:

- chunk size validation
- invalid overlap settings
- paragraph splitting
- word-boundary splitting
- word-aligned overlap
- metadata preservation
- version-aware chunk IDs
- page isolation
- missing provenance
- lifecycle status
- batch lineage
- integration between enrichment, chunking and validation
- chunk QA classification

The complete repository test suite currently passes.

---

## Governance Principles

### Provenance

Every chunk remains traceable to its document, version, source file and page.

### Lifecycle Awareness

Superseded or inappropriate document states can later be filtered before retrieval.

### Reproducibility

Ingestion batch identifiers provide lineage across processing runs.

### Evidence Integrity

Chunking avoids unnecessary splitting of words and preserves page boundaries.

### Validation Before Retrieval

A chunk is not considered retrieval-ready until it passes canonical metadata validation.

---

## Cross-Pollination With Earlier Work

The design reuses concepts from the NHS Operational Data Platform:

- data grain
- lineage
- quality status
- validation
- stable identifiers
- reproducible transformations

In the structured platform, one analytical record represents a Trust-date.

In the document intelligence platform, one retrieval record represents one evidence chunk from one document version and one page.

---

## Future Microsoft Fabric Mapping

The architecture can later map to:

Raw PDFs
→ OneLake raw layer
→ processed page layer
→ validated chunk table
→ retrieval / AI layer
→ Power BI pipeline monitoring

The current Python functions are intentionally kept independent of storage technology so they can later run in Fabric notebooks or pipelines.

---

## Current Limitations

The current chunking system does not yet include:

- token-aware sizing
- embedding-based semantic chunking
- sentence-perfect overlap
- automatic topic classification
- automatic section detection
- retrieval
- embeddings
- reranking

These are intentionally deferred until retrieval quality can be evaluated.

---

## Reflection

The main lesson from Day 3 is that chunking is an evidence-engineering problem rather than a simple text-splitting task.

Poor chunk boundaries, missing provenance, weak lifecycle metadata or duplicate identifiers can reduce retrieval reliability even when the embedding model is strong.

The project therefore treats chunk structure, metadata and QA as first-class parts of the RAG system.
