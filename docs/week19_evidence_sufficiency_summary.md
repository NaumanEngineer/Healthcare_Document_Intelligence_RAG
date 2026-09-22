# Week 19 Evidence Sufficiency Experiment

## Objective

Distinguish three situations:

1. Out-of-scope questions.
2. In-scope questions with insufficient corpus evidence.
3. In-scope questions with adequate evidence.

## Problem Discovered

The scope gate alone achieved 70% abstention success. Q029–Q031 were correctly IN_SCOPE, but the corpus lacked specific evidence for cybersecurity incidents, electronic patient record failure, and medical oxygen supply failure.

Similarity thresholding alone was rejected because unsupported and answerable cases overlapped:

- Q031, unsupported: top semantic score ≈ 0.567.
- Q037, answerable: ≈ 0.500.
- Q026, answerable: ≈ 0.530.
- Q036, answerable: ≈ 0.548.

A threshold high enough to reject Q031 would also reject these legitimate answerable cases, creating false abstentions. Semantic similarity alone did not establish sufficient evidence.

## Solution

A deterministic, concept-first evidence sufficiency layer supports this governance flow:

Question → Scope Gate → Retrieval → Evidence Sufficiency → Lifecycle-safe evidence → Review Decision

This describes the governance flow; existing lifecycle filtering remains within retrieval, and this experiment did not move or replace it. Review decisions remain a separate responsibility.

- Transparent concept aliases recognise specific subjects and their paraphrases, including EPR/electronic patient record and emergency transport/ambulance handover.
- Contextual concepts such as operational pressure are not required when more-specific concepts are present. They remain required when they are the only recognised concept.
- Multi-topic questions require all specific concepts, potentially across several retrieved documents.
- Questions without recognised concepts use a conservative lexical fallback.
- The layer uses no LLM and no similarity threshold as its decision rule.
- Each retrieval method is assessed independently. Insufficient evidence produces empty results for scoring, while original retrieval results and evidence assessments are preserved for auditability.

## Important Cases

| Case | Finding | Outcome |
| --- | --- | --- |
| Q029 | IN_SCOPE, but no cybersecurity evidence | Evidence INSUFFICIENT → ABSTAIN |
| Q030 | IN_SCOPE, but no EPR-failure evidence | Evidence INSUFFICIENT → ABSTAIN |
| Q031 | IN_SCOPE, but no oxygen-supply evidence | Evidence INSUFFICIENT → ABSTAIN |

Q027 is a valid multi-topic question requiring both `severe_weather` and `ambulance_handover`. Semantic retrieval returned ambulance-handover evidence but insufficient severe-weather evidence, so the evidence layer correctly abstained. This is a retrieval limitation, not a scope-classifier failure.

## Validation

- 40 focused evidence-sufficiency tests passed.
- 250 full project tests passed.

## Final 38-Case Governed Benchmark

The completed benchmark figures supplied for this record are:

| Method | Top-1 | Top-k | Abstention | Active-only |
| --- | --- | --- | --- | --- |
| Semantic | 75.0% | 87.5% | 100% | 100% |
| Keyword | 41.7% | 62.5% | 100% | 100% |
| Hybrid | 75.0% | 87.5% | 100% | 100% |
| RRF-only | 70.8% | 75.0% | 100% | 100% |

These results apply to the controlled 38-case evaluation, not production performance.

## Comparison With Scope-Gate-Only Benchmark

| Semantic configuration | Top-1 | Top-k | Abstention | Active-only |
| --- | --- | --- | --- | --- |
| Scope gate only | 79.2% | 87.5% | 70% | 100% |
| Governed scope + evidence | 75.0% | 87.5% | 100% | 100% |

The Top-1 reduction reflects conservative evidence abstention, especially Q027, rather than deterioration of underlying retrieval. Retrieval algorithms were unchanged; the additional gate determines whether retrieved evidence is adequate to proceed.

## Engineering Finding

"The experiment showed that query eligibility and evidence sufficiency are different safety problems. A question may be appropriate for the system's operational scope while still requiring abstention because the available corpus does not substantiate the requested subject."

## NHS Relevance

The assistant should not invent an answer simply because it finds vaguely related NHS operational documents. If the approved evidence needed to answer the exact question is absent, the safer behaviour is to say that adequate evidence was not found and route the issue appropriately.

## Limitations

- Synthetic corpus.
- Only 38 evaluation cases.
- Deterministic concept vocabulary requires maintenance.
- Concept coverage does not prove entailment.
- No NHS subject-matter-expert validation yet.
- Thresholds/concepts are not production-calibrated.
- Q027 exposes a multi-document retrieval weakness.

## Next Experiment

Investigate the Q027 multi-document retrieval failure without weakening the evidence-sufficiency safety gate.
