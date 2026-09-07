# Technology Decisions

## Initial Principles

The project will prioritise:

- transparent architecture
- reproducible retrieval
- evidence traceability
- simple components before unnecessary frameworks
- evaluation before optimisation
- healthcare governance
- human review

## Planned Technology Areas

### Python

Used for:

- ingestion
- preprocessing
- chunking
- retrieval
- evaluation

### Document Parsing

Used to extract machine-readable text and document structure.

The exact parser will be selected after testing against the project document corpus.

### Embeddings

Used to create numerical representations of document chunks and queries for semantic retrieval.

### Vector Index

Used to store and search chunk embeddings.

The first implementation should remain simple enough to inspect and debug.

### Retrieval

Initial retrieval will focus on semantic similarity.

Later iterations may include:

- metadata filtering
- keyword retrieval
- hybrid retrieval
- reranking

### LLM

The language model will generate answers only after relevant evidence has been retrieved.

### Evaluation

Retrieval and answer generation will be evaluated separately.

## Framework Policy

Frameworks such as LangChain or LlamaIndex may be introduced when they provide clear engineering value.

The project will avoid hiding core RAG concepts behind frameworks before the underlying retrieval pipeline is understood.
