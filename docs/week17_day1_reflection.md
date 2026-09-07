# Week 17 Day 1 — RAG Foundations Reflection

## What I Learned

Today I moved from structured operational intelligence into unstructured healthcare document intelligence.

I learned that Retrieval-Augmented Generation is not simply a chatbot connected to documents.

A governed RAG system requires:

- controlled document ingestion
- reliable text extraction
- chunking
- metadata
- embeddings
- retrieval
- filtering
- reranking
- grounded generation
- citations
- evaluation
- human review

## Key RAG Mental Model

RAG can be summarised as:

Retrieval
→ Augmentation
→ Generation

However, a stronger implementation also includes:

Documents
→ Extraction
→ Cleaning
→ Chunking
→ Metadata
→ Embeddings
→ Retrieval
→ Filtering
→ Reranking
→ Evidence Selection
→ Grounded Answer
→ Citation
→ Human Review

## Main Engineering Lesson

The quality of the answer depends heavily on the quality of the retrieved evidence.

A fluent answer does not prove that the system retrieved the correct source.

Retrieval and generation therefore need to be evaluated separately.

## Healthcare Use Case

The project will build an:

Operational Policy & Escalation Intelligence Assistant

The system is designed to retrieve evidence from healthcare operational policies and guidance before generating an answer.

The language model is not treated as the authoritative source.

## Corpus Strategy

The initial corpus will remain deliberately small and controlled.

It will use synthetic and/or publicly available non-sensitive documents.

The first planned document categories include:

- Operational Escalation Policy
- Winter Pressure Plan
- Workforce Escalation Procedure
- Bed Capacity Management Procedure
- Business Continuity Procedure
- Operational Governance Standard

## Governance Principles

The system will:

- preserve source traceability
- retain document versions and status
- use non-sensitive data
- require evidence-grounded answers
- abstain when evidence is insufficient
- support human review
- avoid autonomous operational actions

## Threats Considered

Initial risks include:

- direct prompt injection
- indirect prompt injection
- corpus poisoning
- superseded policy retrieval
- retrieval failure
- unsupported generation
- citation mismatch
- embedding/vector weaknesses
- sensitive-information disclosure
- excessive agency
- overconfidence
- out-of-scope clinical questions

## Security Boundary

The Week 17 prototype will not:

- make autonomous clinical decisions
- prescribe medication
- trigger operational actions
- use patient-identifiable data
- use staff-identifiable data
- ingest confidential internal documents

## Day 1 Outcome

Day 1 established:

- project repository
- architecture
- use-case definition
- corpus strategy
- document register
- governance principles
- threat model
- initial security tests
- initial evaluation questions

The project is ready to begin document ingestion and preprocessing on Day 2.
