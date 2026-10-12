\# Week 23 Day 2 — Evidence-to-Answer Context



\## Purpose



The Answer Context is the deterministic bridge between the governed Evidence Packet and future grounded answer generation.



It prepares a minimal, approved and traceable context package for the language model.



The Answer Context does not:



\- retrieve evidence

\- decide evidence sufficiency

\- decide governance

\- override provenance

\- override lifecycle controls

\- override evidence precedence

\- generate final answer text



Its role is to package only the information that the generator is permitted to use.



\---



\## Governing Principle



> Give the model only what it needs, while preserving every field required for traceability and safety.



The generator should not receive unnecessary retrieval noise.



The generator should not be expected to infer which evidence is approved.



The generator should not decide whether evidence may be combined.



Those decisions must already have been made upstream.



\---



\# Inputs



The Answer Context receives:



1\. Question-level Evidence Packet

2\. Answer Contract



The Evidence Packet remains the source of truth for:



\- question

\- evidence

\- evidence sufficiency

\- provenance

\- lifecycle

\- precedence

\- governance

\- audit information



The Answer Contract remains the source of truth for:



\- response type

\- allowed response sections

\- whether answer generation is permitted

\- whether human review is required

\- whether citations must be preserved



\---



\# Output



The Answer Context should return a structured object.



Suggested top-level fields:



\- context\_version

\- packet\_id

\- question

\- governance\_decision

\- response\_type

\- allowed\_sections

\- generation\_permitted

\- requires\_human\_review

\- evidence\_context

\- citation\_index

\- uncertainty\_context

\- safety\_constraints



\---



\# Evidence Context



The model should receive only approved evidence needed for the response.



Each evidence item should preserve:



\- evidence\_id

\- document\_id

\- chunk\_id

\- title

\- document\_type

\- source\_file

\- version

\- status

\- page

\- evidence\_text

\- evidence\_role



Optional retrieval scores may be retained for audit but should not be necessary for normal answer wording.



The evidence context should not introduce new facts.



\---



\# Citation Index



A citation index should give the generator a stable mapping between evidence and source metadata.



Example:



```text

E1

→ evidence\_id

→ DOC-004

→ page 2

→ chunk DOC-004-V1.0-P002-C001
