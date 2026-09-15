# Keyword vs Semantic Retrieval

## Semantic Retrieval

Semantic retrieval uses embeddings to identify text with similar meaning.

Strengths:

- paraphrased questions
- concept matching
- natural-language variation
- related terminology

Weaknesses:

- may retrieve conceptually similar but less precise documents
- exact specialist terminology may not dominate ranking

---

## Keyword / BM25 Retrieval

Keyword retrieval scores documents based on query-term matches.

BM25 improves basic keyword search by considering:

- term frequency
- term rarity
- document length

Strengths:

- exact policy terminology
- acronyms
- operational phrases
- identifiable codes or named concepts

Weaknesses:

- weaker when users paraphrase
- does not truly understand meaning

---

## Healthcare Example

Query:

"What should happen when ambulance handover delays become significant?"

Keyword retrieval may strongly favour:

Ambulance Handover Escalation Guidance

because the exact terms are present.

A paraphrased query such as:

"What should happen when staff shortages threaten service capacity?"

may favour semantic retrieval because the wording may differ from the source document.

---

## Week 18 Objective

Compare:

1. semantic retrieval
2. keyword / BM25 retrieval
3. hybrid retrieval

using the same benchmark.

No retrieval method will be assumed superior without evaluation.
