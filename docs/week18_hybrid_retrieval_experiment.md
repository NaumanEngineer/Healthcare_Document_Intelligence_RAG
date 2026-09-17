# Week 18 — Hybrid Retrieval Experiment

## Objective

Compare three retrieval approaches against the same controlled
Healthcare Document Intelligence benchmark:

1. semantic retrieval
2. BM25 keyword retrieval
3. hybrid retrieval using Reciprocal Rank Fusion

The purpose is to determine whether hybrid retrieval provides a
measurable improvement rather than assuming that additional
complexity is beneficial.

---

## Baseline

### Semantic Retrieval

Strengths:

- paraphrases
- conceptual similarity
- natural-language variation

Potential weakness:

- may retrieve conceptually related but operationally less
  precise evidence

---

## Keyword Retrieval

BM25 was introduced during Week 18 Day 2.

Strengths:

- exact terminology
- document-specific phrases
- operational language
- acronyms

Potential weakness:

- paraphrased questions
- vocabulary mismatch

---

## Hybrid Retrieval

Hybrid retrieval combines ranked output from:

- semantic retrieval
- BM25 retrieval

using Reciprocal Rank Fusion.

Raw BM25 scores and cosine-similarity scores are not directly
combined.

---

## Metrics

The experiment evaluates:

- Top-1 document success
- Top-k document success
- multi-document retrieval
- expected abstention
- Active-only lifecycle compliance
- qualitative failure cases

---

## Governance Requirement

Retrieval performance must never be improved by weakening
document lifecycle controls.

Draft and Superseded documents remain ineligible for normal
retrieval.

---

## Evaluation Corpus

The benchmark includes:

- exact terminology queries
- paraphrased queries
- overlapping documents
- cross-document questions
- unsupported questions
- lifecycle conflict cases
- prompt-injection-style cases

---

## Results

### Semantic

Top-1 success:
TBC

Top-k success:
TBC

Abstention success:
TBC

Active-only compliance:
TBC

### BM25

Top-1 success:
TBC

Top-k success:
TBC

Abstention success:
TBC

Active-only compliance:
TBC

### Hybrid

Top-1 success:
TBC

Top-k success:
TBC

Abstention success:
TBC

Active-only compliance:
TBC

---

## Failure Analysis

Results will be reviewed by query rather than relying only on
aggregate accuracy.

Questions to investigate:

1. Where did semantic retrieval succeed but BM25 fail?
2. Where did BM25 succeed but semantic retrieval fail?
3. Did hybrid recover either failure?
4. Did hybrid introduce new failures?
5. Did lifecycle controls remain intact?
6. Did unsupported queries retrieve weak but plausible evidence?
7. Did the existing reranker improve or damage the fused ranking?

---

## Decision Rule

Hybrid retrieval will not automatically replace the semantic
baseline.

It should be retained only if evaluation demonstrates useful
improvement in retrieval quality, robustness, or operational
coverage without reducing governance controls.
