\# Week 25 — Citation \& Faithfulness Assurance Framework



\## Purpose



Week 25 strengthens the Healthcare Document Intelligence RAG project by evaluating whether model-assisted answers remain faithful to the approved evidence.



The objective is not simply to confirm that citations exist.



The objective is to verify that:



\- citations are valid

\- citations support the claims they are attached to

\- important claims are not left unsupported

\- the answer does not invent information beyond the evidence

\- the answer does not increase authority beyond the governance state

\- abstention and human-review requirements remain evidence-faithful



\---



\# Week 25 Principle



A citation is not enough.



The cited evidence must actually support the claim being made.



\---



\# Relationship to Week 24



Week 24 proved that model-assisted communication could operate inside a governed architecture.



The system already controls:



\- packet identity

\- governance decision

\- response type

\- human-review state

\- allowed sections

\- citation IDs

\- model output structure

\- abstention preservation

\- deterministic fallback



Week 25 adds a deeper assurance question:



> Even when the output passes the structural contract, is the content actually faithful to the evidence?



\---



\# Faithfulness Model



The Week 25 assurance chain is:



Question



→ Retrieved Evidence



→ Evidence Authority



→ Claim



→ Citation



→ Claim-to-Evidence Support



→ Governance State



→ Final Answer



Every important factual or operational claim should be traceable through this chain.



\---



\# Core Evaluation Dimensions



\## 1. Citation Validity



A citation is valid if the citation ID exists in the approved citation index.



Invalid examples include:



\- unknown citation ID

\- fabricated citation ID

\- citation not supplied to the model

\- duplicate citation misuse



Expected result:



Invalid citations must be rejected.



\---



\## 2. Citation Correctness



A citation is correct if the cited evidence actually supports the associated claim.



A technically valid citation may still be incorrect.



Example:



Claim:



> Bed occupancy is above the escalation threshold.



Citation:



A policy document describing staffing escalation.



The citation exists, but it does not support the claim.



Expected result:



The claim-citation pair should fail citation correctness.



\---



\## 3. Citation Completeness



Citation completeness asks whether all important evidence-dependent claims have appropriate support.



An answer may contain several factual claims while citing only one of them.



Expected result:



Important unsupported claims should be identified.



\---



\## 4. Claim Support



Every evaluated claim should be classified as one of:



SUPPORTED



PARTIALLY\_SUPPORTED



UNSUPPORTED



OVERSTATED



Definitions:



\### SUPPORTED



The approved evidence directly supports the claim.



\### PARTIALLY\_SUPPORTED



The evidence supports part of the claim but not the full wording or scope.



\### UNSUPPORTED



The approved evidence does not support the claim.



\### OVERSTATED



The evidence supports a weaker statement than the model presents.



Example:



Evidence:



> Escalation may be considered.



Model claim:



> Escalation must be initiated immediately.



This is an authority or certainty increase.



\---



\# 5. Evidence Coverage



Evidence coverage asks whether the answer uses enough of the relevant approved evidence to represent the issue faithfully.



Potential failure modes:



\- ignoring a relevant source

\- selecting only supporting evidence while ignoring conflicting evidence

\- missing a higher-authority source

\- over-relying on one document when several are required



\---



\# 6. Source Authority



When multiple sources exist, the system should respect document authority and precedence.



The answer should not prefer:



\- outdated evidence over active evidence

\- lower-authority guidance over approved policy

\- superseded documents over current documents

\- secondary commentary over primary evidence where precedence rules require otherwise



Week 25 evaluation should therefore consider not just whether evidence exists, but whether the correct evidence was used.



\---



\# 7. Unsupported Claim Detection



An unsupported claim is any factual, operational, or decision-oriented statement that cannot be traced to approved evidence.



Examples:



\- invented thresholds

\- invented timelines

\- invented operational instructions

\- unsupported certainty

\- fabricated policy interpretation

\- general model knowledge presented as local evidence



Expected result:



Unsupported claims should be detected and prevented from silently entering the final response.



\---



\# 8. Faithful AUTO\_ANSWER



AUTO\_ANSWER is faithful only if:



\- the answer remains inside the approved evidence

\- citations are valid

\- citations support the associated claims

\- important claims are appropriately cited

\- no unsupported operational recommendation is introduced

\- no authority is increased

\- uncertainty is not hidden



\---



\# 9. Faithful REVIEW\_REQUIRED



REVIEW\_REQUIRED is faithful only if:



\- the model does not provide a final authoritative decision

\- conflicting or insufficient evidence is represented honestly

\- the reason for human review remains visible

\- the model does not collapse uncertainty into false certainty

