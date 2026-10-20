\# Week 27 Day 2 — Unified Orchestrator Build Plan



\## Theme



End-to-End RAG Polish



\## Purpose



Day 2 introduces the thin application layer that composes the mature

retrieval, evidence, governance, generation and assurance subsystems.



The application layer must not become a second implementation of the

Healthcare Document Intelligence RAG architecture.



Its role is orchestration.



\---



\## 1. Canonical Runtime Objective



The final runtime should expose one application-level execution path:



Question

\-> Input Validation

\-> Governed Retrieval

\-> Evidence Packet

\-> Pre-Generation Governance

\-> Evidence Safety

\-> Answer Contract

\-> Answer Context

\-> Controlled Generation

\-> Deterministic Fallback

\-> Post-Generation Assurance

\-> Final Governance

\-> Final Response



\---



\## 2. New Application Package



Week 27 introduces:



`src/application/`



This package exists only for application-level composition.



It must not contain duplicated retrieval, evidence, generation or

assurance algorithms.



\---



\## 3. Planned Canonical Orchestrator



The principal future file is:



`src/application/rag\_pipeline.py`



Its intended public function is:



`run\_rag\_pipeline(...)`



The function will execute one governed request and return one structured

application result.



\---



\## 4. Existing Components to Reuse



The orchestrator should reuse existing aggregate functions wherever possible.



Primary runtime components include:



\- `orchestrate\_retrieval()`

\- canonical evidence `build\_evidence\_packet()`

\- `build\_answer\_contract()`

\- `build\_answer\_context()`

\- `build\_grounded\_response()`

\- `execute\_governed\_model()`

\- `resolve\_generation\_with\_fallback()`

\- existing request-level assurance functions

\- `decide\_post\_generation\_outcome()`

\- system-safety invariant controls

\- fail-closed assurance controls



The orchestrator must not reproduce their internal logic.



\---



\## 5. Thin Integration Responsibilities



The application layer may add only the integration behaviour needed to join

the existing components safely.



This includes:



\- validating the application request and dependencies

\- assigning a request identifier

\- sequencing the existing modules

\- recording execution stages

\- propagating authority reductions

\- selecting the actual response to be assured

\- adapting selected response claims into existing assurance contracts

\- mapping detector outputs into final restrictions

\- producing one final application result

\- failing closed on unexpected integration failure



\---



\## 6. Protected Authority Rule



The application layer must preserve:



AUTO\_ANSWER

REVIEW\_REQUIRED

ABSTAIN



At the assurance boundary:



AUTO\_ANSWER -> PASS

REVIEW\_REQUIRED -> REVIEW\_REQUIRED

ABSTAIN -> ABSTAIN



Assurance may preserve or reduce authority.



Assurance must never increase authority.



\---



\## 7. Provider Boundary



Provider execution must remain explicit.



The application may eventually support:



\- provider mode

\- deterministic-only mode



Provider failure must not become an automatic answer.



The orchestrator must never expose raw provider output as the final

application response without existing validation.



\---



\## 8. Response Selection Rule



Only one response may become the selected response for downstream assurance.



It may be:



\- validated model output

\- deterministic fallback

\- deterministic-only response



The exact selected response must be the response that is assured.



The application must never assure one response and return another.



\---



\## 9. Evidence-Safety Boundary



Safety checks that concern source evidence should occur before unsafe evidence

is exposed to a model provider when applicable.



This includes relevant checks such as:



\- prompt-injection risk

\- lifecycle restrictions

\- temporal restrictions

\- blocked evidence combinations



The application should reuse existing detector outputs rather than rerunning

equivalent checks unnecessarily.



\---



\## 10. Assurance Boundary



Week 25 and Week 26 benchmark runners remain outside the per-request runtime.



The application should call only reusable request-level functions.



Expected benchmark labels must never become runtime truth.



The application must explicitly record:



\- executed checks

\- not-applicable checks

\- skipped checks with reason

\- failed checks



NOT\_APPLICABLE is not PASS.



\---



\## 11. Fail-Closed Integration Boundary



Unexpected application integration failure must return a controlled result

with:



\- status `FAILED\_CLOSED`

\- final outcome `ABSTAIN`

\- failure stage

\- error type

\- safe reason



The application must not silently recover to ANSWER.



\---



\## 12. Day 2 Build Sequence



Day 2 implementation will proceed in small stages.



\### Session 1

Create the application package and freeze the orchestrator build plan.



\### Session 2

Create application request/result contracts and request identity.



\### Session 3

Create the first retrieval-to-evidence orchestration path.



\### Session 4

Add pre-generation governance, answer contract and answer context.



\### Session 5

Add deterministic response and controlled provider execution.



\### Session 6

Add the first request-level assurance/final-governance boundary and tests.



The system will be kept executable and regression-safe after each session.



\---



\## 13. Day 2 Non-Goals



Day 2 will not:



\- redesign retrieval

\- redesign evidence

\- rewrite Week 25 assurance

\- rewrite Week 26 assurance

\- delete legacy generation paths

\- build FastAPI

\- build a UI

\- introduce agent autonomy

\- change benchmark truth

\- change mature thresholds without evidence



\---



\## 14. Day 2 Success Condition



By the end of Day 2, the repository should contain the first working thin

application path joining the mature architecture.



The target is not feature count.



The target is:



> one coherent, testable, governed execution path.

