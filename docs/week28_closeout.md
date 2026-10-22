\# Week 28 Closeout — End-to-End Governed RAG Polish



\## Healthcare Document Intelligence RAG



\### Status



\*\*Week 28: COMPLETE\*\*



Week 28 completed the end-to-end RAG polish phase by converting the existing retrieval, evidence, generation and assurance components into a portfolio-ready governed application.



The system is no longer presented simply as a retrieval or answer-generation prototype.



It is now demonstrated as a governed operational information application capable of deciding whether available evidence permits:



\- ANSWER

\- REVIEW\_REQUIRED

\- ABSTAIN



The central design principle remains:



> The model is optional. The assurance path is not.



\---



\# Week 28 Objectives



Week 28 focused on five final engineering and portfolio objectives:



1\. validate the complete governed application path

2\. demonstrate natural three-outcome behaviour

3\. convert internal governance decisions into manager-facing responses

4\. prove clean-start reproducibility

5\. package the project for recruiters, NHS managers and technical interviewers



These objectives were completed without weakening the governance controls developed during earlier weeks.



\---



\# Day 1 — End-to-End Polish Audit



The existing RAG architecture was reviewed as a complete application rather than as isolated components.



The audit checked:



\- retrieval

\- evidence sufficiency

\- structured Evidence Objects

\- Evidence Packets

\- provenance

\- lifecycle status

\- supersession

\- precedence

\- pre-generation governance

\- Answer Contracts

\- controlled generation

\- deterministic fallback

\- citation assurance

\- groundedness

\- hallucination resistance

\- post-generation governance

\- observability

\- runtime configuration

\- CLI execution

\- portfolio usability



No critical architectural gap requiring redesign was identified.



The remaining work was therefore treated as application polish, reproducibility and portfolio presentation rather than another architecture rebuild.



\---



\# Day 2 — Three-Outcome Governed Demonstration



A deterministic portfolio demonstration was created to prove the three principal user-facing outcomes.



\## ANSWER



Example:



> What factors should be reviewed during operational pressure?



The available approved evidence was sufficient for the application to release a governed answer.



\## REVIEW\_REQUIRED



Example:



> How should workforce and bed capacity pressures be considered together?



Relevant evidence existed, but governance controls prevented the system from releasing an authoritative answer without human review.



\## ABSTAIN



Example:



> What operational guidance applies to temporary overnight visitor parking?



The approved evidence base was insufficient, so the system refused to provide an unsupported answer.



Final demonstration verification:



\- Cases: 3

\- Governance matched: 3

\- Presentation matched: 3

\- Authority preserved: 3

\- Overall verification: PASS



This demonstrated that refusing or escalating an answer is an intentional product capability rather than an application failure.



\---



\# Day 3 — Manager-Facing Governed Responses



The internal governance output was converted into a manager-facing response layer.



The response contract exposes fields including:



\- outcome

\- headline

\- summary

\- answer

\- evidence basis

\- confidence message

\- next action

\- human review requirement

\- citations

\- limitations



The presentation layer is intentionally unable to increase authority.



Therefore:



\### ANSWER



A supported answer and its approved citations may be released.



\### REVIEW\_REQUIRED



The underlying generation candidate is not released as an authoritative answer.



Human review remains mandatory.



\### ABSTAIN



No substantive answer is released.



Unsupported citations are not displayed.



This ensures that user-friendly presentation cannot bypass upstream governance.



\---



\# Day 4 — Clean-Start Reproducibility



The repository was reconstructed and validated in a clean Python environment.



The clean-start environment used:



\- Python 3.14.1

\- pinned project dependencies

\- dependency auditing

\- deterministic Week 28 demonstration

\- focused Week 28 regression tests

\- complete repository regression testing



The clean-start validation demonstrated that the application can be reproduced from repository artifacts rather than depending on hidden local machine state.



Verified clean-start evidence included:



\- dependency audit: PASS

\- governed Week 28 demo: PASS

\- focused Week 28 tests: 59 passed

\- complete repository regression suite: 1,639 passed



This provides stronger engineering evidence than demonstrating the project only inside the original development environment.



\---



\# Day 5 — Portfolio Presentation



The technical project was converted into a recruiter-, manager- and interview-friendly portfolio package.



Created portfolio documentation includes:



\- `docs/week28\_day5\_portfolio\_evidence.md`

\- `docs/week28\_day5\_portfolio\_architecture.md`

\- `docs/week28\_day5\_interview\_and\_manager\_story.md`

\- `docs/week28\_day5\_portfolio\_index.md`



These documents provide different entry points for:



\- recruiters

\- NHS operational managers

\- technical interviewers

\- AI and data engineering reviewers



The portfolio presentation deliberately separates:



\- demonstrated technical capability

\- illustrative operational value

\- unvalidated future production claims



The project therefore avoids claiming production readiness, validated NHS savings or replacement of professional judgement.



\---



\# Day 6 — Final Validation



The final governed demo was rerun after portfolio packaging.



Results:



\- ANSWER outcome: PASS

\- REVIEW\_REQUIRED outcome: PASS

\- ABSTAIN outcome: PASS

\- Governance matched: 3/3

\- Presentation matched: 3/3

\- Authority preserved: 3/3

\- Overall verification: PASS



The focused Week 28 regression suite was also rerun.



Final result:



\*\*59 passed in 16.09 seconds\*\*



No Week 28 regression was identified.



\---



\# Final Application Architecture



The completed governed application can be represented as:



