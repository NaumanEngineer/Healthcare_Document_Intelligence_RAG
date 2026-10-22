# Week 28 Day 5 — Portfolio Architecture



## Healthcare Document Intelligence RAG



This document presents the portfolio architecture of the governed RAG

application in a form suitable for:



- NHS operational managers

- technical interviewers

- AI / data engineering recruiters

- portfolio reviewers



The objective is to communicate the system clearly without requiring the

reader to understand the full development history.



---



# Executive Architecture



```text

Operational Question

&#x20;       ↓

Input Validation

&#x20;       ↓

Scope Control

&#x20;       ↓

Governed Retrieval

&#x20;       ↓

Evidence Sufficiency

&#x20;       ↓

Structured Evidence Objects

&#x20;       ↓

Evidence Packet

&#x20;       ↓

Provenance Verification

&#x20;       ↓

Lifecycle / Supersession / Precedence

&#x20;       ↓

Pre-Generation Governance

&#x20;       ↓

Answer Contract

&#x20;       ↓

Controlled Answer Context

&#x20;       ↓

Deterministic Generation

&#x20;       ↓

Optional Controlled Model Provider

&#x20;       ↓

Generation Validation

&#x20;       ↓

Safe Fallback if Required

&#x20;       ↓

Citation + Faithfulness Assurance

&#x20;       ↓

Post-Generation Governance

&#x20;       ↓

Manager-Facing Presentation

&#x20;       ↓

ANSWER / REVIEW_REQUIRED / ABSTAIN
