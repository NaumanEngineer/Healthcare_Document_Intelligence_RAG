# RAG Failure Analysis

## Objective

Document known and observed failure modes rather than reporting only successful outputs.

---

## Failure Type 1 — Wrong Document Retrieved

Example:

A workforce question retrieves a general escalation policy instead of the Workforce Escalation Procedure.

Possible causes:

- embedding weakness
- ambiguous wording
- overlapping chunks
- insufficient metadata filtering

Potential responses:

- improve query formulation
- test hybrid retrieval
- improve metadata-aware retrieval
- evaluate stronger embedding models

---

## Failure Type 2 — Repeated Chunks From One Document

Example:

A cross-document question returns three chunks from the same policy.

Impact:

Useful evidence from another operational domain may be missed.

Possible future responses:

- document diversity rules
- per-document caps
- maximal marginal relevance
- reranking

---

## Failure Type 3 — Weak Evidence Passes Similarity Threshold

Impact:

The generation layer receives technically similar but operationally irrelevant evidence.

Potential responses:

- empirical similarity-threshold tuning
- reranking
- hybrid search
- benchmark expansion

---

## Failure Type 4 — Correct Citation but Unsupported Claim

A model may cite a valid retrieved source while adding information not actually supported by that source.

Current control:

Lightweight claim-level lexical faithfulness evaluation.

Limitation:

Lexical overlap is not equivalent to semantic entailment.

Future improvement:

Human evaluation and stronger semantic or model-based faithfulness evaluation.

---

## Failure Type 5 — Prompt Injection in Retrieved Text

Retrieved content may contain instructions intended to influence the language model.

Current control:

Retrieved evidence is explicitly treated as source material rather than system instructions.

Future production controls would require stronger content isolation and security testing.

---

## Failure Type 6 — Unsupported Question

The user asks something outside the available evidence corpus.

Expected behaviour:

Abstain rather than use general model knowledge.

---

## Failure Type 7 — Lifecycle Error

A Superseded, Draft or Archived document enters normal answer generation.

Expected behaviour:

Fail the governance control.

Current architecture applies lifecycle controls at multiple boundaries.

---

## Evaluation Principle

Failures should be retained as engineering evidence.

The objective is not to hide weaknesses.

The objective is to understand which failure occurred, why it occurred, and which system component should be improved.
