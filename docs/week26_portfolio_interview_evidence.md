\# Week 26 Portfolio and Interview Evidence



\## Healthcare Document Intelligence RAG



This document converts Week 26 engineering work into evidence suitable for:



\- GitHub portfolio review

\- NHS technical interviews

\- HealthTech interviews

\- AI engineering interviews

\- data and AI governance discussions

\- CV bullet development



\---



\# 1. Recruiter-Level Description



Built an adversarial assurance layer for a healthcare RAG system that verifies citation faithfulness, detects conflicting and outdated evidence, contains prompt injection inside retrieved documents, audits semantic overstatement, preserves safe abstention, and fails closed when assurance inputs are malformed.



\---



\# 2. NHS Manager-Level Description



The system is designed to stop an AI assistant from sounding more confident than the evidence allows.



Before an answer can be trusted, the system checks:



\- where the evidence came from

\- whether the source is current

\- whether sources conflict

\- whether the AI exaggerated the original wording

\- whether a document contains instructions trying to manipulate the AI

\- whether the answer should instead be reviewed by a person



If the assurance process itself breaks, the system does not guess.



It abstains.



\---



\# 3. Technical Interview Description



Week 26 extends the RAG assurance architecture beyond ordinary citation matching.



I implemented and tested:



\- adversarial benchmark cases

\- relationship-aware multi-source grounding

\- semantic-strength auditing

\- version and temporal assurance

\- evidence-plane prompt-injection detection

\- abstention-safety validation

\- cross-layer authority invariants

\- fail-closed integration boundaries

\- failure-injection testing

\- a unified operational assurance gate



The central design constraint is authority monotonicity:



> downstream assurance may preserve or reduce answer authority, but it may never increase it.



\---



\# 4. Strong CV Bullet



Designed and implemented a governance-first assurance layer for a healthcare RAG system, including adversarial citation testing, multi-source groundedness, temporal/version controls, prompt-injection containment, safe abstention, cross-layer authority invariants and fail-closed robustness testing.



\---



\# 5. Stronger Engineering CV Bullet



Engineered a regression-tested healthcare RAG assurance framework that evaluates citation faithfulness, source relationships, semantic overstatement, temporal/version safety, prompt injection and abstention behaviour; added system-level authority invariants and controlled failure injection so malformed assurance inputs deterministically fall back to `ABSTAIN`.



\---



\# 6. Band 7 / Senior Analyst Discussion Point



A useful way to explain the project in an NHS interview is:



> I did not design the AI around the assumption that the model would always be correct. I designed the surrounding assurance process so that uncertainty, conflicting evidence, outdated guidance or a control failure reduces the system's authority rather than increasing it.



This connects technical engineering with:



\- patient safety thinking

\- operational governance

\- auditability

\- human review

\- accountable deployment



\---



\# 7. Example Interview Question



\## Question



How would you reduce hallucination risk in a healthcare RAG system?



\## Suggested answer



I would not rely on prompt engineering alone.



I would separate the problem into evidence, generation and assurance layers.



First, I would require structured evidence with provenance and lifecycle metadata.



Second, I would link generated claims back to evidence and verify citation support.



Third, I would check whether multiple sources are genuinely complementary rather than simply numerous.



I would also evaluate semantic strengthening, because an answer can remain lexically similar to a source while changing â€œmayâ€ into â€œmustâ€.



For healthcare guidance I would add version and temporal checks, because newer does not automatically mean authoritative.



Retrieved content would remain in an untrusted evidence plane so instructions inside documents cannot override application governance.



Finally, unresolved conflict or assurance failure would reduce the answer to human review or abstention rather than allowing the model to continue confidently.



\---



\# 8. Example Governance Interview Question



\## Question



What does fail closed mean in your project?



\## Suggested answer



Fail closed means that if the assurance system cannot establish that an answer is safe to issue, the failure does not become permission to answer.



For example, if the governance state is unknown, required safety signals are malformed, or the assurance evaluator encounters an unexpected integration error, the boundary returns `ABSTAIN`.



This is important because error handling itself can become a safety vulnerability if malformed inputs accidentally bypass assurance.



\---



\# 9. Example Prompt-Injection Interview Question



\## Question



