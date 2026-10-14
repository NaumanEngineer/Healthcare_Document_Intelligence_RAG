\# Week 23 Evaluation — Grounded Communication v2



\## Executive Summary



Week 23 extended the governed healthcare evidence workflow into a complete grounded communication layer.



The system now converts retrieved and governed evidence into manager-facing outputs while preserving:



\- evidence sufficiency controls

\- governance authority

\- answer permissions

\- claim-level citation traceability

\- human review

\- abstention

\- document lifecycle controls



The frozen 75-case benchmark passed with:



\- 14 AUTO\_ANSWER cases

\- 33 REVIEW\_REQUIRED cases

\- 28 ABSTAIN cases

\- 141 supported claims

\- 0 unsupported claims

\- 141 citations used

\- 0 governance overrides

\- 0 expected-abstention auto-answers

\- 0 review cases presented as authoritative

\- 0 abstention evidence leaks

\- 0 unknown citations

\- 0 lifecycle-unsafe automated citations

\- 0 unsafe cases overall



Overall result:



\*\*SAFETY: PASS\*\*



\---



\# Week 23 Objective



The purpose of Week 23 was to move from trusted evidence handling to trusted communication.



The challenge was not simply to generate text.



The challenge was to ensure that downstream communication could never increase authority beyond what the evidence and governance layers permitted.



The resulting architecture is:



Retrieval

→ Evidence Packet

→ Answer Contract

→ Answer Context

→ Grounded Response

→ Claim-to-Citation Linking

→ Review / Abstention UX



\---



\# Day 1 — Governed Answer Contract



Week 23 began by introducing an explicit Answer Contract.



The contract translates governance into communication permission.



Three response states are supported:



\- AUTO\_ANSWER → ANSWER

\- REVIEW\_REQUIRED → REVIEW

\- ABSTAIN → ABSTENTION



The Answer Contract prevents the generation layer from deciding its own authority.



This separates:



\- what evidence exists

\- what governance permits

\- what the communication layer may say



Integration checks showed:



\- Q003 → AUTO\_ANSWER

\- Q027 → REVIEW\_REQUIRED

\- Q029 → ABSTAIN



Full regression after Day 1:



621 tests passed.



\---



\# Day 2 — Evidence-to-Answer Context



Day 2 introduced a structured Answer Context.



The Answer Context provides the generation layer with only the information it is permitted to use.



It includes:



\- packet identity

\- question

\- governance decision

\- response type

\- allowed sections

\- generation permission

\- human-review requirement

\- precedence decision

\- evidence context

\- citation index

\- uncertainty context

\- safety constraints



Stable citation identifiers such as E1, E2 and E3 are generated here.



For ABSTAIN cases:



\- substantive evidence is removed

\- citations are removed

\- generation permission remains false



Real pipeline checks confirmed:



Q003:

\- ANSWER

\- generation permitted

\- 3 evidence items

\- 3 citations



Q027:

\- REVIEW

\- generation not permitted as an authoritative answer

\- human review required

\- 3 evidence items

\- 3 citations



Q029:

\- ABSTENTION

\- 0 evidence items

\- 0 citations



Full regression after Day 2:



633 tests passed.



\---



\# Day 3 — Grounded Response Generation



Day 3 introduced deterministic grounded response generation.



The implementation deliberately used deterministic generation first rather than a live LLM.



This created a controlled baseline before later model-assisted generation.



Three generation statuses are supported:



\- GENERATED

\- REVIEW\_SUMMARY

\- ABSTAINED



AUTO\_ANSWER outputs include:



\- management summary

\- evidence-based explanation

\- operational implication

\- caveats

\- sources



REVIEW\_REQUIRED outputs include:



\- evidence summary

\- why human review is required

\- review focus

\- evidence gaps or uncertainty

\- sources



ABSTAIN outputs include:



\- unable to answer safely

\- reason

\- missing evidence

\- what is needed to continue



Q003 produced GENERATED.



Q027 produced REVIEW\_SUMMARY.



Q029 produced ABSTAINED.



Full regression after Day 3:



649 tests passed.



\---



\# Day 4 — Claim-to-Citation Linking



Day 4 added claim-level traceability.



Claims are classified as:



\- SUPPORTED

\- NON\_SUBSTANTIVE

\- UNSUPPORTED



Supported substantive claims must map to valid citations from the Answer Context.



The linker also validates:



\- packet identity

\- governance identity

\- response type

\- citation IDs

\- blank citations

\- duplicate citations

\- unknown citations



Real examples:



Q003:

\- 5 claims

\- 3 supported

\- 2 non-substantive

\- 0 unsupported



Q027:

\- 4 claims

\- 3 supported

\- 1 non-substantive

\- 0 unsupported



Q029:

\- 3 claims

\- 0 supported

\- 3 non-substantive

\- 0 unsupported



Hardening tests confirmed fail-closed behaviour for:



\- unknown citations

\- response-level unknown citations

\- blank claims

\- blank citations

\- duplicate citations



Full regression after Day 4:



669 tests passed.



\---



\# Day 5 — Review and Abstention UX



