\# Week 22 Day 4 — Contradiction, Supersession \& Precedence Handling



\## Objective



Add a deterministic evidence-set assurance layer that can identify when retrieved healthcare evidence:



\- contains risky lifecycle states;

\- should not be automatically combined;

\- explicitly establishes a conflict;

\- explicitly establishes replacement or precedence;

\- requires human review before evidence is combined.



The goal is not to build a general-purpose contradiction detector.



The goal is to make evidence combination safer, auditable and governance-aware.



\---



\## Design Principle



The system must not infer contradiction merely because two documents discuss the same topic.



Day 4 therefore reuses the existing deterministic relationship validator from the governance layer.



Supported relationship types already available:



\- `CONFLICT`

\- `COMPLEMENTS`

\- `REPLACES`

\- `TAKES\_PRECEDENCE`



The existing governance relationship validator remains authoritative for determining whether explicit relationship wording is present in supplied Active evidence.



\---



\## Existing Safety Foundation



Before Day 4, the project already contained:



\- Active-only normal retrieval;

\- lifecycle states:

&#x20; - Active

&#x20; - Superseded

&#x20; - Draft

&#x20; - Archived

\- deterministic evidence-set relationship validation;

\- a relationship registry for navigation;

\- corrective false-premise handling;

\- high-risk relationship claim protection.



The existing relationship registry does not itself prove relationships.



It is used only to help retrieval locate related evidence.



Relationship truth must still be established from evidence.



\---



\## New Module



Created:



`src/evidence/evidence\_precedence.py`



This module performs deterministic evidence combination assessment.



It introduces three outcomes:



\### `SAFE\_TO\_COMBINE`



The evidence set contains no established conflict, replacement or precedence relationship at this layer.



This does not grant permission to answer.



Downstream governance remains authoritative.



\### `REVIEW\_BEFORE\_COMBINATION`



Human review is required before combining the evidence.



This can occur when:



\- Draft material is present;

\- Superseded material is present;

\- Archived material is present;

\- mixed lifecycle states are detected;

\- an explicit replacement relationship is established;

\- an explicit precedence relationship is established;

\- the underlying relationship validator returns an ambiguous review state.



\### `BLOCK\_COMBINATION`



Automatic evidence combination is blocked when an explicit `CONFLICT` relationship is supported by the supplied Active evidence.



\---



\## Lifecycle Assurance



The precedence layer summarizes lifecycle state by document.



It identifies:



\- risky documents;

\- mixed-status documents;

\- document-level status sets.



Risky lifecycle states are:



\- Draft

\- Superseded

\- Archived



These states cannot be treated as equivalent to current Active evidence.



\---



\## Relationship Checks



For every pair of distinct documents, the system checks:



\- `CONFLICT`

\- `REPLACES`

\- `TAKES\_PRECEDENCE`



The existing Week 21 deterministic relationship validator is reused.



No semantic-similarity contradiction inference is introduced.



\---



\## Evidence Object Adapter



During testing, Day 4 exposed an interface difference between two architecture layers.



Structured Evidence Objects use:



`evidence\_text`



The older deterministic relationship validator expects retrieval-style evidence using:



`text`



An explicit adapter was added inside:



`src/evidence/evidence\_precedence.py`



The adapter preserves the Evidence Object and maps:



`evidence\_text -> text`



for compatibility with the existing validator.



This allowed the project to reuse the trusted governance control rather than duplicate relationship logic.



\---



\## Evidence Packet Integration



Updated:



`src/evidence/evidence\_packet.py`



The Evidence Packet now includes:



`precedence\_assessment`



The evidence packet sequence is now:



Question  

→ Scope Gate  

→ Retrieval  

→ Evidence Sufficiency  

→ Structured Evidence Objects  

→ Provenance  

→ Provenance Summary  

→ Lifecycle Summary  

→ Conflict / Supersession / Precedence Assessment  

→ Governance  

→ Audit Summary



The precedence layer does not replace governance.



It adds another evidence-assurance signal.



\---



\## Scope-Gate Preservation



During Day 4 integration, a regression was detected in the out-of-scope Evidence Packet test.



The first Day 4 packet integration attempted to construct evidence before respecting the original scope gate.



