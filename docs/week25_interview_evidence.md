\# Week 25 Interview Evidence — Citation \& Faithfulness Assurance



\## Purpose



Translate the Week 25 engineering work into concise interview evidence for NHS Band 7, Senior Information Analyst, HealthTech AI Engineer, Responsible AI, and healthcare data/AI roles.



\---



\## 1. Two-Minute Technical Interview Answer



\### Question



Tell me about a technically challenging AI project you built.



\### Answer



I built a governance-first Healthcare Document Intelligence RAG system designed for healthcare and NHS-style operational use.



A key challenge was that a generated answer could look convincing and include citations while still being unsafe. For example, the citation might point to the wrong chunk, use superseded evidence, omit a conflicting source, strengthen uncertain wording, or introduce operational advice that was never supported by the source.



I therefore built a separate assurance layer rather than trusting the model output directly.



The assurance flow checks citation correctness, citation completeness, evidence lifecycle, multi-source support, evidence precedence, groundedness, overstatement, hallucination risk, conflict coverage, governance boundaries and abstention safety.



I also created an 18-case adversarial benchmark covering supported, unsupported, conflicting, overstated and abstention scenarios.



The final automated assurance suite achieved 18 out of 18 alignment on citation assurance and 18 out of 18 on faithfulness assurance, while the full repository regression reached 946 passing tests.



The important design principle was that the model can generate content, but the model does not decide whether that content is safe to accept.



\---



\## 2. NHS Manager / Non-Technical Answer



\### Question



What problem does your project solve?



\### Answer



The problem is that an AI system can give a very confident answer even when the evidence behind it is incomplete, outdated or conflicting.



In an NHS environment, that creates risk because staff may assume that a confident answer with a citation is automatically trustworthy.



My project adds an assurance layer before the answer reaches the user.



It checks whether the source really supports the statement, whether important evidence has been omitted, whether documents conflict, whether uncertainty has been changed into certainty, and whether the AI is giving advice that should instead be reviewed by a person.



If the evidence is not strong enough, the system can require human review or refuse to answer.



The objective is not to replace professional judgement. It is to make AI-generated information more traceable, controlled and auditable.



\---



\## 3. Band 7 Governance Answer



\### Question



How did you manage risk in your AI solution?



\### Answer



I treated risk management as part of the architecture rather than as an afterthought.



The system uses explicit governance states such as AUTO\_ANSWER, REVIEW\_REQUIRED and ABSTAIN.



Downstream assurance can reduce authority but cannot increase it.



For example, an answer originally eligible for automatic response can be downgraded to review if citation or groundedness checks fail.



However, content marked for review cannot be promoted to an authoritative answer, and an abstention decision cannot become substantive operational advice.



I also created automated regression tests to ensure those governance boundaries remain enforced as the system evolves.



\---



\## 4. Example of Finding and Fixing a Defect



\### Question



Tell me about a defect you identified during testing.



\### Answer



During benchmark testing I found that the citation verifier could classify a claim as supported based on high lexical overlap before the high-risk claim guard was evaluated.



That created a safety weakness because a statement could reuse much of the evidence wording but still introduce a new mandatory action, actor or operational instruction.



I changed the validation order so identity and lifecycle checks happen first, then support is calculated, then the high-risk guard runs before lexical acceptance and semantic rescue.



I added regression tests around that ordering so the defect cannot silently return later.



This improved the benchmark from its earlier baseline and strengthened the production verifier rather than weakening the benchmark.



\---



\## 5. Multi-Source Reasoning Answer



\### Question



How does your system handle multiple or conflicting sources?



\### Answer



I deliberately separated two questions.



The first is whether multiple sources together support a claim.



The second is whether those sources are safe to combine for an operational answer.



For example, two documents may jointly support the statement that there is a conflict between them.



That claim can be technically supported.



However, Evidence Precedence can still classify the source combination as BLOCK\_COMBINATION, meaning the system should not turn those conflicting sources into operational advice.



This prevents the system from confusing evidence support with permission to act.



\---



\## 6. Hallucination Answer



\### Question



How did you reduce hallucination risk?



\### Answer



I did not rely on one hallucination score.



I broke the problem into several controls.



The system checks whether each claim is grounded in evidence, whether uncertainty has been strengthened, whether mandatory language or actions have been invented, whether conflicting evidence has been hidden, and whether review or abstention boundaries have been violated.