Day 5 focused on safe blocked-state communication.



The design principle was:



\*\*When automation stops, useful decision support should continue.\*\*



REVIEW\_REQUIRED cases now provide a manager-facing view containing:



\- clear review status

\- evidence summary

\- reason human review is required

\- review focus

\- uncertainty

\- sources

\- next action



ABSTAIN cases provide:



\- unable-to-answer status

\- reason no safe answer is available

\- missing information

\- what would allow progress

\- safe next action



The design prevents:



\- hidden answers inside abstentions

\- evidence leakage

\- unsupported speculation

\- silent removal of human review

\- automatic decision substitution



Real pipeline checks confirmed:



Q027:

\- HUMAN\_REVIEW\_REQUIRED

\- evidence remains visible

\- sources remain visible

\- manager review remains mandatory



Q029:

\- UNABLE\_TO\_ANSWER\_SAFELY

\- missing cybersecurity evidence identified

\- no evidence leaked

\- no citations exposed

\- safe next action provided



Full regression after Day 5:



690 tests passed.



\---



\# Day 6 — End-to-End Communication Benchmark



The full Week 23 stack was evaluated across the frozen 75-case benchmark.



\## Governance Distribution



\- REVIEW\_REQUIRED: 33

\- AUTO\_ANSWER: 14

\- ABSTAIN: 28



\## Response Types



\- REVIEW: 33

\- ANSWER: 14

\- ABSTENTION: 28



\## Generation Statuses



\- REVIEW\_SUMMARY: 33

\- GENERATED: 14

\- ABSTAINED: 28



\## Claim Metrics



\- Supported claims: 141

\- Non-substantive claims: 145

\- Unsupported claims: 0



\## Citation Metrics



\- Total citations used: 141

\- Average citations per AUTO\_ANSWER: 3.0



\## Quality Metrics



\- Average supported claims per AUTO\_ANSWER: 3.0

\- Review UX cases: 33

\- Abstention UX cases: 28



\---



\# Safety Outcomes



The benchmark explicitly tested whether downstream communication weakened upstream assurance.



Results:



\- governance overrides: 0

\- expected-abstention auto-answers: 0

\- review cases presented as authoritative: 0

\- abstention evidence leakage: 0

\- unsupported material claims: 0

\- unknown citations: 0

\- lifecycle-unsafe automated citations: 0



Unsafe cases:



0



Overall safety result:



\*\*PASS\*\*



\---



\# Why This Matters



A healthcare AI system should not be judged only by whether it produces fluent answers.



For operational use, it must also demonstrate:



\- evidence grounding

\- provenance

\- document lifecycle awareness

\- contradiction handling

\- governance

\- human-review preservation

\- safe abstention

\- traceable claims

\- controlled authority



Week 23 proves that the project now contains all of these elements in one end-to-end communication workflow.



\---



\# Current System Maturity



The project has now progressed through three major stages.



\## Week 21 — Smart Retrieval



The system learned how to retrieve, rescue and route evidence more effectively.



\## Week 22 — Trusted Evidence



The system learned how to structure, verify, combine and govern retrieved evidence.



\## Week 23 — Trusted Communication



The system learned how to communicate that evidence without weakening governance.



This progression can be summarised as:



Smart Retrieval

→ Trusted Evidence

→ Trusted Communication



\---



\# Important Limitation



The current grounded-generation layer is deterministic.



This is intentional.



It creates a controlled safety baseline before introducing live LLM generation.



Therefore:



\- unsupported-claim performance currently applies to the deterministic communication layer

\- it should not yet be presented as proof that an unrestricted LLM will always generate zero unsupported claims

\- future model-assisted generation must be evaluated against the same safety benchmark



\---



\# Economic Evaluation Status



No direct cost-saving claim has yet been measured.



Potential future operational metrics include:



\- policy-search time

\- management briefing preparation time

\- manual evidence checks avoided

\- manager review time

\- number of source-document lookups avoided

\- inference cost per query

\- review rate



These remain prospective until measured in a real or simulated workflow study.



\---



\# Portfolio Positioning



This project should not be presented simply as:



"RAG chatbot for healthcare documents."



A more accurate description is:



\*\*Governed Healthcare Evidence and Operational Intelligence System\*\*



It combines:



\- hybrid retrieval

\- bounded agentic rescue

\- evidence sufficiency

\- structured evidence extraction

\- provenance

\- contradiction and precedence handling

\- governance

\- grounded answer permissions

\- claim-level citation linking

\- human review

\- safe abstention



This makes the project relevant to:



\- NHS information and analytics

\- healthcare AI engineering

\- clinical and operational governance

\- regulated AI

\- decision-support systems

\- health-tech platform engineering



\---



\# Week 23 Conclusion



Week 23 successfully converted the evidence-assurance architecture into a governed communication system.



The frozen 75-case benchmark completed with:



\- 141 supported claims

\- 0 unsupported claims

\- 141 citations

\- 0 governance overrides

\- 0 unsafe cases



The communication layer therefore preserved the assurance layer across the evaluated benchmark.



\*\*Week 23 status: COMPLETE\*\*
