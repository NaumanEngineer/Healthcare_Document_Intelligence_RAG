# Week 18 Portfolio Evidence

## Project

Healthcare Document Intelligence / RAG Assistant

---

# CV Bullet

Built and evaluated a governed healthcare RAG retrieval layer using semantic search, BM25, hybrid retrieval and reciprocal-rank fusion across 14 controlled operational-policy cases. Improved abstention success from 0% to 100% through deterministic scope controls while preserving 70% Top-1, 90% Top-k and 100% Active-only lifecycle compliance. Added confidence-based AUTO_ANSWER, REVIEW_REQUIRED and ABSTAIN routing with structured audit records and human-review controls.

---

# Short CV Version

Built a governed NHS-style RAG assistant with retrieval benchmarking, lifecycle filtering, 100% abstention success, human-review routing and auditable evidence controls.

---

# Interview — 60 Second Technical Explanation

I built a healthcare document intelligence assistant designed for operational policy rather than general chatbot use.

I first implemented semantic retrieval and then compared it against BM25, hybrid retrieval and RRF-only fusion using a controlled 14-case benchmark.

Semantic and the original hybrid approach both achieved 70% Top-1 and 90% Top-k retrieval. BM25 and RRF-only were weaker.

The more important finding was that retrieval relevance alone was not enough. Out-of-scope questions such as medication prescribing could still retrieve semantically related operational documents.

I therefore added a deterministic scope gate, which improved abstention success from 0% to 100% without reducing retrieval performance.

I then added a governance layer that routes cases to AUTO_ANSWER, REVIEW_REQUIRED or ABSTAIN based on evidence strength, lifecycle status, ambiguity and cross-document reasoning.

The system also records an audit trail so the evidence and decision can be inspected later.

---

# Interview — NHS Manager Explanation

The system helps staff find the right operational guidance quickly, but it does not automatically trust every search result.

If the evidence is clear and comes from approved current documents, the system can provide a grounded response.

If the evidence is ambiguous or several policies need to be interpreted together, it routes the question for human review.

If the question is outside the approved scope, such as clinical prescribing advice, the system refuses to answer from the operational-policy library.

This reduces the risk of staff receiving confident but unsupported guidance while still making approved operational information easier to access.

---

# Key Evidence

## Retrieval Benchmark

Semantic:

- Top-1: 70%

- Top-k: 90%

- Abstention: 100%

- Active-only: 100%

Hybrid:

- Top-1: 70%

- Top-k: 90%

- Abstention: 100%

- Active-only: 100%

BM25:

- Top-1: 20%

- Top-k: 40%

RRF-only:

- Top-1: 40%

- Top-k: 50%

---

# Governance Outcomes

Across 14 controlled evaluation cases:

- AUTO_ANSWER: 3

- REVIEW_REQUIRED: 8

- ABSTAIN: 3

The AUTO_ANSWER cases represented clear operational topics with sufficiently strong Active evidence.

The ABSTAIN cases represented unsupported or out-of-scope requests.

The remaining cases were conservatively routed to human review.

---

# Engineering Lessons

1. Higher retrieval complexity does not automatically improve accuracy.

2. Semantic similarity does not equal sufficient evidence.

3. Document lifecycle status matters independently of relevance.

4. Out-of-scope questions require explicit controls rather than similarity thresholds alone.

5. Human review should be triggered by ambiguity, not simply by the number of documents retrieved.

6. AI governance should be measurable and testable rather than only described in documentation.

---

# Portfolio Positioning

This project demonstrates more than basic RAG implementation.

It provides evidence of:

- document ingestion;

- metadata governance;

- chunking;

- embeddings;

- semantic retrieval;

- BM25 retrieval;

- hybrid retrieval;

- reranking;

- retrieval benchmarking;

- lifecycle controls;

- abstention;

- human-review routing;

- auditability;

- evidence-based evaluation;

- healthcare AI governance.

The project is positioned as a governed operational evidence assistant rather than an autonomous healthcare decision-maker.

