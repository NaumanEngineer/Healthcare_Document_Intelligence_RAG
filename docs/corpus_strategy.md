# Document Corpus Strategy

## Objective

Define a controlled, traceable and non-sensitive document corpus for the Healthcare Document Intelligence RAG project.

The corpus will provide the evidence base used for retrieval and grounded answer generation.

---

## Initial Corpus Scope

The initial prototype will use:

- synthetic healthcare operational policies
- publicly available non-sensitive healthcare guidance
- synthetic escalation procedures
- synthetic workforce guidance
- synthetic business continuity material
- synthetic governance documentation

The corpus will not contain:

- patient-identifiable information
- staff-identifiable information
- confidential internal operational documents
- individual clinical records
- private organisational data
- documents containing secrets or credentials

---

## Initial Document Categories

The first corpus will include documents representing:

1. Operational Escalation Policy
2. Winter Pressure Plan
3. Workforce Escalation Procedure
4. Bed Capacity Management Procedure
5. Business Continuity Procedure
6. Operational Governance Standard

---

## Corpus Design Principles

The corpus should be:

- controlled
- versioned
- traceable
- non-sensitive
- small enough to inspect manually
- diverse enough to test retrieval quality
- realistic enough to support healthcare operational use cases

---

## Source Categories

Each document should be classified as one of:

- Synthetic
- Public Guidance
- Public Policy
- Public Operational Standard

The source type must be recorded in metadata.

---

## Evidence Boundary

The system should only generate evidence-grounded answers from documents included in the approved corpus.

General language-model knowledge must not be presented as if it came from the controlled document set.

---

## Version Control

Each document should retain:

- document_id
- title
- version
- effective_date
- source_type
- source_location
- document_status

If multiple versions exist, the system should preserve which version produced the retrieved evidence.

---

## Document Status

Documents may later be classified as:

- Active
- Superseded
- Draft
- Archived

The prototype should prefer Active documents where status metadata is available.

---

## Corpus Governance

Documents should only enter the retrieval corpus after basic validation of:

- source
- document type
- sensitivity
- version
- effective date
- readability
- extraction quality

---

## Initial Goal

The first implementation should begin with a deliberately small corpus of approximately 5–10 documents.

This allows retrieval failures to be inspected manually before scaling the system.