I then combined these signals into a fail-closed assurance decision.



In the adversarial benchmark, the controls identified 11 hallucination-risk cases, 11 overstatement cases, two review-authority increases, one abstention violation and one ignored conflict while still matching all 18 benchmark expectations.



\---



\## 7. Evaluation Answer



\### Question



How did you know your solution was working?



\### Answer



I created a fixed adversarial benchmark rather than evaluating examples subjectively.



The benchmark contains 18 cases with predefined expectations for claim support, citation behaviour, evidence precedence, governance and safe handling.



The benchmark includes positive and negative scenarios.



Twelve cases deliberately represent expected failures or unsafe behaviours.



The important metric is therefore not whether every case produces a normal answer.



The important metric is whether the assurance system reacts exactly as expected.



The final result was 18 out of 18 alignment for citation assurance and 18 out of 18 for integrated faithfulness assurance.



I also ran the full repository regression, which completed with 946 passing tests.



\---



\## 8. Limitation Answer



\### Question



What are the limitations of your project?



\### Answer



The current benchmark is deliberately controlled and contains 18 cases.



A 100 percent benchmark result does not prove universal safety.



It proves that the implementation matches the behaviours encoded in that benchmark.



There are still areas I would expand, including three-source reasoning, long multi-claim answers, numerically dense evidence, complex version chains, citation flooding, role-responsibility hallucination, prompt injection inside retrieved evidence, and more advanced temporal reasoning.



I document those limitations rather than presenting the system as clinically validated.



\---



\## 9. Responsible AI Answer



\### Question



What does responsible AI mean in practical engineering terms to you?



\### Answer



For me, responsible AI means translating abstract principles into technical controls.



For example:



\- traceability becomes provenance and citation checks;

\- transparency becomes evidence-linked claims;

\- uncertainty becomes overstatement detection;

\- human oversight becomes REVIEW\_REQUIRED states;

\- safety becomes fail-closed behaviour;

\- accountability becomes logged decisions and reproducible evaluation;

\- limitation awareness becomes explicit abstention.



I try to make governance executable rather than keeping it only in documentation.



\---



\## 10. Why This Is Relevant to the NHS



\### Question



Why is this work relevant to an NHS role?



\### Answer



The NHS increasingly needs people who can connect data engineering, AI capability and governance.



The difficult part is not simply getting a model to generate an answer.



The difficult part is making sure the answer is supported, reproducible, explainable and safe enough for the intended use.



This project demonstrates that I can translate those operational and governance risks into technical architecture, automated tests and auditable evidence.



That is relevant to senior information, analytics, AI assurance, data engineering and responsible-AI roles.



\---



\## 11. STAR Example



\### Situation



A healthcare RAG system could produce highly plausible answers with citations, but citation presence alone did not guarantee that the answer was supported or safe.



\### Task



Build an assurance approach that could distinguish supported answers from unsupported, overstated, conflicting or governance-inappropriate outputs.



\### Action



I:



\- designed an 18-case adversarial benchmark;

\- hardened citation verification;

\- added citation completeness;

\- implemented multi-source claim verification;

\- added groundedness and overstatement auditing;

\- implemented hallucination-resistance controls;

\- preserved governance ceilings;

\- added safe abstention;

\- created an automated assurance runner;

\- generated machine-readable and human-readable reports;

\- added fail-closed tests.



\### Result



The system achieved:



\- 18/18 citation-assurance benchmark alignment;

\- 18/18 faithfulness benchmark alignment;

\- 13 dedicated automated assurance tests passing;

\- 946 full repository tests passing.



The project now provides reproducible assurance evidence rather than relying solely on model confidence or manual inspection.



\---



\## 12. Thirty-Second Elevator Pitch



I built a healthcare document intelligence RAG system with a separate AI assurance layer.



Instead of trusting generated answers because they contain citations, the system checks whether claims are actually supported, whether citations are complete, whether evidence conflicts, whether uncertainty has been overstated, and whether human review or abstention is required.



I tested it against an 18-case adversarial benchmark and automated the entire assurance workflow.



\---



\## 13. One-Line Portfolio Description



Governance-first healthcare RAG with automated citation, groundedness, hallucination, conflict and abstention assurance.



\---



\## Interview Principle



The strongest message is:



> I did not optimise only for answer quality. I designed for evidence quality, governance and safe failure.



\## Status



\*\*Week 25 Day 6 Session 4 COMPLETE\*\*

