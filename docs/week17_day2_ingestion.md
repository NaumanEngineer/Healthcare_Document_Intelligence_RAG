# Week 17 Day 2 — Document Ingestion and Cleaning

## Objective

Build a governed document-ingestion foundation for the Healthcare Document Intelligence RAG project.

The Day 2 pipeline focuses on converting approved PDF documents into structured, traceable page-level records while preserving source provenance and preparing the data for later chunking, retrieval and grounded generation.

---

## What Was Built

### 1. PDF Ingestion Design

Defined the initial ingestion architecture for:

- text-based PDFs
- page-level extraction
- source-file preservation
- explicit failure handling
- immutable raw documents

Initial parser:

- PyMuPDF

OCR and scanned-document processing are intentionally outside the first implementation scope.

---

## 2. PDF Loader

Implemented:

`src/ingestion/load_documents.py`

Responsibilities include:

- validating file existence
- validating PDF file type
- extracting text page by page
- preserving one-based page numbers
- preserving source filename
- recording extraction status
- detecting whether a document contains usable text

Example page record:

```python
{
    "document_id": "DOC-001",
    "page_number": 1,
    "text": "Operational escalation guidance...",
    "source_file": "DOC-001_operational_escalation_policy.pdf",
    "extraction_status": "success"
}
