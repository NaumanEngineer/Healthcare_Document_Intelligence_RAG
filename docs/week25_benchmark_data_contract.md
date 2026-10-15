\# Week 25 — Benchmark Data Contract



\## Purpose



The Week 25 benchmark requires a consistent structure so citation and faithfulness evaluation can be automated, repeatable, and auditable.



The benchmark must align with the Healthcare Document Intelligence RAG architecture that already exists.



Week 25 therefore reuses the project's existing:



\- evidence object structure

\- citation index structure

\- claim-citation linkage

\- lifecycle controls

\- precedence decisions

\- governance decisions

\- citation verification statuses



The benchmark must not introduce a competing production schema.



\---



\# Benchmark Design Principle



A benchmark is useful only if:



1\. expected behaviour is defined before evaluation;



2\. benchmark fields reflect the real system;



3\. failures remain visible;



4\. the benchmark does not invent production fields that do not exist.



\---



\# Benchmark Case Structure



Each benchmark case should contain the following fields.



\## case\_id



Unique benchmark identifier.



Example:



W25-C001



\---



\## case\_name



Short descriptive name.



Example:



clean\_supported\_auto\_answer



\---



\## description



Human-readable explanation of the behaviour being tested.



\---



\## question



The operational or management question being evaluated.



\---



\## expected\_governance\_decision



Allowed values:



AUTO\_ANSWER



REVIEW\_REQUIRED



ABSTAIN



\---



\## expected\_response\_type



Allowed values:



ANSWER



REVIEW



ABSTENTION



\---



\# Evidence Items



\## evidence\_items



List of evidence records supplied to the benchmark case.



Evidence records should reuse the existing production evidence structure where relevant.



Existing fields include:



\- evidence\_id

\- document\_id

\- chunk\_id

\- title

\- document\_type

\- source\_type

\- source\_location

\- source\_file

\- version

\- effective\_date

\- status

\- page

\- chunk\_number

\- evidence\_text

\- ingestion\_batch\_id

\- retrieval\_route

\- evidence\_role

\- retrieval\_scores



Not every synthetic benchmark case must populate every optional field.



Required identity and provenance fields should remain consistent with the production architecture.



\---



\# Evidence Identity



Existing evidence identity follows:



EVIDENCE::<chunk\_id>



Example:



EVIDENCE::DOC-001-V1.0-P002-C001



The Week 25 benchmark must not create an alternative evidence-ID convention.



\---



\# Citation Index



\## citation\_index



List of citations available to the governed answer context.



Citation records should reuse the existing structure.



Fields include:



\- citation\_id

\- evidence\_id

\- document\_id

\- chunk\_id

\- page

\- source\_file

\- version

\- status



Example:



citation\_id:

E1



evidence\_id:

EVIDENCE::DOC-001-V1.0-P002-C001



document\_id:

DOC-001



chunk\_id:

DOC-001-V1.0-P002-C001



page:

2



source\_file:

DOC-001\_operational\_escalation\_policy.pdf



version:

1.0



status:

Active



\---



\# Required Citation IDs



\## required\_citation\_ids



Citation IDs expected to appear when the relevant material claims are made.



Example:



\["E1"]



\---



\# Allowed Citation IDs



\## allowed\_citation\_ids



Complete set of citation IDs that may legitimately appear.



\---



\# Forbidden Citation IDs



\## forbidden\_citation\_ids



Citation IDs that must not appear.



These may represent:



\- irrelevant evidence

\- incorrect benchmark traps

\- unsafe lifecycle evidence

\- evidence excluded by the expected reasoning path



\---



\# Expected Claims



\## expected\_claims



Material claims expected to appear or be represented faithfully.



Each expected claim should contain:



\- claim\_id

\- claim\_text

\- expected\_support\_status

\- supporting\_evidence\_ids

\- required\_citation\_ids



Example:



claim\_id:

C1



claim\_text:

"Operational escalation should be coordinated."



expected\_support\_status:

SUPPORTED



supporting\_evidence\_ids:

\["EVIDENCE::DOC-001-V1.0-P002-C001"]



required\_citation\_ids:

\["E1"]



\---



\# Production Claim Support Statuses



Week 25 should use the production citation-verification statuses:



SUPPORTED



PARTIALLY\_SUPPORTED



UNSUPPORTED



CITATION\_MISMATCH



These are authoritative production statuses.



\---



\# Analytical Labels



The evaluation layer may use additional analytical labels for reporting purposes, such as:



OVERSTATEMENT\_DETECTED



UNCERTAINTY\_HIDDEN



CONFLICT\_IGNORED



CITATION\_INCOMPLETE



ABSTENTION\_VIOLATION



REVIEW\_AUTHORITY\_INCREASE



These labels must not be confused with the production verifier's support statuses.



\---



\# Forbidden Claims



\## forbidden\_claims



Material statements that must not appear.



Examples:



\- fabricated thresholds

\- unsupported timelines

\- invented policy interpretation

\- authoritative recommendations under REVIEW\_REQUIRED

\- substantive advice under ABSTAIN



\---



\# Expected Verification Decision



\## expected\_verification\_decision



Expected answer-level result from the existing citation-verification layer.



Allowed values:



PASS



REVIEW\_REQUIRED



ABSTAIN



\---



\# Expected Precedence Decision



\## expected\_precedence\_decision



Used where evidence precedence is relevant.



Existing values include:



SAFE\_TO\_COMBINE



