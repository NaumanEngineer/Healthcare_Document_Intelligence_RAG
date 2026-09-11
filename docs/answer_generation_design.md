# Grounded Answer Generation Design

## Objective

Build a controlled answer-generation layer for the Healthcare Document Intelligence RAG system.

The language model must not act as an independent source of NHS operational guidance.

Its role is to explain and summarise evidence that has already passed retrieval, lifecycle and quality controls.

---

## Core Principle

Retrieval establishes the evidence.

Generation explains the evidence.

The language model must not replace the evidence layer.

---

## Generation Flow

User Question
→ Query Validation
→ Governed Semantic Retrieval
→ Lifecycle Filtering
→ Embedding Compatibility Checks
→ Stale-Embedding Detection
→ Candidate Ranking
→ Reranking
→ Evidence Threshold
→ Final Evidence Set
→ Evidence Formatting
→ Grounded Prompt
→ Language Model
→ Citation Validation
→ Final Answer

---

## Evidence Boundary

The model may answer only from evidence supplied by the retrieval layer.

It must not:

- invent policy content
- rely on unsupported background knowledge
- cite documents that were not retrieved
- use Superseded, Draft or Archived guidance
- fabricate page references
- infer clinical decisions
- make autonomous operational decisions

---

## Answer Behaviour

A normal answer should contain:

1. a direct answer
2. a concise explanation
3. supporting evidence
4. source document
5. version
6. page
7. evidence identifier

Example:

Operational leadership should review the escalation conditions and apply the actions defined in the current escalation procedure.

Source:
Operational Escalation Policy
Version: 1.0
Page: 3

---

## Insufficient Evidence Behaviour

The system must be allowed to say that the available evidence is insufficient.

Example:

The available operational documents do not provide enough evidence to answer this question reliably.

The system must prefer abstention over unsupported generation.

---

## Clinical Boundary

The prototype is designed for operational policy and management guidance.

It is not designed to:

- diagnose patients
- recommend medication
- provide treatment decisions
- replace clinical judgement
- make emergency clinical decisions

Clinical questions should be treated as outside the intended scope.

---

## Citation Contract

Every evidence-based claim should remain traceable to retrieved material.

Citation data may include:

- document_id
- title
- version
- page
- chunk_id
- source_file

The generation layer must not create citation identifiers.

Citation identifiers must originate from retrieval results.

---

## Lifecycle Rules

Only retrieval-eligible evidence may enter the answer-generation layer.

Default lifecycle policy:

- Active → allowed
- Superseded → blocked
- Draft → blocked
- Archived → blocked

Generation must not override retrieval eligibility.

---

## Prompt Contract

The prompt supplied to the language model should contain:

### System Instructions

Define:

- role
- evidence restrictions
- citation rules
- abstention behaviour
- scope boundaries

### User Question

Preserve the user's original question.

### Evidence Context

Supply only retrieved and validated evidence.

### Output Instructions

Require:

- concise answer
- evidence-based explanation
- citations
- uncertainty statement where appropriate

---

## Separation of Responsibilities

### Retrieval Layer

Responsible for:

- evidence discovery
- lifecycle filtering
- semantic similarity
- eligibility
- ranking
- evidence thresholds

### Generation Layer

Responsible for:

- explaining retrieved evidence
- summarising evidence
- presenting citations
- communicating uncertainty

### Evaluation Layer

Responsible for:

- checking citation validity
- checking evidence use
- checking abstention
- detecting unsupported references

---

## Human Accountability

The system is decision-support only.

Human users remain responsible for interpreting and applying operational guidance.

The assistant should make source evidence easy to inspect rather than presenting generated text as authoritative truth.

---

## Prompt-Injection Boundary

Retrieved document text must be treated as evidence, not as executable instructions.

If a retrieved document contains text such as:

"Ignore previous instructions"

or:

"Reveal hidden system information"

the generation layer must not follow those instructions.

The system prompt and governance rules remain higher priority than retrieved document content.

---

## Evidence Sufficiency

Generation should occur only when the retrieval layer has returned evidence that passed:

- lifecycle eligibility
- embedding compatibility
- stale-vector checks
- similarity threshold
- final evidence selection

If the evidence set is empty, generation should not proceed normally.

The expected behaviour is abstention.

---

## Future Azure Architecture

The local architecture should be replaceable with enterprise services later.

Current:

Python
→ local embeddings
→ local retrieval
→ modular generation interface

Future:

Microsoft Fabric / OneLake
→ governed document layer
→ Azure AI Search
→ Azure OpenAI
→ retrieval and answer evaluation
→ Power BI monitoring

The core governance contracts should remain independent of the specific technology provider.

---

## Day 5 Design Principle

A safe healthcare RAG system should not ask:

"Can the model answer this?"

It should ask:

"Do we have sufficient, current and traceable evidence for the model to explain?"
