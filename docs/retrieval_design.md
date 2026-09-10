# Retrieval Design

## Objective

Design a governed semantic retrieval layer for healthcare operational documents.

The retrieval system must identify relevant evidence while preserving provenance, document lifecycle, version awareness, traceability and explicit retrieval-quality controls.

Retrieval and generation are intentionally separated so that retrieval failures can be evaluated independently from language-model behaviour.

---

## Retrieval Flow

The planned retrieval flow is:

User Query
→ Query Validation
→ Query Embedding
→ Eligible Chunk Set
→ Vector Similarity
→ Candidate Retrieval
→ Optional Reranking
→ Final Evidence Set
→ Final Eligibility Verification

Generation occurs only after retrieval has produced an acceptable evidence set.

---

## Core Retrieval Principle

Semantic similarity alone is not sufficient for governed healthcare retrieval.

A chunk may be semantically relevant but still be unsuitable because it is:

- Superseded
- Draft
- Archived
- missing provenance
- linked to an incompatible embedding configuration
- generated from stale or changed text

Retrieval therefore combines semantic relevance with explicit metadata and lifecycle controls.

---

## Embedding Input Contract

Only chunks that pass the canonical chunk metadata validator are considered embedding-ready.

The required sequence is:

document metadata enrichment
→ chunking
→ canonical chunk validation
→ embedding

Low-level chunks that have not passed canonical validation must not enter the embedding layer.

Embedding-ready chunks should contain at minimum:

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

Optional fields may include:

- source_location
- ingestion_batch_id
- section
- topic

---

## Embedding Output Contract

Each successfully embedded chunk should preserve the complete validated chunk record and add:

- vector
- embedding_model
- embedding_dimensions
- text_hash

### vector

The numeric embedding representation of the chunk text.

The vector must:

- contain numeric values only
- contain finite values
- contain at least one value
- have a non-zero norm
- match the expected embedding dimensions

Zero vectors must not be silently accepted.

---

### embedding_model

Identifies the embedding model and configuration used to create the vector.

The model identifier should be specific enough to distinguish incompatible embedding configurations.

Query vectors and chunk vectors must use the same embedding configuration.

---

### embedding_dimensions

The number of values in the embedding vector.

This must equal:

`len(vector)`

and must also match the query embedding dimensions used during similarity search.

---

### text_hash

A deterministic fingerprint of the chunk text.

The initial implementation may use SHA-256.

Purpose:

- detect changed chunk text
- identify stale embeddings
- support reproducibility
- reduce the risk of reusing an embedding for changed evidence

The text hash is not a replacement for the human-readable chunk ID.

---

## Embedding Failure Handling

Embedding failures must be explicit.

The pipeline must not:

- silently drop failed chunks
- replace failed embeddings with zero vectors
- mix partially incompatible embedding configurations
- treat missing vectors as valid retrieval records

Potential failure states include:

- empty text
- model failure
- invalid numeric output
- non-finite vector values
- zero-norm vector
- unexpected dimensions
- incompatible model configuration

Failures should be surfaced for QA and review.

---

## Query Contract

A retrieval request requires:

- nonblank query text
- positive integer `candidate_k`
- positive integer `final_k`
- explicit metadata filters where required

The query embedding must use the same embedding model and configuration as the stored chunk embeddings.

Invalid queries should fail clearly rather than entering similarity search.

---

## Query Embeddings

A user question is converted into a numeric vector using the same embedding configuration used for document chunks.

Example query:

`What actions are required during workforce escalation?`

The resulting query vector is compared with eligible chunk vectors.

---

## Similarity Search

The initial prototype will use cosine similarity.

Cosine similarity measures the directional similarity between the query vector and each chunk vector.

Higher scores generally indicate stronger semantic similarity.

Similarity scores are treated as relative retrieval signals rather than universal safety thresholds.

A high similarity score does not by itself prove that evidence is current, valid or sufficient.

---

## Metadata Filtering Order

Hard retrieval eligibility rules should be applied before final candidate selection.

Prototype default lifecycle policy:

- Active documents are eligible
- Superseded documents are excluded
- Draft documents are excluded
- Archived documents are excluded

This avoids the following failure:

1. semantic search retrieves only a very small top-k set
2. most of those chunks are later removed by lifecycle filtering
3. eligible chunks ranked slightly lower are never considered

The preferred order is:

Query
→ Query Embedding
→ Eligible Chunk Set
→ Similarity Scoring
→ Candidate Retrieval
→ Optional Reranking
→ Final Evidence

Eligibility should also be verified again before returning final evidence.

---

## Retrieval Eligibility

The default prototype retrieval policy is strict:

`status == Active`

This is intentionally stronger than simply preferring Active documents.

Future versions may support explicit policy-controlled retrieval of historical or Superseded content for audit or comparison purposes.

Such behaviour must be intentionally configured rather than happening automatically.

---

## Candidate Retrieval vs Final Retrieval

Two retrieval counts are distinguished.

### candidate_k

Number of eligible semantic candidates retrieved before optional reranking.

Example:

`candidate_k = 10`

### final_k

Number of evidence chunks ultimately returned.

Example:

`final_k = 3`

This distinction avoids ambiguity around the meaning of `top_k`.

The relationship should normally satisfy:

`final_k <= candidate_k`

---

## Retrieval Result Contract

Each final retrieval result should preserve:

- rank
- similarity_score
- chunk_id
- document_id
- title
- document_type
- source_type
- version
- effective_date
- status
- source_file
- source_location where available
- page
- chunk_number
- text
- embedding_model
- embedding_dimensions
- text_hash

These fields support:

- citation construction
- retrieval debugging
- version checking
- provenance
- auditability
- evaluation

---

## Insufficient Evidence

The system must support an explicit insufficient-evidence outcome.

The nearest available vector result should not automatically be treated as useful evidence.

Possible insufficient-evidence situations include:

- empty query
- no eligible chunks
- no valid vectors
- incompatible embedding configurations
- fewer useful results than requested
- weak semantic evidence
- evidence that does not answer the user question
- evidence available only in excluded lifecycle states

The retrieval layer should be able to return an empty or insufficient-evidence outcome rather than forcing a result.

---

## Retrieval and Generation Separation

Retrieval is evaluated independently from generation.

This allows failures to be classified as:

1. ingestion failure
2. chunking failure
3. metadata failure
4. embedding failure
5. retrieval failure
6. evidence-selection failure
7. generation failure

This separation improves:

- debugging
- explainability
- evaluation
- governance
- system safety

A language model should not be used to conceal poor retrieval.

---

## Provenance Requirements

Every retrieved evidence unit must remain traceable to:

- document ID
- document title
- document version
- document lifecycle status
- source file
- page
- chunk ID

Where available, `source_location` should provide a durable reference to the original document.

Provenance must survive:

ingestion
→ cleaning
→ metadata enrichment
→ chunking
→ embedding
→ retrieval

---

## Source Field Definitions

The term `source` is avoided when it could be ambiguous.

The canonical fields are:

### source_type

Describes the origin category.

Examples:

- Synthetic
- Public

### source_file

The source filename used during ingestion.

### source_location

Optional durable location or URI for the original source.

This distinction improves traceability and future citation design.

---

## Version Awareness

Version metadata is part of retrieval governance.

A semantically strong result from an obsolete version must not automatically outrank appropriate current evidence.

Chunk IDs include document version for readability and traceability.

Example:

`DOC-001-V1.0-P003-C002`

However, chunk IDs are not content hashes.

The separate `text_hash` field provides content-change detection.

---

## Embedding Compatibility

The retrieval layer must not compare incompatible vectors.

Before similarity search, the system should verify:

- embedding model compatibility
- embedding dimension compatibility
- finite vector values
- non-zero vector norms

Mixing embedding configurations may produce meaningless similarity scores.

---

## Overlapping Chunk Behaviour

Adjacent chunks may contain controlled overlap.

This improves context preservation but may also cause multiple highly similar chunks from the same page to dominate retrieval results.

Future retrieval evaluation should therefore inspect:

- repeated evidence
- near-duplicate candidates
- excessive same-page concentration

Deduplication or diversity controls may later be introduced if evaluation shows they are necessary.

---

## Lifecycle Changes