```text

Operational Question

&#x20;       ↓

Input Validation

&#x20;       ↓

Scope Control

&#x20;       ↓

Governed Retrieval

&#x20;       ↓

Evidence Sufficiency

&#x20;       ↓

Structured Evidence Objects

&#x20;       ↓

Evidence Packet

&#x20;       ↓

Provenance Verification

&#x20;       ↓

Lifecycle / Supersession / Precedence

&#x20;       ↓

Pre-Generation Governance

&#x20;       ↓

Answer Contract

&#x20;       ↓

Controlled Answer Context

&#x20;       ↓

Deterministic Generation

&#x20;       ↓

Optional Provider-Neutral Model Execution

&#x20;       ↓

Generation Validation

&#x20;       ↓

Safe Deterministic Fallback

&#x20;       ↓

Citation and Faithfulness Assurance

&#x20;       ↓

Post-Generation Governance

&#x20;       ↓

Manager-Facing Governed Presentation

&#x20;       ↓

ANSWER / REVIEW\_REQUIRED / ABSTAIN

```



\---



\# What Makes the Project Different



The strongest feature of this project is not that it can generate answers.



Its strongest feature is that the application has been deliberately engineered to determine when an answer should \*\*not\*\* be released.



The application treats:



\- insufficient evidence

\- conflicting evidence

\- provenance problems

\- lifecycle concerns

\- precedence ambiguity

\- citation weakness

\- groundedness problems

\- unsupported generation

\- governance escalation



as first-class application states.



That is fundamentally different from a generic chatbot or basic RAG demonstration.



\---



\# NHS Operational Value Proposition



A potential NHS use case is operational guidance retrieval.



Instead of staff manually searching across multiple policies and deciding which document is current or applicable, the system can:



1\. retrieve relevant approved material

2\. structure the evidence

3\. check provenance and lifecycle status

4\. assess whether the evidence is sufficient

5\. identify conflicts and precedence issues

6\. generate only within governed evidence

7\. verify citations and faithfulness

8\. release an answer, require review, or abstain



The intended operational benefit is reduced avoidable search and reconciliation effort while retaining human oversight.



Any numerical savings estimates associated with this project remain illustrative and have not been validated in an NHS deployment.



\---



\# Portfolio Evidence



A reviewer can inspect:



\## Application



\- `src/application/rag\_pipeline.py`

\- `src/application/app.py`

\- `src/application/week28\_demo\_runner.py`

\- `src/application/manager\_response.py`



\## Generation



\- `src/generation/answer\_contract.py`

\- `src/generation/answer\_context.py`

\- `src/generation/controlled\_model\_generation.py`

\- `src/generation/model\_execution.py`

\- `src/generation/generation\_fallback.py`



\## Assurance



\- `src/application/assurance.py`

\- `src/evaluation/citation\_completeness.py`

\- `src/evaluation/groundedness\_audit.py`

\- `src/evaluation/hallucination\_resistance.py`

\- `src/evaluation/overstatement\_audit.py`



\## Portfolio



\- `README.md`

\- `docs/week28\_day5\_portfolio\_index.md`

\- `docs/week28\_day5\_portfolio\_evidence.md`

\- `docs/week28\_day5\_portfolio\_architecture.md`

\- `docs/week28\_day5\_interview\_and\_manager\_story.md`



\---



\# Limitations



The project currently:



\- uses synthetic or controlled portfolio evidence

\- is not connected to live NHS clinical systems

\- does not process real patient information

\- does not include production identity and access management

\- does not provide a completed NHS clinical safety case

\- does not prove financial savings in an operational NHS deployment

\- does not replace clinical or operational professional judgement

\- is not represented as a production-deployed NHS system



These limitations are intentional and should be stated clearly in interviews and portfolio discussions.



\---



\# Engineering Progression



The project evolved through the following stages:



\*\*Smart Retrieval\*\*



↓



\*\*Trusted Evidence\*\*



↓



\*\*Governed Communication\*\*



↓



\*\*Assured Generation\*\*



↓



\*\*Reproducible Governed RAG Application\*\*



The result is a substantially stronger portfolio artifact than a conventional “chat with documents” RAG project.



\---



\# Interview Positioning



A concise technical description is:



> I built a governed healthcare document intelligence RAG application for NHS-style operational guidance. It combines hybrid retrieval, structured evidence, provenance and lifecycle controls, precedence assessment, controlled generation, citation and faithfulness assurance, adversarial testing, deterministic fallback and explicit ANSWER, REVIEW\_REQUIRED and ABSTAIN outcomes. I then packaged the system as a reproducible end-to-end application and validated the Week 28 path with a clean governed demonstration and regression testing.



The strongest follow-up point is:



> I spent significant effort engineering when the system should not answer, because in healthcare operational environments an unsupported confident answer can be more dangerous than no answer.



\---



\# Week 28 Final Status



\*\*Architecture:\*\* PASS



\*\*Governance:\*\* PASS



\*\*Manager-facing presentation:\*\* PASS



\*\*Three-outcome behaviour:\*\* PASS



\*\*Authority preservation:\*\* PASS



\*\*Clean-start reproducibility:\*\* PASS



\*\*Focused Week 28 regression:\*\* 59 passed



\*\*Complete clean-start repository regression:\*\* 1,639 passed



\*\*Portfolio packaging:\*\* COMPLETE



\*\*Week 28:\*\* COMPLETE



\---



\# Transition to Week 29



Weeks 27–28 completed the \*\*End-to-End RAG Polish\*\* phase.



The next roadmap phase is:



\## Weeks 29–32 — Microsoft Azure AI in Healthcare Specialist Phase



The objective is not to replace the governed architecture already built.



The objective is to learn how this architecture could evolve toward a cloud-hosted healthcare AI platform using appropriate Azure services while preserving:



\- evidence governance

\- human review

\- safe abstention

\- reproducibility

\- observability

\- provider neutrality

\- responsible AI principles



This creates the bridge from a strong local governed AI application toward later production-oriented healthcare AI engineering and AI-102 preparation.

