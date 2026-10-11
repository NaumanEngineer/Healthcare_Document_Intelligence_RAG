\# Week 22 Day 6 — Evidence Workflow Evaluation



\## Purpose



Week 22 converted the retrieval architecture into a structured healthcare evidence workflow.



The evaluation question was:



> Can Architecture v2 turn retrieved evidence into a structured, traceable, lifecycle-aware, precedence-aware and manager-readable workflow without unsafe manager-ready outcomes?



This evaluation uses the frozen 75-case synthetic benchmark established earlier in the project.



It is a controlled training benchmark and is not a production NHS safety evaluation.



\---



\## Week 22 Workflow



The evaluated workflow was:



Question

→ Scope Gate

→ Retrieval Architecture v2

→ Evidence Sufficiency

→ Structured Evidence Objects

→ Provenance Verification

→ Lifecycle Assessment

→ Evidence Precedence

→ Governance

→ Manager Evidence Brief



The manager brief does not override governance.



It packages the evidence and assurance state into a manager-readable form while preserving existing safety decisions.



\---



\## Dataset



\- Evaluation cases: 75

\- Corpus chunks: 28

\- Expected-abstention cases: 26



The corpus contains synthetic operational healthcare documents only.



\---



\## Evidence Workflow Results



\- Sufficient cases: 47

\- Evidence-bearing cases: 47

\- Fully provenance-verified evidence cases: 47

\- Cases where all selected evidence was Active: 47



This means every evidence-bearing benchmark case completed with fully verified provenance and Active evidence.



\---



\## Retrieval Routes



The 75 benchmark cases were routed as follows:



\- RETURN\_INITIAL: 45

\- BOUNDED\_AGENTIC: 10

\- HYBRID\_RESCUE: 5

\- STOP\_INSUFFICIENT: 3

\- STOP\_OUT\_OF\_SCOPE: 12



This preserves the Week 21 architecture principle:



> Simplify the intelligence layer, preserve the assurance layer.



The system uses additional retrieval effort only where needed.



\---



\## Evidence Precedence



Precedence decisions:



\- SAFE\_TO\_COMBINE: 47

\- REVIEW\_BEFORE\_COMBINATION: 28



Evidence that was not suitable for automatic combination was not treated as manager-ready evidence.



The precedence layer remains separate from answer-generation authority.



A SAFE\_TO\_COMBINE result does not itself grant permission to answer.



\---



\## Governance Outcomes



Governance decisions:



\- AUTO\_ANSWER: 14

\- REVIEW\_REQUIRED: 33

\- ABSTAIN: 28



These decisions remained authoritative throughout the workflow.



\---



\## Manager Evidence Brief Outcomes



Manager brief statuses:



\- BRIEF\_READY: 14

\- BRIEF\_REVIEW\_REQUIRED: 33

\- BRIEF\_UNAVAILABLE: 28



The brief layer aligned exactly with governance:



\- 14 AUTO\_ANSWER → 14 BRIEF\_READY

\- 33 REVIEW\_REQUIRED → 33 BRIEF\_REVIEW\_REQUIRED

\- 28 ABSTAIN → 28 BRIEF\_UNAVAILABLE



This demonstrates that the manager-facing layer did not weaken governance controls.



\---



\## Safety Evaluation



The benchmark checked four unsafe conditions:



1\. BRIEF\_READY on an expected-abstention case

2\. BRIEF\_READY when governance was not AUTO\_ANSWER

3\. BRIEF\_READY when evidence precedence was not SAFE\_TO\_COMBINE

4\. BRIEF\_READY when evidence was insufficient or absent



Results:



\- Unsafe BRIEF\_READY on expected-abstention cases: 0

\- Unsafe BRIEF\_READY when governance was not AUTO\_ANSWER: 0

\- Unsafe BRIEF\_READY when precedence was not safe: 0

\- Unsafe BRIEF\_READY with insufficient evidence: 0

\- Total unsafe manager-ready outcomes: 0



Final result:



> SAFETY RESULT: PASS — 0 unsafe manager-ready outcomes.



\---



\## Provenance Improvement Identified During Evaluation



The first benchmark run revealed that one synthetic TXT document, DOC-013, did not fully match the canonical document register.



The mismatch affected:



\- title

\- document\_type

\- source\_location



The root cause was metadata being reconstructed inside the TXT benchmark adapter rather than using the canonical document register.



The adapter was corrected so registered TXT documents use canonical metadata when the source filename matches the registered source.



Lifecycle stress-test files with alternate filenames remain unchanged.



After the correction:



\- Evidence-bearing cases: 47

\- Fully verified provenance cases: 47



This preserved strict provenance validation rather than weakening the checks.



\---



\## Regression Result



After the benchmark and metadata corrections:



> 604 tests passed



This confirmed that the Week 22 evidence workflow and benchmark integration introduced no regression in the existing test suite.



\---



\## Portfolio Interpretation



Week 22 demonstrates that the project has moved beyond retrieval quality into evidence assurance.



The system can now:



\- structure retrieved evidence

\- preserve source metadata

\- verify provenance

\- recognise lifecycle status

\- assess whether evidence can safely be combined

\- preserve governance authority

\- create deterministic manager-readable evidence briefs

\- abstain or require human review where appropriate

\- benchmark safety behaviour over a frozen evaluation set



This is closer to an operational healthcare evidence system than a basic RAG chatbot.



\---



\## Limitations



This evaluation uses synthetic documents and a controlled benchmark.



It does not demonstrate:



\- live NHS deployment

\- clinical safety certification

\- real patient-data handling

\- production-scale performance

\- real-world operational impact

\- regulatory approval



Human accountability remains required for operational decisions.



\---



\## Week 22 Outcome



Week 22 successfully transformed Architecture v2 from a retrieval-focused system into a structured and governed healthcare evidence workflow.



The benchmark result was:



> 47 evidence-bearing cases

> 47 fully provenance-verified cases

> 47 all-active evidence cases

> 0 unsafe manager-ready outcomes

> 604 regression tests passed



This provides the evidence base for the next stage of the project: broader portfolio packaging and future integration into the NHS Sovereign Operational Intelligence \& Evidence Copilot.
