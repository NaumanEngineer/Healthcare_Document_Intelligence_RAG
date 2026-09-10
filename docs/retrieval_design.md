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

Each successfully embedded chunk preserves the complete validated chunk record and adds:

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

## Embedding Model Identity

The `embedding_model` field identifies the embedding model/configuration used to create a vector.

The current prototype records:

`sentence-transformers/all-MiniLM-L6-v2`

The model identifier is treated as part of the embedding contract.

Query vectors and stored chunk vectors must use compatible embedding configurations.

Future deployments may also record:

- model revision
- provider
- normalization configuration
- deployment identifier

These are deferred until Azure or another hosted embedding service is introduced.

---

## Embedding Dimensions

The `embedding_dimensions` field records:

`len(vector)`

Vector dimensions must be validated before similarity comparison.

A query vector must have the same dimensions as the chunk vectors it is compared against.

Dimension mismatch is treated as an explicit failure rather than silently continuing.

---

## text_hash

A deterministic SHA-256 fingerprint is created from the exact text used to generate the embedding.

Purpose:

- detect changed chunk text
- identify stale embeddings
- support reproducibility
- prevent accidental reuse of embeddings after content changes

The text hash is not a replacement for the readable chunk ID.

---

## Embedding Failure Handling

Embedding failures must be explicit.

The pipeline must not:

- silently drop failed chunks
- replace failed embeddings with zero vectors
- mix partially incompatible embedding configurations
- treat missing vectors as valid retrieval records

When multiple chunks are embedded, a failure must identify the affected `chunk_id`.

Potential failures include:

- invalid chunk metadata
- empty text
- model failure
- malformed numeric output
- non-finite vector values
- zero-norm vector
- dimension mismatch
- incompatible embedding configuration

---

## Batch Embedding Behaviour

The local prototype processes chunks sequentially.

If one chunk fails:

- the failure is surfaced immediately
- the failing chunk ID is included in the error
- the failed record is not silently omitted

More advanced retry or partial-success handling is deferred until a production batch-processing design is needed.

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

Preferred order:

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

Future versions may support intentionally configured access to historical or Superseded content for audit purposes.

Such behaviour must never happen accidentally.

---

## Candidate Retrieval vs Final Retrieval

Two retrieval counts are distinguished.

### candidate_k

Number of eligible semantic candidates retrieved before optional reranking.

### final_k

Number of evidence chunks ultimately returned.

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
- weak semantic evidence
- evidence that does not answer the question
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

A language model should not be used to conceal poor retrieval.

---

## Provenance Requirements

Every retrieved evidence unit must remain traceable to:

- document ID
- document title
- document version
- lifecycle status
- source file
- page
- chunk ID

Provenance must survive:

ingestion
→ cleaning
→ metadata enrichment
→ chunking
→ embedding
→ retrieval

---

## Version Awareness

Version metadata is part of retrieval governance.

A semantically strong result from an obsolete version must not automatically outrank appropriate current evidence.

Readable chunk IDs contain document version.

Example:

`DOC-001-V1.0-P003-C002`

The separate `text_hash` detects changes to the actual chunk content.

---

## Embedding Compatibility

The retrieval layer must not compare incompatible vectors.

Before similarity search, the system should verify:

- embedding model compatibility
- embedding dimension compatibility
- finite vector values
- non-zero vector norms

Mixing incompatible embedding configurations may produce meaningless similarity scores.

---

## Overlapping Chunk Behaviour

Adjacent chunks may contain controlled overlap.

This improves context preservation but may result in repeated evidence appearing among the highest-ranked retrieval candidates.

Future retrieval evaluation should inspect:

- near-duplicate evidence
- repeated same-page chunks
- excessive same-document concentration

Deduplication or diversity controls will only be introduced if evaluation demonstrates a need.

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

DuckDB is also not treated as the primary vector-search engine in the initial implementation.

---

## Planned Parquet Knowledge Layer

Validated chunks may later be persisted to Parquet.

Conceptual local architecture:

Validated Chunks
→ Parquet
→ DuckDB
→ SQL Inspection / QA / Retrieval Evaluation

This provides a local lakehouse-style learning environment before future Microsoft Fabric implementation.

---

## Future Microsoft Fabric Mapping

The local architecture is intentionally designed to evolve from:

Python
+ Parquet
+ DuckDB
+ local embedding abstraction

toward:

Fabric OneLake
+ Lakehouse
+ enterprise orchestration
+ Azure AI embedding services
+ governed enterprise retrieval

The core Python processing logic should remain independent of storage technology where practical.

---

## QA Boundaries

Different QA layers have separate responsibilities.

### Ingestion QA

Evaluates document extraction and page-level processing.

### Chunk Metadata Validation

Determines whether one chunk satisfies the canonical structural contract.

### Chunk QA

Evaluates retrieval-unit quality characteristics such as:

- empty chunks
- duplicate IDs
- abnormal chunk sizes
- provenance problems

### Embedding QA

The embedding layer validates:

- nonempty vectors
- numeric vector values
- finite values
- non-zero vector norm
- expected dimensions
- text-hash consistency

Future embedding QA may also assess batch-wide model consistency.

### Future Retrieval QA

Will evaluate:

- correct-document retrieval
- correct-page retrieval
- Top-1 success
- Top-k success
- lifecycle filtering
- irrelevant retrieval
- insufficient-evidence handling

---

## QA Acceptance Gates

Prototype policy:

- `failed` → do not proceed automatically
- `review` → inspect before downstream use
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

Reranking will be introduced only after initial retrieval behaviour can be measured.

---

## Citation Readiness

The retrieval layer is designed to preserve enough provenance for later citations.

A basic citation can be constructed from:

- document title
- document version
- page
- source file

Where available, `source_location` should provide a durable source reference.

Citation generation itself is deferred until grounded-answer generation.

---

## Current Limitations

The current prototype does not yet include:

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

The local embedding layer currently uses a lightweight sentence-transformer model for learning and prototype evaluation.

---

## Design Principle

The retrieval system follows this principle:

> Evidence must be structurally valid, provenance-preserving, lifecycle-appropriate, embedding-compatible and semantically relevant before it is presented to a language model.
