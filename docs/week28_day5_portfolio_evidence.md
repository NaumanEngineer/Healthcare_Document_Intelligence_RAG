# Week 28 Day 5 — Portfolio Evidence



## Healthcare Document Intelligence RAG



### Purpose



Healthcare Document Intelligence RAG is a governed retrieval-augmented

generation system designed for NHS-style operational guidance.



The application is designed to help staff locate relevant approved guidance,

understand the evidence supporting a response, and avoid unsupported

automation when evidence is insufficient, conflicting, superseded or requires

human judgement.



The system is not designed as an unrestricted chatbot.



Its central engineering question is:



> Should the system answer at all?



rather than only:



> Can a language model generate an answer?



---



# Portfolio Summary



The project demonstrates an end-to-end governed RAG architecture covering:



- document ingestion

- metadata and lifecycle controls

- semantic retrieval

- BM25 keyword retrieval

- hybrid retrieval

- evidence sufficiency

- structured Evidence Objects

- question-level Evidence Packets

- provenance verification

- lifecycle assessment

- conflict and precedence handling

- pre-generation governance

- answer contracts

- controlled answer context

- deterministic generation

- optional provider-neutral model execution

- safe deterministic fallback

- citation verification

- citation completeness

- groundedness assurance

- hallucination resistance

- adversarial safety testing

- post-generation governance

- manager-facing governed responses

- structured observability

- runtime configuration

- CLI execution

- dependency auditing

- clean-start reproducibility

- automated regression testing



---



# Governed Outcomes



The application supports three explicit final states.



## ANSWER



An answer may be released when approved evidence is sufficient and all

mandatory governance and assurance conditions permit release.



## REVIEW_REQUIRED



Relevant evidence exists, but human review is required before authoritative

use.



The user-facing layer must not silently convert this state into an answer.



## ABSTAIN



The system cannot safely answer from the available approved evidence.



The application must not invent:



- evidence

- citations

- authority

- confidence

- hidden substantive answers



---



# Portfolio Demonstration



The Week 28 demonstration executes three natural scenarios through the real

application pipeline.



Cases:



- `W28-DEMO-ANSWER-001`

- `W28-DEMO-REVIEW-001`

- `W28-DEMO-ABSTAIN-001`



Validated result:



```text

Cases: 3

Governance matched: 3

Presentation matched: 3

Authority preserved: 3

Overall verification: PASS
