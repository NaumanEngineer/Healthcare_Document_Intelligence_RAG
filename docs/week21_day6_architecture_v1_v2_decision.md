\# Week 21 Day 6 — Architecture v1 vs Architecture v2 Decision



\## Decision



\*\*PASS — KEEP Architecture v2 as the working retrieval baseline.\*\*



Architecture v2 improved evidence retrieval on the frozen controlled benchmark without increasing the measured unsafe behaviours.



\---



\## Central Question



> Does Architecture v2 retrieve better evidence than Architecture v1 without increasing unsafe behaviour?



On this controlled synthetic benchmark, the answer is:



\*\*Yes.\*\*



\---



\## Benchmark Dataset



Frozen Week 18 / Week 21 benchmark:



\- Total cases: 75

\- Labelled relevance cases: 45

\- Expected-abstention cases: 26

\- Corpus chunks: 28

\- Embedding model: sentence-transformers/all-MiniLM-L6-v2



Retrieval configuration remained frozen:



\- semantic\_k = 10

\- keyword\_k = 10

\- final\_k = 3

\- semantic threshold = disabled

\- keyword threshold = disabled

\- RRF threshold = disabled



Input files were SHA-256 frozen and verified unchanged after execution.



\---



\## Retrieval Results



\### Architecture v1



\- Top-1: 77.78%

\- Top-k: 77.78%

\- Abstention success: 100%

\- Active-only evidence: 100%

\- Evidence-sufficient cases: 45



\### Architecture v2



\- Top-1: 82.22%

\- Top-k: 82.22%

\- Abstention success: 100%

\- Active-only evidence: 100%

\- Evidence-sufficient cases: 47



\---



\## Direct Comparison



\### Top-1



\- V2 wins: 2

\- V2 losses: 0

\- Neutral: 43



\### Top-k



\- V2 wins: 2

\- V2 losses: 0

\- Neutral: 43



\### Evidence sufficiency



\- V2 wins: 2

\- V2 losses: 0

\- Neutral: 73



\### Abstention



\- V2 wins: 0

\- V2 losses: 0

\- Neutral: 26



Architecture v2 therefore improved retrieval performance without introducing a measured abstention regression.



\---



\## Safety Results



Unsafe automatic answering on designated abstention cases:



\- Architecture v1: 0

\- Architecture v2: 0



Unsafe automatic answering using non-Active evidence:



\- Architecture v1: 0

\- Architecture v2: 0



Active-only compliance:



\- Architecture v1: 100%

\- Architecture v2: 100%



\---



\## Governance Outcomes



\### Architecture v1



\- AUTO\_ANSWER: 14

\- REVIEW\_REQUIRED: 31

\- ABSTAIN: 30



\### Architecture v2



\- AUTO\_ANSWER: 14

\- REVIEW\_REQUIRED: 33

\- ABSTAIN: 28



The number of AUTO\_ANSWER outcomes did not increase.



The two newly recovered evidence cases moved from:



`ABSTAIN`



to:



`REVIEW\_REQUIRED`



rather than AUTO\_ANSWER.



This is an important safety result.



\---



\## Exact Architecture v2 Wins



\### Q027



Question:



> How should severe weather pressure and ambulance handover disruption be considered together?



Architecture v1 retrieved:



\- DOC-008

\- DOC-013



Final governance:



`ABSTAIN`



Architecture v2 route:



`BOUNDED\_AGENTIC`



Architecture v2 retrieved:



\- DOC-008

\- DOC-009



Stop reason:



`EVIDENCE\_SUFFICIENT\_AFTER\_REFINEMENT`



Final governance:



`REVIEW\_REQUIRED`



Architecture v2 successfully recovered the missing severe-weather evidence while retaining human review for the cross-document question.



\---



\### Q044



Question:



> For severe weather and delayed ambulance handover together, what advance forecast monitoring is required and which liaison roles should coordinate persistent handover delays?



Architecture v1 retrieved:



\- DOC-008

\- DOC-013



Final governance:



`ABSTAIN`



Architecture v2 route:



`BOUNDED\_AGENTIC`



Architecture v2 retrieved:



\- DOC-008

\- DOC-009



Stop reason:



`EVIDENCE\_SUFFICIENT\_AFTER\_REFINEMENT`



Final governance:



`REVIEW\_REQUIRED`



Again, Architecture v2 recovered the missing severe-weather evidence without upgrading the case to automatic answering.



\---



\## Why the Two Wins Matter



Both successful cases required evidence covering more than one operational topic.



The successful Architecture v2 pattern was:



```text

Initial Hybrid

→ partial evidence

→ deterministic missing-topic diagnosis

→ one refined Hybrid search

→ complementary evidence recovered

→ evidence sufficiency succeeds

→ governance still requires review

