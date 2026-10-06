\# Week 21 Day 3 — Relationship-Aware Retrieval



\## Objective



Evaluate whether the system can retrieve not only relevant documents, but also the correct related evidence when explicit policy or procedure relationships matter.



The Day 3 question was:



> Can the system retrieve the right related documents when document relationships such as COMPLEMENTS, REPLACES, TAKES\_PRECEDENCE, or CONFLICT matter, without weakening governance?



\---



\## Existing Architecture



Before Day 3, the project already supported deterministic post-retrieval relationship validation through:



`src/governance/evidence\_set\_relationship.py`



Supported relationship types:



\- CONFLICT

\- COMPLEMENTS

\- REPLACES

\- TAKES\_PRECEDENCE



The existing validator is deliberately conservative.



It requires:

\- multiple relevant documents;

\- Active-only evidence for authoritative relationship validation;

\- explicit relationship language in the supplied evidence.



It does not infer a relationship merely because documents discuss similar topics.



However, retrieval itself had no explicit relationship registry or relationship-aware expansion mechanism.



\---



\## Design Decision



A small explicit document-level relationship registry was introduced rather than a graph database or inferred relationship model.



New module:



`src/retrieval/document\_relationships.py`



The registry stores only source-backed relationships.



Initial verified relationship:



`DOC-011 COMPLEMENTS DOC-003`



This is supported by the synthetic Critical Staffing Contingency Procedure, which explicitly states that it complements the Workforce Escalation Procedure.



Relationships are stored at document level.



Chunks remain evidence units.



The registry is used for navigation only.



It is not considered proof that a relationship exists.



\---



\## Core Safety Principle



The architecture separates:



`registry = navigation`



`evidence = proof`



`governance = decision`



A structured relationship can cause the system to retrieve additional evidence, but the final relationship claim must still be validated by the existing deterministic governance layer.



\---



\## Relationship Directionality



Current traversal semantics:



\- COMPLEMENTS — symmetric for retrieval

\- CONFLICT — symmetric for retrieval

\- REPLACES — directional

\- TAKES\_PRECEDENCE — directional



Directionality affects retrieval expansion only.



It does not alter governance validation.



\---



\## Lifecycle Safety



Relationship-aware retrieval continues to use the existing document lifecycle controls.



Normal retrieval permits Active documents only.



Draft, Superseded, or Archived material may remain available for audit or governance testing but cannot enter the normal evidence set.



Lifecycle status is not treated as equivalent to a relationship.



For example:



`Superseded != explicit REPLACES relationship`



unless the underlying evidence actually establishes the replacement.



\---



\## Relationship-Aware Retrieval



New module:



`src/retrieval/relationship\_aware\_retrieval.py`



The expansion flow is:



Hybrid retrieval

→ inspect retrieved document IDs

→ relationship registry lookup

→ identify related Active documents

→ identify relationship-evidence documents

→ retrieve evidence-bearing chunks

→ retrieve related-document chunks

→ bounded merge

→ downstream evidence sufficiency and governance



The module does not invent semantic scores and does not modify ordinary Hybrid globally.



Relationship expansion is currently bounded by:



`max\_related\_chunks = 2`



\---



\## Important Day 3 Finding



The first implementation retrieved the correct related document but failed governance validation.



Example:



Initial evidence:



\- DOC-011 page 1



Relationship expansion added:



\- DOC-003 page 1

\- DOC-003 page 2



The validator returned:



`RELATIONSHIP\_NOT\_ESTABLISHED`



The reason was that the explicit relationship statement existed in:



`DOC-011-V1.0-P002-C001`



rather than in the initially retrieved DOC-011 page 1 chunk.



This demonstrated that:



> retrieving the correct documents is not sufficient when the relationship proof exists in a specific chunk.



The architecture was therefore refined to prioritise evidence-bearing chunks from `evidence\_document\_id`.



\---



\## Corrected Behaviour



After the refinement, the expanded evidence set became:



\- DOC-011 page 1

\- DOC-011 page 2

\- DOC-003 page 1



The existing governance validator then returned:



`RELATIONSHIP\_SUPPORTED`



Matched relationship term:



`complements`



A false control using:



`CONFLICT`



returned:



`RELATIONSHIP\_NOT\_ESTABLISHED`



This proved that the registry was helping evidence discovery without directly determining relationship truth.



\---



\## Tests



\### Document Relationship Registry



