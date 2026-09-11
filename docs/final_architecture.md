# Final Week 17 Architecture

## Purpose

The system separates evidence discovery, answer generation and evaluation into independent layers.

This reduces the risk of treating the language model itself as the source of truth.

---

## Layer 1 — Document Processing

Documents
→ extraction
→ cleaning
→ metadata enrichment
→ chunking
→ chunk QA

Output:

validated, traceable document chunks.

---

## Layer 2 — Semantic Knowledge Layer

Validated chunks
→ embeddings
→ text hashes
→ Parquet
→ DuckDB catalogue

Purpose:

- semantic representation
- analytical inspection
- lifecycle analysis
- QA
- future evaluation reporting

---

## Layer 3 — Governed Retrieval

Question
→ query embedding
→ Active-only eligibility
→ embedding compatibility
→ stale-vector check
→ cosine similarity
→ candidate ranking
→ reranking
→ evidence threshold
→ final evidence

Purpose:

determine which evidence is allowed to influence the answer.

---

## Layer 4 — Grounded Generation

Final evidence
→ evidence packet
→ controlled prompt
→ evidence sufficiency decision
→ LLM interface
→ generated explanation

Purpose:

explain evidence rather than invent knowledge.

---

## Layer 5 — Answer Quality Controls

Generated answer
→ citation validation
→ baseline faithfulness screening
→ human review

Purpose:

check that answer references are valid and the response appears supported by retrieved evidence.

---

## Layer 6 — Evaluation

Benchmark questions
→ retrieval evaluation
→ abstention evaluation
→ lifecycle evaluation
→ citation QA
→ faithfulness analysis
→ failure analysis

Purpose:

measure where the system works and where it fails.

---

## Future Enterprise Mapping

Local prototype:

Python
→ Parquet
→ DuckDB
→ local embedding model
→ modular LLM interface

Potential enterprise evolution:

Microsoft Fabric / OneLake
→ governed healthcare data and document layer
→ Azure AI Search
→ Azure OpenAI
→ evaluation and monitoring
→ Power BI
→ human review workflow

The governance contracts should remain stable even when the underlying technology changes.
