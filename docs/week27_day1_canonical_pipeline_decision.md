\# Week 27 Day 1 — Canonical End-to-End Pipeline Decision



\## Theme



End-to-End RAG Polish



\## Purpose



Week 27 moves the Healthcare Document Intelligence RAG project from a

collection of mature subsystems toward one coherent application path.



The objective is not to create another RAG architecture.



The objective is to compose the existing retrieval, evidence,

governance, generation and assurance layers into one canonical

end-to-end workflow.



\---



\# 1. Starting Position



The repository already contains mature modules for:



\- ingestion

\- preprocessing

\- storage

\- retrieval

\- evidence construction

\- governance

\- controlled generation

\- citation assurance

\- adversarial assurance

\- system safety

\- fail-closed robustness

\- evaluation



Weeks 25 and 26 are treated as protected assurance subsystems.



Week 27 must integrate them rather than replace them.



\---



\# 2. Canonical Retrieval Controller



The authoritative retrieval controller is:



`src/retrieval/retrieval\_orchestrator.py`



Its responsibilities are:



1\. query scope assessment

2\. initial hybrid retrieval

3\. evidence sufficiency assessment

4\. deterministic retrieval routing

5\. at most one bounded enhancement route

6\. final evidence reassessment against the original question



Supported enhancement routes include:



\- relationship-aware retrieval

\- bounded agentic retrieval

\- hybrid evidence rescue



Retrieval does not approve an answer.



Retrieval does not bypass downstream governance.



This separation must remain intact.



\---



\# 3. Retrieval-to-Evidence Boundary



The canonical bridge from retrieval output into structured evidence is:



`src/evidence/evidence\_from\_retrieval.py`



Its responsibility is to:



\- consume retrieval output

\- preserve retrieval-route provenance

\- require final evidence sufficiency

\- construct structured evidence objects



It does not make new retrieval decisions.



It does not modify governance.



\---



\# 4. Canonical Evidence Packet



The authoritative question-level evidence container is:



`src/evidence/evidence\_packet.py`



The packet assembles:



\- question identity

\- retrieval metadata

\- evidence sufficiency

\- structured evidence

\- provenance

\- lifecycle information

\- precedence assessment

\- missing evidence

\- governance

\- audit information



The Evidence Packet does not itself grant permission to answer.



\---



\# 5. Governance Boundary



Governance remains separate from retrieval and generation.



Important governance modules include:



\- `src/governance/review\_decision.py`

\- `src/evidence/evidence\_precedence.py`

\- `src/governance/citation\_verification.py`

\- `src/governance/high\_risk\_claim\_guard.py`



The principal governance states remain:



\- `AUTO\_ANSWER`

\- `REVIEW\_REQUIRED`

\- `ABSTAIN`



Risk or uncertainty may reduce authority.



It must not increase authority.



\---



\# 6. Canonical Generation Path



The Week 27 canonical generation path will use the Week 24 controlled

generation architecture.



Primary modules:



\- `src/generation/answer\_context.py`

\- `src/generation/controlled\_model\_generation.py`

\- `src/generation/governed\_prompt.py`

\- `src/generation/model\_execution.py`

\- `src/generation/generation\_fallback.py`



The language model is treated as an untrusted generation component.



The model receives only governed input.



Model output must pass validation before entering the final workflow.



Provider failure, parsing failure or validation failure must not silently

become an authoritative answer.



\---



\# 7. Legacy / Demonstration Generation Paths



The repository also contains:



\- `src/generation/demo\_pipeline.py`

\- `src/generation/answer\_generator.py`



These files remain useful for:



\- historical continuity

\- focused unit testing

\- demonstrations

\- backwards compatibility



They are not selected as the Week 27 canonical application runtime.



`demo\_pipeline.py` uses deterministic hand-built evidence rather than

the complete governed retrieval stack.



`answer\_generator.py` represents an earlier simplified generation path.



Week 27 will therefore compose the later controlled-generation

architecture instead of building the application around these older

paths.



No legacy files should be deleted during Day 1.



\---



\# 8. Assurance Subsystem



Weeks 25 and 26 provide the protected assurance subsystem.



It includes:



\- claim-citation linking

\- citation verification

\- citation completeness

\- multi-source verification

\- groundedness auditing

\- semantic precision

\- version and temporal assurance

\- prompt-injection assurance

\- abstention safety

\- cross-layer system safety

\- fail-closed robustness

\- operational assurance evaluation



Week 27 should expose these controls through the end-to-end application

path without rewriting their validated internal behaviour.



\---



\# 9. Canonical Week 27 Runtime



The intended runtime architecture is:



Question

\-> Query Scope Gate

\-> Retrieval Orchestrator

\-> Evidence Sufficiency

\-> Structured Evidence

\-> Evidence Packet

\-> Provenance

\-> Precedence

\-> Pre-Generation Governance

\-> Answer Context

\-> Controlled Model Input

\-> Governed Prompt

\-> Provider-Neutral Model Execution

\-> Model Output Validation

\-> Deterministic Fallback if required

\-> Claim / Citation Assurance

\-> Faithfulness and Safety Assurance

\-> Post-Generation Governance

\-> Final Response



The permitted final operational outcomes are:



\- ANSWER

\- REVIEW\_REQUIRED

\- ABSTAIN



\---



\# 10. Week 27 Application Layer



Week 27 may introduce a thin application/orchestration layer.



Its purpose will be composition, not duplication.



The application layer should:



\- call existing modules

\- preserve existing contracts

\- expose one canonical execution path

\- produce one structured result

\- produce one structured audit trace

\- fail closed when integration fails



It should not:



\- reimplement retrieval

\- reimplement evidence construction

\- create a second governance framework

\- create another generation validator

\- replace Week 25/26 assurance

\- embed business logic that belongs in existing modules



\---



\# 11. Architectural Rule



The Week 27 rule is:



> Compose mature components; do not duplicate them.



\---



\# 12. Economic Design Principle



The system is intended to reduce expensive human document-search and

reconciliation work while retaining human judgement for ambiguous or

high-risk cases.



The value proposition is therefore not:



AI replaces healthcare staff.



It is:



AI reduces low-value evidence-search work while governance preserves

human control over uncertain decisions.



\---



\# 13. Day 1 Decision



The Week 27 canonical architecture is approved as:



Retrieval Orchestrator

\-> Evidence Packet

\-> Governance

\-> Controlled Generation

\-> Assurance

\-> Final Governance



A new application layer may now be created to compose these existing

subsystems.



The existing mature components remain authoritative within their own

responsibility boundaries.