This was corrected.



The packet now preserves the intended sequence:



Out of scope  

→ no structured evidence generated  

→ no evidence combination attempted  

→ governance remains responsible for abstention.



Evidence Objects are built only when:



\- `scope.allowed == True`

\- final evidence sufficiency is `True`



This preserves the fail-closed design from earlier Week 22 work.



\---



\## Unit Tests



Created:



`tests/test\_evidence\_precedence.py`



Coverage includes:



1\. single Active document;

2\. Draft evidence;

3\. Superseded evidence;

4\. Archived evidence;

5\. mixed lifecycle state;

6\. two Active documents with no established risky relationship;

7\. explicit conflict;

8\. explicit replacement;

9\. explicit precedence;

10\. empty evidence set;

11\. missing required evidence field;

12\. invalid input type.



Result:



`12 passed`



\---



\## Evidence Packet Regression



Existing packet tests were rerun after Day 4 integration.



Result:



`9 passed`



This confirmed that precedence handling did not break the existing Evidence Packet contract.



\---



\## Real Q027 Check



Question:



> How should severe weather pressure and ambulance handover disruption be considered together?



Architecture v2 retrieval outcome:



\- route: `BOUNDED\_AGENTIC`

\- stop reason: `EVIDENCE\_SUFFICIENT\_AFTER\_REFINEMENT`

\- evidence sufficient: `True`

\- evidence count: `3`

\- documents:

&#x20; - DOC-008

&#x20; - DOC-009



All evidence remained Active.



All three provenance records were VERIFIED.



The Day 4 precedence result was:



`SAFE\_TO\_COMBINE`



The system checked:



\- `CONFLICT`

\- `REPLACES`

\- `TAKES\_PRECEDENCE`



None was established by the supplied Active evidence.



Therefore no precedence-layer block was triggered.



Importantly, governance still returned:



`REVIEW\_REQUIRED`



with:



\- `requires\_human\_review = True`

\- `may\_generate\_answer = False`



This confirms that precedence assessment did not weaken the existing governance decision.



\---



\## Interpretation



Day 4 separates two different questions.



\### Question 1



Can these evidence items be safely combined at the evidence-set level?



Handled by:



`evidence\_precedence.py`



\### Question 2



May the system generate an answer?



Handled by:



the existing governance layer.



For Q027:



\- evidence combination assessment = `SAFE\_TO\_COMBINE`

\- governance outcome = `REVIEW\_REQUIRED`



This separation is intentional.



\---



\## NHS / Manager Interpretation



In operational terms, the system now behaves more like a cautious analyst reviewing several policy documents.



Before combining evidence, it checks:



\- whether the documents are current;

\- whether any are drafts or obsolete;

\- whether one explicitly replaces another;

\- whether one explicitly takes priority over another;

\- whether the documents explicitly conflict.



It does not assume two documents conflict simply because they discuss the same operational issue.



This reduces the risk of mixing outdated or incompatible guidance in an evidence brief.



\---



\## Full Regression



Full project regression after Day 4 changes:



`592 passed`



Previous Day 3 baseline:



`580 passed`



No regression was introduced across the wider project test suite.



\---



\## Architecture After Day 4



Question  

→ Scope Gate  

→ Architecture v2 Retrieval  

→ Evidence Sufficiency  

→ Structured Evidence  

→ Provenance Verification  

→ Lifecycle Check  

→ Conflict / Supersession / Precedence Assessment  

→ Governance  

→ Human Review / Abstention / Allowed Workflow



\---



\## Safety Boundary



Day 4 does not provide general natural-language contradiction detection.



A relationship is treated as established only when supported by explicit evidence through the existing deterministic validator.



Absence of an established conflict does not prove that no real-world conflict exists.



It means only that the supplied evidence does not establish that relationship.



\---



\## Decision



\*\*PASS — KEEP\*\*



The deterministic precedence and evidence-combination layer becomes part of the Week 22 Evidence Packet architecture.



Day 5 can now build a manager-ready Evidence Brief on top of:



\- retrieval intelligence;

\- structured evidence;

\- provenance;

\- lifecycle assurance;

\- precedence handling;

\- governance.