`tests/test\_document\_relationships.py`



32 tests passed.



Coverage includes:



\- explicit relationship lookup

\- symmetric traversal

\- relationship-type filtering

\- invalid relationship rejection

\- duplicate-edge protection

\- unregistered document rejection

\- lifecycle-aware filtering

\- audit access to non-Active relationships



\### Relationship-Aware Retrieval



`tests/test\_relationship\_aware\_retrieval.py`



26 tests passed.



Coverage includes:



\- bounded expansion

\- relationship evidence prioritisation

\- related-document expansion

\- canonical ordering

\- lifecycle filtering

\- duplicate prevention

\- audit metadata

\- non-matching text rejection

\- non-Active evidence rejection

\- expansion limits



\### Full Regression



Full project regression:



`479 passed`



No existing behaviour was broken by the Day 3 changes.



\---



\## Frozen Benchmark



A dedicated Day 3 benchmark compared:



\- Hybrid

\- Hybrid + Relationship-Aware Retrieval



Frozen benchmark size:



75 synthetic healthcare retrieval cases.



Results:



\### Hybrid



\- Top-1 success: 77.78%

\- Top-k success: 77.78%

\- Abstention success: 100%

\- Active-only safety: 100%



\### Hybrid + Relationship-Aware Retrieval



\- Top-1 success: 77.78%

\- Top-k success: 77.78%

\- Abstention success: 100%

\- Active-only safety: 100%



Relationship expansion occurred in 18 cases.



Relationship-evidence chunks were identified in 16 cases.



No Top-1 wins occurred.



No Top-1 losses occurred.



No Top-k wins occurred.



No Top-k losses occurred.



No evidence-sufficiency decision changes occurred.



\---



\## Runtime



Controlled synthetic benchmark runtime:



Hybrid:



approximately 2.66 seconds



Hybrid + Relationship-Aware:



approximately 2.99 seconds



The additional cost was small in this synthetic benchmark.



These timings are development measurements only and must not be presented as production NHS performance.



\---



\## Interpretation



The generic 75-case retrieval benchmark did not show an aggregate retrieval-accuracy improvement.



This does not mean the feature has no value.



The benchmark mainly evaluates expected-document retrieval.



It does not specifically measure whether the evidence set contains the exact chunk required to establish a document relationship.



The targeted DOC-011 / DOC-003 experiment demonstrated a capability that the generic metric does not capture:



Relationship-aware retrieval recovered the explicit relationship-evidence chunk needed for deterministic governance validation.



\---



\## Architecture Decision



Decision:



\*\*PASS — KEEP EXPERIMENTAL\*\*



Relationship-aware retrieval should remain an Architecture v2 experimental capability.



It should not replace Hybrid, Hybrid Rescue, or bounded agentic retrieval.



Each mechanism addresses a different failure mode:



\### Hybrid Rescue



Use when relevant evidence exists deeper in the same query's candidate pool.



\### Bounded Agentic Retrieval



Use when evidence sufficiency identifies a recoverable missing topic that warrants one focused follow-up query.



\### Relationship-Aware Retrieval



Use when an already retrieved document has an explicit, verified relationship to another document and relationship-specific evidence may be needed.



\---



\## Future Routing Direction



Potential Architecture v2 routing:



Question

→ Scope Gate

→ Hybrid Retrieval

→ Evidence Sufficiency

→ deterministic diagnosis



If sufficient:

→ continue



If explicit relationship context exists:

→ Relationship-Aware Retrieval



If recoverable missing topic exists:

→ Bounded Agentic Retrieval



If same-query evidence exists deeper:

→ Hybrid Rescue



If unsupported, unsafe, or external/current evidence is required:

→ Review or Abstain



Then:



→ reassess evidence

→ deterministic governance

→ human review where required



\---



\## Portfolio-Safe Claim



Built and evaluated a deterministic relationship-aware retrieval layer that uses explicit document relationships to locate related and evidence-bearing Active chunks while keeping relationship truth separate from retrieval metadata.



On a frozen 75-case synthetic healthcare benchmark, the capability preserved baseline retrieval accuracy, 100% abstention safety, and 100% Active-only evidence safety. Targeted validation showed that it could recover a missing relationship-evidence chunk and enable deterministic confirmation of an explicitly supported policy relationship without falsely validating an unsupported conflict.



These results are controlled synthetic development measurements and are not production NHS performance claims.

