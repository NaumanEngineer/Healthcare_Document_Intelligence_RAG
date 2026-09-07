# RAG Architecture

## Objective

Build a healthcare document intelligence system that retrieves relevant source evidence before generating an answer.

## Core Pipeline

1. Document ingestion
2. Text extraction
3. Text cleaning
4. Structure-aware chunking
5. Metadata enrichment
6. Embedding generation
7. Vector indexing
8. Query processing
9. Semantic retrieval
10. Metadata filtering
11. Reranking
12. Evidence selection
13. Grounded answer generation
14. Citation
15. Human review

## Architecture

```text
Healthcare Documents
        ↓
Document Ingestion
        ↓
Text Extraction
        ↓
Cleaning / Normalisation
        ↓
Chunking
        ↓
Metadata
        ↓
Embeddings
        ↓
Vector Index
        ↓
User Query
        ↓
Retrieval
        ↓
Metadata Filtering
        ↓
Reranking
        ↓
Evidence Selection
        ↓
LLM
        ↓
Grounded Answer
        ↓
Citations
        ↓
Human Review
