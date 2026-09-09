# Chunk Metadata Schema

## Objective

Define the canonical metadata contract for retrieval-ready chunks in the Healthcare Document Intelligence RAG system.

Metadata is treated as part of retrieval quality and governance rather than as descriptive information only.

---

## Chunk Grain

One record represents:

> One retrievable evidence unit from one document, from one page, with one stable chunk identifier.

Chunks do not cross document boundaries.

The current prototype also preserves page boundaries.

---

## Required Fields

### chunk_id

Unique identifier for the retrieval unit.

Example:

`DOC-001-V1.0-P003-C002`

The identifier contains:

- document ID
- document version
- page
- chunk ordinal

---

### document_id

Stable identifier for the source document.

Example:

`DOC-001`

---

### title

Human-readable document title.

Example:

`Operational Escalation Policy`

---

### document_type

Classification of the source document.

Examples:

- Operational Policy
- Procedure
- Operational Plan
- Governance

---

### source_type

Origin classification.

Initial values may include:

- Synthetic
- Public

Sensitive or confidential healthcare content is outside the prototype scope.

---

### version

Document version associated with the chunk.

Version metadata supports lifecycle-aware retrieval and reduces the risk of retrieving obsolete guidance.

---

### effective_date

Date from which the document version is intended to apply.

Format:

`YYYY-MM-DD`

---

### status

Lifecycle state of the source document.

Supported prototype values:

- Active
- Superseded
- Draft
- Archived

Retrieval should later prefer or restrict results to appropriate lifecycle states.

---

### source_file

Original source filename.

This supports provenance, debugging and citation construction.

---

### page

One-based page number of the source evidence.

Page provenance is preserved through ingestion, cleaning and chunking.

---

### chunk_number

Ordinal position of the chunk within the source page.

---

### text

The cleaned retrieval-ready evidence text.

---

## Optional Enrichment Fields

### section

Document section or subsection associated with the chunk.

Example:

`Workforce Escalation`

---

### topic

High-level operational topic.

Examples:

- workforce
- bed_capacity
- escalation
- business_continuity
- governance

Topic metadata may later support retrieval filtering and evaluation.

---

### source_location

Optional source URI, repository location or public source reference.

---

### ingestion_batch_id

Identifier for the ingestion run that produced the chunk.

This supports:

- reproducibility
- reprocessing
- lineage
- debugging
- auditability

---

## Retrieval Governance

Metadata may later be used to:

1. exclude Draft documents
2. exclude or penalise Superseded documents
3. restrict retrieval by document type
4. filter by operational topic
5. verify document versions
6. construct citations
7. investigate retrieval failures

Semantic similarity alone is not sufficient for governed healthcare retrieval.

---

## Future Fabric Mapping

A future Microsoft Fabric Lakehouse representation may use one row per chunk.

Possible columns include:

- chunk_id
- document_id
- version
- status
- effective_date
- page
- chunk_number
- section
- topic
- source_file
- ingestion_batch_id
- text

This allows the same metadata model to support Python processing, enterprise storage, Power BI monitoring and AI retrieval.

---

## Current Limitations

The prototype does not yet automatically infer:

- document sections
- operational topics
- semantic labels

These fields may initially be supplied deterministically or manually.

LLM-generated metadata will not be introduced until its quality and governance implications can be evaluated.