REVIEW\_BEFORE\_COMBINATION



BLOCK\_COMBINATION



This field may be omitted for cases where precedence is not relevant.



\---



\# Human Review



\## requires\_human\_review



Boolean:



true



or:



false



\---



\# Conflict Expectation



\## conflict\_expected



Boolean indicating whether the case deliberately contains materially conflicting evidence.



\---



\# Uncertainty Expectation



\## uncertainty\_expected



Boolean indicating whether uncertainty should remain visible.



\---



\# Abstention Expectation



\## abstention\_expected



Boolean indicating whether the safe behaviour is to avoid a substantive answer.



\---



\# Benchmark Tags



\## benchmark\_tags



List used for grouping and analysis.



Potential values include:



citation\_validity



citation\_correctness



citation\_completeness



claim\_support



lifecycle



precedence



conflict



uncertainty



review



abstention



adversarial



missing\_evidence



semantic\_rescue



high\_risk\_mismatch



regression



\---



\# Case-Level Evaluation Result



The Week 25 runner should eventually produce one structured result per case.



Initial result fields should include:



\- case\_id

\- case\_name

\- expected\_governance\_decision

\- actual\_governance\_decision

\- expected\_response\_type

\- actual\_response\_type

\- expected\_verification\_decision

\- actual\_verification\_decision

\- expected\_precedence\_decision

\- actual\_precedence\_decision

\- claim\_results

\- citation\_validity\_status

\- citation\_completeness\_status

\- unsupported\_claim\_count

\- partially\_supported\_claim\_count

\- citation\_mismatch\_count

\- governance\_preserved

\- human\_review\_preserved

\- abstention\_preserved

\- failure\_reasons

\- overall\_faithfulness\_status



\---



\# Overall Faithfulness Status



Allowed benchmark-level outcomes:



PASS



PASS\_WITH\_WARNINGS



FAIL



\---



\# PASS



A case passes if:



\- governance is preserved

\- response type is correct

\- expected citation-verification behaviour occurs

\- material claims are appropriately supported

\- required citations are present

\- forbidden citations are absent

\- no unsafe lifecycle evidence is treated as authoritative support

\- no material conflict is hidden

\- no unsafe authority increase occurs



\---



\# PASS\_WITH\_WARNINGS



A case may pass with warnings if:



\- the response remains materially faithful

\- governance remains preserved

\- no safety-significant authority increase occurs

\- only minor non-material completeness or presentation weaknesses remain



Warnings must remain visible.



\---



\# FAIL



A case fails if any material citation, faithfulness, governance, lifecycle, or precedence condition is violated.



Examples:



\- fabricated citation

\- citation mismatch

\- unsupported material claim

\- hidden conflict

\- unsafe lifecycle source accepted

\- incorrect governance state

\- REVIEW\_REQUIRED converted into an authoritative decision

\- ABSTAIN converted into substantive advice



\---



\# Existing Citation Verification Behaviour



The project already verifies:



\- citation presence

\- citation resolution

\- document identity

\- chunk identity

\- lifecycle safety

\- lexical claim support

\- high-risk mismatches

\- guarded semantic paraphrase rescue



Week 25 must build around these behaviours.



\---



\# High-Risk Mismatch Principle



Semantic rescue must not override hard safety concerns.



These include:



\- citation mismatch

\- unsafe lifecycle state

\- unsupported numerical claims

\- unsupported mandatory wording

\- unsupported actors

\- unsupported actions

\- negation mismatch

\- unsupported prohibitions



\---



\# Citation Completeness Extension



Week 25 introduces a new assurance question:



> Did every material answer claim enter the claim-verification process?



This is different from verifying claims that were already supplied.



A system may correctly validate all submitted claims while failing to capture another material statement.



Therefore citation completeness is a benchmark-level concern.



\---



\# Cross-Evidence Faithfulness Extension



Week 25 should also test whether:



\- all materially relevant evidence is represented where necessary

\- conflicting evidence is not selectively ignored

\- unsafe lifecycle evidence is not preferred

\- valid citations are not used to justify broader unsupported claims



\---



\# Initial Benchmark Categories



The Week 25 inventory includes cases covering:



1\. clean supported AUTO\_ANSWER



2\. correct multi-source answer



3\. valid citation attached to wrong claim



4\. material claim missing citation



5\. unknown citation



6\. irrelevant citation



7\. unsupported operational claim



8\. partially supported claim



9\. overstatement



10\. lower-quality or unsafe source handling



11\. superseded source handling



12\. conflicting evidence requiring review



13\. ignored conflict



14\. hidden uncertainty



15\. REVIEW\_REQUIRED becoming authoritative



16\. missing evidence requiring ABSTAIN



17\. ABSTAIN containing substantive advice



18\. fabricated threshold



\---



\# Minimum Week 25 Benchmark Size



Initial target:



18 cases.



The purpose is not benchmark volume.



The purpose is strong coverage of meaningful failure modes.



\---



\# Regression Requirement



All earlier citation, evidence, precedence, governance, answer-context, and generation tests must remain valid.



Week 25 hardening must not weaken previous safety controls.



\---



\# Architecture Rule



Do not add production fields merely because they are convenient for the benchmark.



If benchmark evidence demonstrates a genuine architecture gap, that change should be made explicitly and tested separately.



\---



\# Week 25 Data Contract Principle



The benchmark evaluates the system that actually exists, not an imagined version of it.

