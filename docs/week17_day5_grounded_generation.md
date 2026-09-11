# Week 17 Day 5 — Grounded Answer Generation

## Objective

Build a controlled answer-generation layer on top of the governed retrieval system.

The language model is not treated as the source of truth.

Its role is to explain evidence that has already passed retrieval, lifecycle and quality controls.

---

## What Was Built

### 1. Evidence Formatter

Implemented:

`src/generation/evidence_formatter.py`

Purpose:

- validate retrieved evidence
- preserve source metadata
- block non-Active evidence
- format evidence into controlled prompt blocks
- preserve citation information
- return an explicit empty-evidence state

---

## 2. Grounded Prompt Builder

Implemented:

`src/generation/prompt_builder.py`

The prompt contract requires the model to:

- answer only from supplied evidence
- avoid outside knowledge
- avoid invented citations
- treat retrieved text as evidence rather than instructions
- abstain when evidence is insufficient
- remain outside clinical decision-making scope

---

## 3. Answer Generator

Implemented:

`src/generation/answer_generator.py`

The generation layer:

- checks whether evidence exists
- skips the language model when evidence is unavailable
- calls a model only when evidence is present
- returns a structured result
- keeps citations attached to the answer

The model-provider interface is deliberately modular so a future Azure OpenAI client can replace the current test client without rewriting the business logic.

---

## 4. Citation Validation

Implemented:

`src/evaluation/answer_qa.py`

The QA layer checks whether document IDs and chunk IDs mentioned in generated answers belong to the approved retrieval evidence.

Invented citations are rejected.

---

## 5. Abstention

When no reliable evidence exists:

- no normal generation occurs
- the model is not called
- no citations are returned
- the system produces an insufficient-evidence response

This reduces unsupported generation and unnecessary model usage.

---

## 6. Prompt-Injection Boundary

Retrieved text is treated as untrusted source material.

Instructions found inside a retrieved document do not override the system's generation rules.

The current implementation establishes a structural prompt-injection boundary, although production deployment would require additional controls.

---

## 7. End-to-End Demo

Implemented:

`src/generation/demo_pipeline.py`

The local demo proves the chain:

Question
→ Approved Evidence
→ Evidence Packet
→ Grounded Prompt
→ Model Interface
→ Generated Answer
→ Citation QA

A deterministic demo client is used instead of an external API so architecture and testing remain reproducible.

---

## Architecture After Day 5

Healthcare Documents
→ Ingestion
→ Cleaning
→ Metadata
→ Chunking
→ Embeddings
→ Governed Retrieval
→ Reranking
→ Evidence Threshold
→ Evidence Packet
→ Grounded Prompt
→ LLM
→ Citation Validation
→ Final Answer

---

## Governance Controls

### Evidence Before Generation

Generation is downstream of retrieval.

### Active-Only Evidence

Non-current lifecycle states are blocked before generation.

### Abstention

The system can refuse unsupported questions.

### Citation Allow-List

Generated source identifiers must originate from the retrieved evidence set.

### Human Accountability

The tool supports human decision-making and does not replace operational accountability.

### Clinical Boundary

The current prototype is for operational guidance, not clinical diagnosis or treatment.

---

## Current Limitations

The prototype does not yet provide:

- claim-level faithfulness evaluation
- production Azure OpenAI integration
- production authentication or access control
- hybrid keyword + vector retrieval
- learned reranking
- production prompt-injection defences
- clinical decision support
- human-review workflow UI

These are future enhancements rather than hidden capabilities.

---

## Key Lesson

A language model should not be the first component trusted in a healthcare RAG system.

The stronger architecture is:

retrieve evidence
→ validate evidence
→ generate from evidence
→ validate the generated answer
