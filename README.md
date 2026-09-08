# Healthcare Document Intelligence RAG

## Overview

This project develops a governed healthcare document intelligence system using Retrieval-Augmented Generation (RAG).

The system is designed to retrieve relevant evidence from healthcare operational and governance documents before generating an answer.

The project focuses on:

- healthcare document ingestion
- text preprocessing
- structure-aware chunking
- metadata design
- semantic retrieval
- hybrid retrieval concepts
- reranking
- evidence-grounded generation
- citations
- retrieval evaluation
- governance
- human oversight

## Problem

Healthcare organisations operate with large volumes of policies, procedures, escalation guidance and operational documentation.

Important information can be difficult to locate quickly, particularly when staff need to understand which document, section or policy supports an operational decision.

This project explores how RAG can provide evidence-grounded access to healthcare documentation while preserving traceability and human review.

## Intended Users

Potential users include:

- NHS information and performance teams
- operational managers
- governance teams
- winter-pressure teams
- workforce planners
- analysts
- healthcare AI engineers

## Current Scope

The initial implementation will use synthetic and/or publicly available non-sensitive documents.

No patient-identifiable information will be used.

## Planned Architecture

Documents  
→ Ingestion  
→ Cleaning  
→ Chunking  
→ Metadata  
→ Embeddings  
→ Retrieval  
→ Reranking  
→ Evidence-Grounded Generation  
→ Citation  
→ Human Review

## Governance Principles

The language model is not treated as the source of truth.

Retrieved source evidence is the primary basis for generated answers.


## Document Ingestion Layer

The current implementation includes a governed PDF ingestion pipeline using PyMuPDF.

The ingestion layer:

- validates approved PDF inputs
- extracts page-level text
- preserves document and page provenance
- normalizes formatting noise
- attaches version-aware document metadata
- records extraction quality
- supports automated ingestion QA tests

Raw source documents remain unchanged in `data/raw/`.

The ingestion architecture is intentionally modular so it can later support chunking, retrieval, Azure services and Microsoft Fabric storage/orchestration.

If sufficient evidence cannot be retrieved, the system should state that the available evidence is insufficient rather than fabricate policy content.

## Status

Week 17 — RAG foundation and document-intelligence design.
