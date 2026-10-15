\# Week 25 Portfolio Positioning — Citation \& Faithfulness Assurance



\## Portfolio Objective



Present the Week 25 work as evidence that the Healthcare Document Intelligence RAG project is not only capable of generating answers, but also capable of evaluating whether those answers are safe, supported, traceable, and governance-aligned.



\## Portfolio Message



The project should not be described as:



> “I built a RAG chatbot with citations.”



A stronger description is:



> “I built a governance-first healthcare RAG assurance layer that verifies citation support, citation completeness, multi-source claims, groundedness, overstatement, evidence conflict, hallucination risk, governance boundaries, and safe abstention.”



\## Why This Matters



In healthcare AI, an answer that looks plausible is not enough.



The system must be able to show:



\- where a claim came from;

\- whether the cited source actually supports the claim;

\- whether all material claims are cited;

\- whether conflicting evidence exists;

\- whether uncertainty has been strengthened;

\- whether unsupported operational advice has been introduced;

\- whether human review is required;

\- whether the system should abstain.



Week 25 turns these requirements into executable assurance controls.



\## Engineering Evidence



The Week 25 implementation includes:



\- authoritative 18-case citation and faithfulness benchmark;

\- citation lifecycle checks;

\- high-risk claim guard ordering;

\- citation completeness audit;

\- multi-citation claim linking;

\- multi-source claim verification;

\- evidence precedence checks;

\- groundedness audit;

\- overstatement audit;

\- hallucination-resistance audit;

\- conflict-coverage audit;

\- governance-preserving decisions;

\- safe abstention checks;

\- automated JSON and Markdown assurance reporting;

\- fail-closed command-line execution;

\- automated regression testing.



\## Quantitative Evidence



Current validated results:



\- benchmark cases: 18;

\- Day 3 citation assurance: 18/18 matched;

\- Day 4 faithfulness assurance: 18/18 matched;

\- benchmark match rate: 100%;

\- hallucination-risk cases detected: 11;

\- overstatement cases detected: 11;

\- review-authority increases detected: 2;

\- abstention violations detected: 1;

\- ignored conflicts detected: 1;

\- Day 5 assurance tests: 13 passed;

\- full repository regression: 946 passed.



These numbers represent controlled benchmark and regression evidence, not claims of universal safety.



\## GitHub Positioning



A recruiter reviewing the repository should be able to see:



\### 1. A clear healthcare problem



Healthcare RAG systems can produce confident answers that are:



\- incompletely cited;

\- based on superseded documents;

\- overly certain;

\- operationally unsafe;

\- inconsistent with governance;

\- unable to handle conflicting evidence safely.



\### 2. A clear engineering response



The project introduces an assurance layer between generated output and final response acceptance.



\### 3. A measurable evaluation method



The project uses a fixed benchmark and regression suite rather than subjective manual inspection alone.



\### 4. Fail-closed behaviour



If assurance fails, the system does not silently proceed.



\### 5. Governance-first design



The system may reduce authority but must not increase it.



\## Suggested README Section



\## Citation \& Faithfulness Assurance



The project includes a dedicated assurance layer for evaluating generated healthcare answers before they are accepted.



Controls include:



\- citation correctness;

\- citation completeness;

\- evidence lifecycle validation;

\- multi-source claim support;

\- groundedness;

\- uncertainty preservation;

\- overstatement detection;

\- hallucination resistance;

\- evidence-conflict handling;

\- governance preservation;

\- safe abstention.



A controlled 18-case benchmark is used to test supported, unsupported, conflicting, overstated, and abstention scenarios.



Current benchmark performance:



\- Citation assurance: 18/18 matched

\- Faithfulness assurance: 18/18 matched

\- Full regression: 946 tests passed



Run the automated assurance suite with:



`python -m src.evaluation.run\_week25\_assurance\_suite`



Generated assurance reports:



\- `outputs/week25\_automated\_assurance\_report.json`

\- `outputs/week25\_automated\_assurance\_report.md`



The benchmark is a controlled regression and assurance framework. It is not presented as proof of universal clinical or operational safety.



\## CV Positioning



\### Technical CV Bullet



Built a governance-first healthcare RAG assurance framework covering citation verification, citation completeness, multi-source evidence, groundedness, overstatement, hallucination resistance, conflict handling, and safe abstention; achieved 18/18 benchmark alignment and 946 passing repository regression tests.



\### Shorter CV Bullet



Engineered an automated assurance layer for healthcare RAG covering citations, groundedness, hallucination risk, conflict handling and governance, with 100% alignment across an 18-case adversarial benchmark.



\### NHS-Focused CV Bullet



Developed a healthcare document intelligence assurance system designed to prevent unsupported, overstated, conflicting, or governance-inappropriate AI responses before they reach NHS users.



\## Recruiter Interpretation



This project demonstrates skills beyond prompt engineering.



It provides evidence of capability in:



\- Python engineering;

\- RAG architecture;

\- evaluation design;

\- AI governance;

\- safety testing;

\- data provenance;

\- healthcare AI assurance;

\- automated testing;

\- reproducible reporting;

\- failure-mode analysis.



\## Band 7 / Senior Analyst Relevance



The work is relevant to senior NHS roles because it demonstrates the ability to:



\- translate risk into technical controls;

\- design reproducible assurance processes;

\- explain AI limitations clearly;

\- distinguish evidence quality from model confidence;

\- protect operational decision-making;

\- document audit evidence;

\- communicate technical risk to non-technical stakeholders.



\## HealthTech AI Engineer Relevance



The project is particularly useful for roles involving:



\- healthcare RAG;

\- clinical document intelligence;

\- AI governance;

\- model assurance;

\- responsible AI;

\- retrieval systems;

\- safety evaluation;

\- AI platform engineering.



\## Portfolio Principle



The project should communicate:



> “I do not treat model output as trustworthy merely because it sounds confident or contains citations. I built an assurance layer that checks whether the answer deserves to be trusted.”



\## Status



\*\*Week 25 Day 6 Session 3 COMPLETE\*\*

