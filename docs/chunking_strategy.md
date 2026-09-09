# Chunking Strategy

## Objective

Transform cleaned healthcare document text into retrieval-ready chunks while preserving meaning, provenance and document structure.

## Design Principle

Chunking is treated as an evidence-design problem rather than simple text splitting.

The objective is to create chunks that are small enough for precise retrieval but large enough to preserve operational meaning.

## Initial Strategy

The first implementation uses structure-aware recursive chunking.

The pipeline will:

1. preserve document boundaries
2. preserve page-level provenance
3. prefer paragraph boundaries
4. split oversized paragraphs when necessary
5. apply controlled overlap
6. reject empty chunks
7. preserve metadata on every chunk

## Initial Chunk Size

Prototype target:

- approximately 800–1200 characters per chunk
- approximately 100–200 characters of overlap

These values are starting points and will later be evaluated against retrieval quality.

## Why Not Fixed-Length Only?

Blind fixed-length chunking can split:

- escalation conditions
- policy responsibilities
- procedural steps
- exceptions
- numbered instructions

This can reduce retrieval quality and create incomplete evidence.

## Healthcare Considerations

Healthcare operational documents often contain:

- escalation thresholds
- responsible roles
- exceptions
- procedural sequences
- governance requirements

The chunking pipeline should preserve these relationships where possible.

## Chunk Grain

A chunk should ideally represent a meaningful evidence unit such as:

- a policy subsection
- an escalation rule
- a procedural step
- a governance responsibility

## Provenance

Every chunk must remain traceable to:

- document ID
- source file
- page number
- chunk number
- document version
- document status

## Initial Limitations

The first implementation will not yet perform:

- semantic chunking using embeddings
- LLM-based chunk boundary detection
- cross-document chunking
- retrieval optimisation
- vector indexing


## Overlap Behaviour

Overlap is word-aligned rather than character-aligned.

The overlap size is treated as a maximum character budget, and the start position is moved forward to a word boundary where possible.

This prevents broken words from appearing at chunk boundaries.

The current prototype does not guarantee sentence-aligned overlap. Sentence fragments may still occur, which is accepted as a documented limitation to keep the implementation simple and transparent.

