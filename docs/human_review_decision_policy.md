\# Human Review Decision Policy



\## Purpose



This document defines how the Healthcare Document Intelligence RAG system decides whether retrieved evidence can support an automatic operational answer, requires human review, or should be rejected.



The objective is not to maximise answer volume.



The objective is to provide useful operational evidence while maintaining clear boundaries, traceability, lifecycle control, and human accountability.



\---



\## Decision Outcomes



The system supports three decision outcomes:



1\. AUTO\_ANSWER

2\. REVIEW\_REQUIRED

3\. ABSTAIN



\---



\# 1. AUTO\_ANSWER



AUTO\_ANSWER means the system has sufficient approved evidence to generate a grounded operational response without mandatory human review.



An AUTO\_ANSWER decision should only be made when:



\- the user question is within the approved operational-policy scope;

\- retrieved evidence comes from Active documents;

\- relevant evidence has been retrieved;

\- there is no known lifecycle conflict;

\- there is no significant ambiguity between multiple competing documents;

\- the question does not request prohibited clinical or prescribing advice;

\- the question does not require live external information;

\- the answer can be grounded directly in retrieved evidence;

\- citations can be provided.



\---



\# 2. REVIEW\_REQUIRED



REVIEW\_REQUIRED means the question is within scope and some relevant evidence exists, but the system should not automatically present the result as authoritative without human inspection.



Human review may be required when:



\- several documents provide plausible but different guidance;

\- retrieved evidence is ambiguous;

\- the top retrieval result is not clearly stronger than alternatives;

\- cross-document reasoning is required;

\- a lifecycle conflict is detected;

\- operational guidance may have significant organisational consequences;

\- evidence appears incomplete;

\- retrieved documents contain potentially conflicting instructions;

\- the system cannot confidently identify one authoritative source.



\---



\# 3. ABSTAIN



ABSTAIN means the system should not attempt to generate a substantive answer from the available corpus.



The system should abstain when:



\- the query is outside the approved operational scope;

\- the user requests medication or prescribing advice;

\- the user requests antibiotic dosing;

\- the question requires current external information not contained in the corpus;

\- no eligible Active evidence is available;

\- retrieval produces no acceptable evidence;

\- available evidence is insufficient to support the requested conclusion.



\---



\# Decision Hierarchy



\## Step 1 — Scope



If the query is out of scope:



ABSTAIN



\---



\## Step 2 — Evidence Availability



If the query is in scope but no eligible evidence is retrieved:



ABSTAIN



\---



\## Step 3 — Lifecycle Safety



Evidence from Draft, Superseded, or Archived documents must not be treated as normal authoritative evidence.



If lifecycle ambiguity cannot be resolved automatically:



REVIEW\_REQUIRED



\---



\## Step 4 — Evidence Clarity



If one clearly relevant Active source supports the query:



AUTO\_ANSWER may be permitted.



If several plausible sources exist and authority is unclear:



REVIEW\_REQUIRED



\---



\## Step 5 — Cross-Document Reasoning



Questions that explicitly require combining multiple operational domains should normally receive:



REVIEW\_REQUIRED



until stronger evidence-combination and verification controls are available.



\---



\# Current Prototype Confidence Rule



AUTO\_ANSWER currently requires:



\- query is in scope;

\- retrieved evidence is Active;

\- top semantic similarity is at least 0.65;

\- score gap between the top two results is at least 0.05;

\- no explicit cross-document reasoning trigger exists;

\- no lifecycle warning exists.



These thresholds are experimental values derived from the current synthetic benchmark.



They are not production or clinically validated thresholds.



\---



\# Human Reviewer Responsibilities



A human reviewer should be able to inspect:



\- original user question;

\- decision outcome;

\- decision reason;

\- retrieved document IDs;

\- document titles;

\- document versions;

\- document status;

\- relevant chunks;

\- retrieval scores;

\- citations;

\- lifecycle warnings;

\- scope warnings.



The reviewer should then be able to:



\- approve;

\- reject;

\- override;

\- request better evidence;

\- escalate to the appropriate operational owner.



\---



\# Auditability



Every decision should eventually record:



\- query ID;

\- question;

\- timestamp;

\- scope decision;

\- evidence used;

\- document lifecycle status;

\- retrieval method;

\- decision outcome;

\- decision reason;

\- reviewer status;

\- reviewer action, if applicable.



\---



\# Governance Principle



The system is an operational evidence assistant.



It is not an autonomous decision-maker.



Human accountability remains with the authorised NHS operational or governance professional.



The system should prefer:



transparent uncertainty



over



unsupported confidence.

