\# Week 25 — Existing Architecture Alignment



\## Purpose



Before implementing the Week 25 citation and faithfulness benchmark, the existing Healthcare Document Intelligence RAG architecture was inspected.



The purpose was to avoid creating a parallel evaluation schema that duplicates or contradicts existing evidence, citation, provenance, and precedence structures.



Week 25 will extend the existing architecture rather than replace it.



\---



\# Architecture Finding



The project already contains mature components for:



\- evidence-object construction

\- provenance preservation

\- evidence packets

\- lifecycle handling

\- evidence precedence

\- claim-to-citation linkage

\- citation verification

\- high-risk claim mismatch detection

\- lexical support checking

\- guarded semantic paraphrase rescue

\- governance-aware answer verification



Therefore Week 25 should focus on:



> Benchmarking, regression testing, completeness auditing, adversarial evaluation, and faithfulness measurement across the existing controls.



It should not rebuild citation verification from scratch.



\---



\# Existing Evidence Contract



The existing evidence architecture already uses fields including:



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



Week 25 benchmark data should reuse these names where relevant.



\---



\# Existing Evidence Identity



Evidence identity follows the existing pattern:



EVIDENCE::<chunk\_id>



Example:



EVIDENCE::DOC-001-V1.0-P002-C001



The benchmark should not introduce a competing evidence-identity convention.



\---



\# Existing Citation Contract



The existing answer-context citation index uses fields including:



\- citation\_id

\- evidence\_id

\- document\_id

\- chunk\_id

\- page

\- source\_file

\- version

\- status



Week 25 should reuse this citation structure.



\---



\# Existing Claim-Citation Structure



The project already links grounded-answer claims to approved citations.



Existing claim-level concepts include:



\- claim text

\- support status

\- citation IDs

\- substantive vs non-substantive claims



Existing linkage behaviour already checks:



\- packet identity

\- governance consistency

\- response-type consistency

\- known citation IDs

\- duplicate citation IDs



Week 25 should build assurance metrics around this existing linkage rather than creating an unrelated claim format.



\---



\# Existing Citation Verification Input



Citation verification currently evaluates claim objects conceptually shaped as:



claim\_id



claim\_text



citation:

\- document\_id

\- chunk\_id



The citation resolves against supplied evidence.



\---



\# Existing Citation Verification Statuses



The production verifier currently returns:



SUPPORTED



PARTIALLY\_SUPPORTED



UNSUPPORTED



CITATION\_MISMATCH



These statuses should remain authoritative for Week 25 unless later evidence justifies an explicit production change.



Week 25 should not silently rename these statuses.



\---



\# Existing Answer-Level Verification Decisions



The current citation verification layer returns:



PASS



REVIEW\_REQUIRED



ABSTAIN



Current behaviour includes:



PASS



All verified material claims are supported.



REVIEW\_REQUIRED



At least one claim is:



\- unsupported

\- partially supported

\- citation mismatched



ABSTAIN



No answer claims were supplied for verification.



\---



\# Existing Lifecycle Safety



The citation verifier treats Active evidence as lifecycle-safe.



Evidence with lifecycle states such as:



\- Superseded

\- Draft

\- Archived



must not silently support authoritative answers.



Lifecycle status is already a meaningful safety signal in the architecture.



Week 25 should reuse `status`.



\---



\# Existing Precedence Controls



The project already evaluates evidence combination using precedence decisions including:



SAFE\_TO\_COMBINE



REVIEW\_BEFORE\_COMBINATION



BLOCK\_COMBINATION



Existing precedence reasoning already covers:



\- non-active lifecycle states

\- mixed lifecycle states

\- explicit conflicts

\- document replacement relationships

\- explicit precedence relationships

\- missing evidence



Week 25 benchmark cases should assert expected precedence behaviour where relevant.



\---



\# Important Schema Correction



The initial Week 25 benchmark draft proposed fields such as:



authority\_rank



At present, this inspection has not established `authority\_rank` as part of the production evidence contract.



Therefore Week 25 must not pretend this field already exists.



For Week 25, authority and precedence should initially be evaluated using existing signals:



\- lifecycle status

\- precedence decision

\- replacement relationships

\- conflict relationships

\- document identity

\- evidence provenance



If later evaluation demonstrates that an explicit authority ranking is genuinely required, that should be introduced as a deliberate architecture change rather than silently added to benchmark data.



\---



\# Existing Faithfulness Controls



The citation verifier already combines multiple assurance stages.



\## Citation presence



Claims without citations are unsupported.



\## Citation resolution



Citation document/chunk identifiers must resolve to supplied evidence.



\## Lifecycle safety



Unsafe lifecycle evidence cannot pass as valid support.



