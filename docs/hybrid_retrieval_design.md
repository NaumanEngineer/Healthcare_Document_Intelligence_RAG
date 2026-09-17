# Hybrid Retrieval Design

## Objective

Combine semantic retrieval and BM25 keyword retrieval without
naively combining incompatible raw scores.

---

## Why Hybrid Retrieval

Semantic search is strong when the user's wording differs from
the source document.

BM25 is strong when exact operational terminology is important.

Neither method is assumed to be universally superior.

The hybrid layer combines their ranked outputs.

---

## Retrieval Flow

User Question
→ Semantic Retrieval
→ BM25 Retrieval
→ Reciprocal Rank Fusion
→ Hybrid Candidate Ranking
→ Existing Reranking
→ Evidence Threshold
→ Final Evidence

---

## Reciprocal Rank Fusion

RRF combines result positions rather than raw retrieval scores.

Conceptually:

RRF contribution = 1 / (k + rank)

A result that appears highly ranked in both retrieval systems
receives contributions from both.

This avoids directly comparing cosine-similarity scores with
BM25 scores.

---

## Example

Semantic:

1. DOC-012
2. DOC-008
3. DOC-001

BM25:

1. DOC-008
2. DOC-012
3. DOC-007

Hybrid fusion may favour DOC-008 and DOC-012 because both
retrieval methods independently rank them highly.

---

## Governance Boundary

Hybrid retrieval must not weaken existing controls.

The system must continue to enforce:

- Active-only eligibility
- provenance preservation
- lifecycle status
- evidence thresholds
- final eligibility checks

A Superseded or Draft document must not become eligible simply
because it ranks strongly in one retrieval method.

---

## Evaluation Principle

Hybrid retrieval will be retained only if benchmark evaluation
shows that it improves retrieval quality, coverage, governance,
or operational usefulness.

The benchmark comparison will include:

1. semantic only
2. BM25 only
3. hybrid retrieval
