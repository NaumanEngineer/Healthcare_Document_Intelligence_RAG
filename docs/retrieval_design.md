# Retrieval Design

## Objective

Design a governed semantic retrieval layer for healthcare operational documents.

The retrieval system must identify relevant evidence while preserving provenance, document lifecycle, version awareness and traceability.

---

## Retrieval Flow

User Query
→ Query Embedding
→ Vector Similarity Search
→ Metadata Filtering
→ Candidate Evidence
→ Reranking
→ Final Evidence Set

Generation is intentionally kept separate from retrieval.

---

## Embeddings

Embeddings convert text into numeric vectors that represent semantic meaning.

Both document chunks and user queries are embedded into the same vector space.

Similarity between vectors is then used to identify relevant evidence.

---

## Query Embeddings

A user question is converted into a vector using the same embedding model used for document chunks.

Example:

Question:

`What actions are required during workforce escalation?`

The resulting query vector is compared with chunk vectors.

---

## Chunk Embeddings

Every validated retrieval-ready chunk will receive an embedding.

The embedding layer must preserve the relationship between:

- chunk_id
- document_id
- version
- page
- status
- text
- vector

---

## Similarity Search

The initial prototype will use cosine similarity to compare query vectors with chunk vectors.

Similarity scores indicate relative semantic closeness.

They are not treated as absolute safety thresholds.

---

## Top-K Retrieval

The system will retrieve multiple candidate chunks rather than assuming the highest-scoring vector is always correct.

Initial prototype:

`top_k = 3 to 5`

Candidate evidence will later be reranked.

---

## Metadata Governance

Semantic similarity alone is not sufficient.

Retrieval must account for metadata including:

- status
- version
- document type
- source
- page provenance

Active documents should normally be preferred over Superseded, Draft or Archived content.

---

## Retrieval vs Generation

Retrieval and generation are evaluated separately.

This allows failures to be diagnosed as:

1. retrieval failure
2. evidence-selection failure
3. generation failure

This separation improves transparency and governance.

---

## DuckDB Role

DuckDB is used as a local analytical knowledge catalogue.

It supports:

- querying chunk metadata
- analysing QA results
- inspecting ingestion batches
- analysing retrieval evaluation results
- querying Parquet outputs

DuckDB is not the embedding model.

---

## Future Fabric Mapping

The local architecture can later evolve approximately as:

Python + Parquet + DuckDB
→ Fabric OneLake + Lakehouse
→ Azure AI embeddings
→ governed enterprise retrieval

The current implementation is intentionally modular so storage and embedding services can be replaced later.

---

## Current Limitations

The prototype does not yet include:

- embeddings
- vector indexing
- reranking
- hybrid keyword + semantic search
- generation
- production authentication
- access controls

These are introduced incrementally after retrieval quality can be tested.