\## Lexical support



Material claim terms are compared against evidence terms.



\## High-Risk Mismatch Guard



Material mismatches block semantic rescue.



High-risk categories include concerns such as:



\- unsupported numbers

\- mandatory wording

\- actors

\- actions

\- negation

\- prohibitions



\## Guarded Semantic Rescue



Low-risk paraphrases may be recovered through semantic similarity.



Semantic similarity is not treated as factual proof.



It cannot override hard safety failures.



\---



\# Existing Semantic Safety Principle



Semantic similarity may assist with safe paraphrase recognition.



It must not override:



\- citation mismatch

\- unsafe lifecycle state

\- unsupported numerical claims

\- unsupported mandatory wording

\- unsupported actors

\- unsupported actions

\- negation mismatch

\- unsupported prohibitions



This principle should remain unchanged during Week 25.



\---



\# Week 25 Extension Layer



Week 25 should now add capabilities around the existing architecture.



The intended progression is:



Existing Evidence Objects



→ Existing Evidence Precedence



→ Existing Governed Answer Context



→ Existing Claim-Citation Linkage



→ Existing Citation Verification



→ NEW Week 25 Benchmark Cases



→ NEW Citation Completeness Auditing



→ NEW Cross-Claim Faithfulness Evaluation



→ NEW Adversarial Regression Tests



→ NEW Benchmark Metrics



→ NEW Assurance Reporting



\---



\# Week 25 Benchmark Adaptation



The benchmark should use real project terminology.



Each case should initially capture:



\- case\_id

\- case\_name

\- description

\- question

\- expected\_governance\_decision

\- expected\_response\_type

\- evidence\_items

\- citation\_index

\- expected\_claim\_support

\- expected\_verification\_decision

\- expected\_precedence\_decision where relevant

\- required\_citation\_ids

\- forbidden\_citation\_ids

\- uncertainty\_expected

\- requires\_human\_review

\- benchmark\_tags



\---



\# Expected Claim Support



Benchmark expectations should initially use the production statuses:



SUPPORTED



PARTIALLY\_SUPPORTED



UNSUPPORTED



CITATION\_MISMATCH



Additional analytical labels may be introduced by the Week 25 evaluation layer, but they must not be confused with existing production verifier statuses.



\---



\# Overstatement Handling



The Week 25 framework uses the concept:



OVERSTATED



The current production verifier does not expose `OVERSTATED` as a separate status.



Instead, some overstatement behaviour may already be detected through high-risk mismatch controls and appear as:



PARTIALLY\_SUPPORTED



or:



UNSUPPORTED



Week 25 should first measure this behaviour.



A separate OVERSTATED production status should only be introduced if benchmark evidence proves it is useful and does not duplicate existing high-risk mismatch handling.



\---



\# Authority Handling



The Week 25 framework also uses the concept of authority increase.



The existing architecture already provides signals through:



\- governance decisions

\- lifecycle status

\- precedence analysis

\- review requirements

\- abstention

\- high-risk mismatch detection



Week 25 should evaluate authority preservation using these existing controls first.



No artificial numeric authority ranking should be introduced without a demonstrated need.



\---



\# Citation Completeness Gap



The existing verifier is strong at checking a claim that has been supplied for verification.



Week 25 must additionally test:



> Did all material claims in the answer reach claim-level verification?



This is different from asking whether a supplied claim has a valid citation.



A system can verify every submitted claim correctly while still missing an uncaptured material claim.



Therefore citation completeness becomes an important Week 25 extension.



\---



\# Cross-Evidence Faithfulness Gap



Week 25 should also test cases where:



\- several evidence items are relevant

\- only one is cited

\- conflicting evidence exists

\- a superseded source competes with an active source

\- a valid citation supports only part of a broader answer



These require benchmark-level reasoning beyond individual citation validity.



\---



\# Regression Assurance



Week 25 should preserve existing behaviours while extending assurance.



Existing citation, evidence, precedence, answer-context, and governance tests must continue to pass.



New Week 25 code should not weaken earlier controls.



\---



\# Week 25 Engineering Decision



Week 25 will not rebuild:



\- evidence objects

\- citation identity

\- lifecycle validation

\- claim-citation linking

\- basic citation verification

\- evidence precedence



Week 25 will build around them.



\---



\# Day 1 Architecture Decision



The Week 25 benchmark must reflect the real system.



The production architecture remains the source of truth.



Benchmark design adapts to the architecture where appropriate.



Architecture changes are introduced only when benchmark evidence demonstrates a genuine gap.



\---



\# Day 1 Principle



Do not build an evaluation system for an imaginary architecture.



Evaluate the architecture that actually exists.