Document lifecycle metadata may change after embeddings are created.

For example:

`Active → Superseded`

This does not necessarily require immediate re-embedding because lifecycle status is metadata rather than semantic content.

However, retrieval eligibility must use the current lifecycle metadata rather than assuming the status that existed at embedding time.

---

## Stale Embedding Detection

If chunk text changes, the existing embedding may become stale.

The `text_hash` field provides a mechanism to compare:

stored text hash
vs
current chunk text hash

A mismatch indicates that the embedding should be regenerated.

---

## DuckDB Role

DuckDB is planned as the local analytical knowledge catalogue.

It has not yet been implemented in the current prototype.

Planned uses include:

- querying Parquet chunk outputs
- analysing chunk metadata
- inspecting ingestion batches
- analysing QA results
- analysing retrieval evaluation results

DuckDB is not the embedding model.

DuckDB is also not treated as the core vector-search system in the initial implementation.

---

## Planned Parquet Knowledge Layer

Validated chunks may later be written to Parquet.

Conceptual local flow:

Validated Chunks
→ Parquet
→ DuckDB
→ SQL Inspection / QA / Retrieval Evaluation

This provides a local lakehouse-style learning environment before future Microsoft Fabric implementation.

---

## Future Microsoft Fabric Mapping

The local architecture is intentionally designed to evolve toward:

Python
+ Parquet
+ DuckDB
+ local embedding abstraction

to:

Fabric OneLake
+ Lakehouse
+ enterprise orchestration
+ Azure AI embedding services
+ governed enterprise retrieval

The current Python components should remain independent of storage technology where practical.

---

## QA Boundaries

Different QA layers have different responsibilities.

### Ingestion QA

Evaluates document extraction and page-level processing.

It must not be used to calculate chunk-level metrics.

### Chunk Metadata Validation

Determines whether one chunk satisfies the canonical structural contract.

### Chunk QA

Evaluates chunk quality characteristics such as:

- empty chunks
- duplicate IDs
- abnormal chunk sizes
- provenance problems

### Future Embedding QA

Will evaluate:

- missing vectors
- invalid vectors
- dimension mismatches
- stale embeddings
- incompatible embedding configurations

### Future Retrieval QA

Will evaluate:

- correct-document retrieval
- correct-page retrieval
- Top-1 success
- Top-k success
- lifecycle filtering
- irrelevant retrieval
- insufficient-evidence handling

These layers should remain separate.

---

## QA Acceptance Gates

QA results should influence whether data proceeds to later stages.

Prototype policy:

- `failed` → do not proceed automatically
- `review` → requires inspection before downstream use
- `passed` → eligible to continue, subject to canonical validation

The exact production policy may later become more sophisticated.

---

## Reranking

Reranking is a planned optional stage.

It has not yet been implemented.

The initial retrieval implementation will first establish:

- reliable embeddings
- vector validation
- metadata filtering
- semantic similarity
- candidate retrieval
- retrieval evaluation

Reranking will be introduced only after the initial retrieval behaviour can be measured.

---

## Batch Lineage

`ingestion_batch_id` is an optional lineage field.

A batch identifier should be created once per ingestion run and propagated through all derived pages and chunks from that run.

Later, embedding runs may also receive their own batch or model-version metadata if needed.

---

## Citation Readiness

The retrieval layer is designed to provide enough provenance for later citations.

A basic citation can be constructed from:

- document title
- document version
- page
- source file

Where available, `source_location` should provide a durable path or URI.

Citation generation itself is deferred until the grounded-answer stage.

---

## Current Limitations

The current prototype does not yet include:

- embedding implementation
- vector indexing
- semantic retrieval
- retrieval thresholds
- hybrid keyword + vector retrieval
- reranking
- generation
- citation rendering
- DuckDB implementation
- Parquet persistence
- Microsoft Fabric implementation
- production authentication
- production access controls

These capabilities will be added incrementally after the underlying contracts are validated.

---

## Design Principle

The retrieval system follows this principle:

> Evidence must be structurally valid, provenance-preserving, lifecycle-appropriate and semantically relevant before it is presented to a language model.

This keeps retrieval quality and governance as first-class parts of the healthcare RAG architecture.