How do you handle prompt injection in retrieved documents?



\## Suggested answer



I treat retrieved documents as untrusted evidence, not instructions.



The application and governance rules sit in a trusted control plane.



A retrieved document can contribute facts, but text such as â€œignore previous instructionsâ€ or â€œdo not mention conflicting guidanceâ€ cannot alter the system's governing rules.



I created adversarial benchmark cases specifically for this and added detection for governance, conflict-suppression, authority and response-override attempts.



\---



\# 10. Example Multi-Source Interview Question



\## Question



Why is citation count not enough to prove groundedness?



\## Suggested answer



Because two citations do not necessarily support one combined claim.



They may be unrelated, describe different contexts, refer to different versions, or even conflict.



My Week 26 work introduced relationship-aware groundedness so the system distinguishes complementary evidence from unknown relationships, version succession and explicit conflict.



This prevents a system from creating false consensus by combining individually valid but incompatible sources.



\---



\# 11. Example Semantic Precision Interview Question



\## Question



What subtle hallucination problem did you test?



\## Suggested answer



One important problem is modal strengthening.



An AI can produce an answer that appears very close to the source but changes the authority of the statement.



For example:



\- â€œmayâ€ becomes â€œshouldâ€

\- â€œshouldâ€ becomes â€œrequiredâ€

\- â€œcouldâ€ becomes â€œmustâ€



That kind of change may be operationally significant in healthcare even though most of the wording overlaps.



I therefore added a semantic-precision layer that may reduce support confidence but is not permitted to increase authority.



\---



\# 12. Example Temporal Safety Interview Question



\## Question



Why not simply prefer the newest document?



\## Suggested answer



Because recency and authority are different concepts.



A newer document may be supplementary, draft, locally scoped or not intended to replace the older guidance.



I therefore model version relationships separately from publication dates.



The system can represent current, previous, replacement, parallel-active and unknown version relationships and send ambiguous cases to review.



\---



\# 13. STAR Evidence



\## Situation



Healthcare RAG systems can produce fluent answers even when evidence is conflicting, outdated, adversarial or only partially supportive.



\## Task



Create an assurance architecture that reduces the chance that these failures become authoritative answers.



\## Action



I built a 12-case adversarial benchmark and implemented controls for:



\- relationship-aware groundedness

\- semantic strengthening

\- version and temporal validity

\- prompt injection

\- abstention safety



I then added cross-layer system invariants so assurance could never increase authority, followed by a fail-closed boundary and controlled failure-injection benchmark.



Finally, I combined the assurance layers into a unified operational gate.



\## Result



The project now has a regression-tested, machine-readable assurance path that can distinguish between:



\- safe answering

\- human review

\- abstention



and explicitly handles malformed assurance inputs by failing closed.



\---



\# 14. GitHub Reviewer Takeaway



A technical reviewer should be able to see that this repository is not merely:



\- embeddings

\- vector search

\- prompting

\- LLM output



It also contains:



\- assurance architecture

\- adversarial evaluation

\- governance states

\- testable safety invariants

\- evidence lifecycle reasoning

\- failure injection

\- regression testing

\- documentation explaining engineering decisions



That makes the repository stronger evidence of applied AI engineering than a standard tutorial RAG project.



\---



\# 15. Portfolio Positioning



Recommended project positioning:



\*\*Healthcare Document Intelligence RAG â€” Governance, Citation Faithfulness and Adversarial Assurance\*\*



Suggested one-line description:



> A governance-first healthcare RAG system that combines provenance-aware retrieval, controlled generation and adversarial assurance to decide when an answer can be issued, requires human review, or must abstain.



\---



\# 16. Evidence for Future Roles



The Week 26 work is relevant to roles such as:



\- Healthcare AI Engineer

\- Responsible AI Engineer

\- AI Assurance Engineer

\- Clinical AI Platform Engineer

\- RAG / LLM Engineer

\- AI Governance Technical Specialist

\- Healthcare Data Scientist

\- Senior Information Analyst with AI responsibilities

\- Decision Intelligence Engineer

\- AI Product Assurance Engineer



The strongest differentiation is not simply the use of an LLM.



It is the ability to demonstrate how model output is constrained, evaluated, governed and safely degraded under uncertainty.