\- cited evidence accurately supports the review summary



\---



\# 10. Faithful ABSTAIN



ABSTAIN is faithful only if:



\- no substantive answer is produced

\- no unsupported recommendation is introduced

\- no evidence is invented

\- no citation is fabricated

\- the missing-information state remains explicit

\- the safe next action does not become hidden operational advice



\---



\# Claim-Level Evaluation Unit



Week 25 will evaluate the answer at claim level rather than treating the entire answer as one block.



Each claim should be represented conceptually as:



\- claim\_id

\- claim\_text

\- claim\_type

\- citations\_used

\- support\_status

\- supporting\_evidence\_ids

\- authority\_status

\- evaluation\_reason



Example:



claim\_id: C1



claim\_text:

"Operational escalation should be coordinated."



claim\_type:

OPERATIONAL



citations\_used:

\["E1"]



support\_status:

SUPPORTED



supporting\_evidence\_ids:

\["EV1"]



authority\_status:

VALID



evaluation\_reason:

"The approved operational policy directly supports coordinated escalation."



\---



\# Claim Types



Initial claim categories:



FACTUAL



OPERATIONAL



POLICY



UNCERTAINTY



REVIEW



ABSTENTION



These categories may be expanded later if evaluation evidence shows a need.



\---



\# Week 25 Failure Types



The benchmark should detect at least:



CITATION\_UNKNOWN



CITATION\_INCORRECT



CITATION\_MISSING



CLAIM\_UNSUPPORTED



CLAIM\_PARTIALLY\_SUPPORTED



CLAIM\_OVERSTATED



AUTHORITY\_MISMATCH



CONFLICT\_IGNORED



UNCERTAINTY\_HIDDEN



ABSTENTION\_VIOLATION



REVIEW\_AUTHORITY\_INCREASE



\---



\# Evaluation Result Model



Each evaluated answer should eventually produce structured results such as:



case\_id



governance\_decision



response\_type



citation\_validity



citation\_correctness



citation\_completeness



claim\_support\_results



unsupported\_claim\_count



overstated\_claim\_count



authority\_violations



governance\_preserved



overall\_faithfulness\_status



\---



\# Initial Overall Status



Initial overall statuses:



PASS



PASS\_WITH\_WARNINGS



FAIL



Suggested interpretation:



PASS



All important claims are supported and appropriately cited.



PASS\_WITH\_WARNINGS



The answer is materially faithful but contains minor citation or completeness weaknesses that do not change operational meaning.



FAIL



The answer contains unsupported, misleading, incorrectly cited, authority-increasing, or governance-breaking content.



\---



\# Benchmark Philosophy



The benchmark should contain both normal and adversarial cases.



Normal cases test expected system behaviour.



Adversarial cases deliberately attempt to expose:



\- citation misuse

\- unsupported certainty

\- authority inflation

\- hidden recommendations

\- conflicting evidence handling

\- source-precedence failures

\- abstention failures



A strong system should be measured by how safely it fails, not only by how often it produces an answer.



\---



\# Week 25 Success Criteria



Week 25 succeeds if the project can systematically identify:



1\. invalid citations



2\. correct citation IDs attached to unsupported claims



3\. important claims with missing citations



4\. unsupported claims



5\. overstated claims



6\. authority mismatches



7\. ignored conflicting evidence



8\. unsafe certainty



9\. review-state authority increases



10\. abstention violations



\---



\# Relationship to Week 26



Week 25 builds the first citation and faithfulness assurance layer.



Week 26 will deepen the approach through:



\- broader benchmark coverage

\- regression testing

\- more difficult adversarial cases

\- answer-quality audits

\- comparative evaluation

\- evaluation trend tracking

\- stronger reviewer-oriented assurance



\---



\# Portfolio Relevance



This framework demonstrates that the Healthcare Document Intelligence RAG project is evaluated beyond surface-level answer quality.



The project treats:



\- evidence

\- claims

\- citations

\- authority

\- uncertainty

\- governance

\- failure behaviour



as separate assurance concerns.



This is more appropriate for healthcare and other safety-sensitive environments than relying only on whether generated answers appear convincing.



\---



\# Interview Positioning



A useful interview explanation is:



> I do not treat citation presence as proof that a RAG answer is trustworthy. A citation can exist while supporting the wrong claim. I therefore evaluate validity, correctness, completeness, claim-level support, authority, uncertainty and governance preservation separately.



\---



\# Week 25 Day 1 Principle



A credible answer is not one that merely contains citations.



A credible answer is one whose important claims can be traced to the right approved evidence without increasing authority beyond that evidence.

