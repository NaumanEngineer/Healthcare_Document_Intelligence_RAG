\# Week 25 Day 2 — Citation \& Faithfulness Baseline Findings



\## Purpose



The initial Week 25 golden benchmark was executed against the existing citation-verification and evidence-precedence logic.



This establishes the pre-hardening baseline for citation and faithfulness assurance.



\---



\# Baseline Result



Cases evaluated:



18



Matched benchmark expectations:



14



Mismatched benchmark expectations:



4



Baseline match rate:



77.8%



Mismatched cases:



\- W25-C007

\- W25-C008

\- W25-C009

\- W25-C012



\---



\# Interpretation Principle



A benchmark mismatch does not automatically mean production code is wrong.



Each mismatch must be classified as one of:



\- benchmark expectation error

\- production safety gap

\- architecture limitation

\- evaluation-model mismatch



The benchmark should expose weaknesses rather than be altered merely to increase the pass rate.



\---



\# W25-C007 — Unsupported Operational Claim



\## Observed



Expected:



PARTIALLY\_SUPPORTED



Actual:



UNSUPPORTED



\## Interpretation



Benchmark expectation error.



The approved evidence states that bed-capacity pressure should be reviewed alongside site-flow and escalation arrangements.



The candidate claim states that leadership should cancel all elective activity immediately.



The evidence does not materially support that action.



Therefore:



UNSUPPORTED



is more appropriate than:



PARTIALLY\_SUPPORTED



\## Decision



Correct the benchmark expectation.



Do not weaken the production verifier.



\---



\# W25-C008 — Compound Claim With Unsupported Mandatory Action



\## Evidence



The evidence supports severe-weather preparation before disruption.



\## Candidate Claim



The candidate claim adds that all elective activity must be cancelled.



\## Expected



PARTIALLY\_SUPPORTED



REVIEW\_REQUIRED



\## Actual



SUPPORTED



PASS



\## Interpretation



Production safety gap.



The candidate contains an unsupported mandatory operational action.



The existing citation verifier can return SUPPORTED through the ordinary lexical-support path before the high-risk mismatch guard is evaluated.



This means high lexical overlap may allow an unsafe additional action or mandatory statement to pass before high-risk checking occurs.



\## Required Hardening



High-risk mismatch checks should occur before any final SUPPORTED decision.



A lexical threshold alone must not bypass high-risk safety controls.



\---



\# W25-C009 — Authority and Certainty Inflation



\## Evidence



Operational escalation may be considered where sustained pressure is identified.



\## Candidate Claim



Operational escalation must be initiated immediately when pressure is identified.



\## Expected



PARTIALLY\_SUPPORTED



REVIEW\_REQUIRED



\## Actual



SUPPORTED



PASS



\## Interpretation



Production safety gap.



The candidate increases both:



\- certainty

\- operational authority



The evidence uses discretionary language:



may be considered



The candidate changes this into:



must be initiated immediately



The existing lexical-support stage allowed the claim to pass before high-risk mismatch checking.



\## Required Hardening



High-risk mismatch detection must run before a claim can receive final SUPPORTED status.



Mandatory wording and authority escalation must not be bypassed by lexical overlap.



\---



\# Shared Finding From C008 and C009



The current verification order permits:



Citation validation



→ Lifecycle validation



→ Lexical support



→ Early SUPPORTED result



→ High-risk mismatch guard



This creates a bypass condition.



The safer order is:



Citation validation



→ Lifecycle validation



→ High-risk mismatch guard



→ Lexical support



→ Guarded semantic rescue where appropriate



→ Final support decision



This preserves deterministic safety checks before similarity-based support decisions.



\---



\# W25-C012 — Conflicting Evidence Claim



\## Expected



SUPPORTED



PASS



with:



BLOCK\_COMBINATION



from the precedence layer.



\## Actual



PARTIALLY\_SUPPORTED



REVIEW\_REQUIRED



while precedence correctly identifies the blocking conflict.



\## Interpretation



Multi-source claim evaluation limitation.



The claim:



"The approved evidence contains conflicting operational positions."



depends on multiple evidence sources.



The current citation-verification contract associates one claim with one citation object.



Therefore the claim-level verifier cannot directly evaluate combined support from both conflicting sources.



The evidence-precedence engine already handles this relationship safely.



\## Decision



Do not force the existing single-citation verifier to treat the claim as fully supported without an explicit architecture decision.



Record multi-source claim verification as a Week 25 capability gap.



Evaluate whether it should be addressed during later Week 25 or Week 26 hardening.



\---



\# Baseline Architecture Findings



The Week 25 baseline revealed three different findings.



\## Benchmark quality issue



W25-C007



The benchmark expectation was too permissive.



\## Production verification gap



W25-C008



W25-C009



High-risk mismatch checking occurs too late in the verification sequence.



\## Architecture limitation



W25-C012



Claim-level verification currently assumes one primary citation per claim, while some claims require multiple evidence sources.



\---



\# Hardening Priority



Priority 1:



Move high-risk mismatch detection ahead of any final lexical SUPPORTED decision.



Priority 2:



Correct the W25-C007 benchmark expectation.



Priority 3:



Document and later evaluate multi-source claim verification for W25-C012.



\---



\# Safety Principle



Lexical similarity must never allow a high-risk claim mutation to bypass deterministic safety checks.



\---



\# Day 2 Engineering Lesson



A benchmark is valuable not because every test passes.



A benchmark is valuable because it distinguishes:



\- incorrect expectations

\- genuine safety defects

\- architecture limitations

\- safe existing behaviour

