# Week 18 — Semantic vs Keyword Retrieval

## Objective

Compare the Week 17 semantic retrieval baseline against
BM25 keyword retrieval using the same operational questions.

The purpose is not to assume one method is superior.

The purpose is to identify which query types favour each
retrieval approach.

---

## Comparison Principle

Semantic retrieval asks:

"What text has similar meaning?"

Keyword retrieval asks:

"Which text contains the strongest matching terminology?"

---

## Test Query 1 — Exact Ambulance Terminology

Question:

"What should happen when ambulance handover delays become significant?"

Expected likely source:

DOC-008 — Ambulance Handover Escalation Guidance

Observation:

To be completed after real retrieval execution.

---

## Test Query 2 — Paraphrased Staffing Pressure

Question:

"What should be done when staff shortages threaten service capacity?"

Relevant sources may include:

- DOC-003 — Workforce Escalation Procedure
- DOC-011 — Critical Staffing Contingency Procedure

Observation:

To be completed after real retrieval execution.

---

## Test Query 3 — Severe Weather

Question:

"What operational action is needed when severe weather disrupts services?"

Potentially relevant sources:

- DOC-009 — Severe Weather Operational Plan
- DOC-002 — Winter Pressure Plan
- DOC-005 — Business Continuity Procedure

Observation:

To be completed after real retrieval execution.

---

## Test Query 4 — Bed Capacity

Question:

"Which guidance covers escalation when bed capacity is under pressure?"

Expected likely source:

DOC-004 — Bed Capacity Management Procedure

Observation:

To be completed after real retrieval execution.

---

## Test Query 5 — General Operational Pressure

Question:

"What should operational teams do when multiple pressures affect normal service delivery?"

Potentially relevant sources:

- DOC-001
- DOC-012
- DOC-013

Observation:

To be completed after real retrieval execution.

---

## Expected Learning

Keyword retrieval may perform better when:

- exact NHS terminology is used
- policy names or phrases are distinctive
- acronyms or specialist language matter

Semantic retrieval may perform better when:

- the user paraphrases
- wording differs from the policy
- conceptual similarity matters more than exact terms

---

## Important Limitation

BM25 scores and semantic cosine-similarity scores are not directly comparable.

The comparison should focus on:

- ranking
- document success
- query type
- failure cases

rather than raw score size.
