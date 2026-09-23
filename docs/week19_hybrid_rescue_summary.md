# Week 19 Hybrid Rescue Experiment

## Objective

Improve governed retrieval for multi-document operational questions without weakening abstention safety, lifecycle safety, or existing strong semantic/hybrid ranking.

## Starting Point

The governed 38-case baseline was:

| Method | Top-1 | Top-k | Abstention | Active-only |
| --- | --- | --- | --- | --- |
| Semantic | 75.0% | 87.5% | 100% | 100% |
| Hybrid | 75.0% | 87.5% | 100% | 100% |
| RRF-only | 70.8% | 75.0% | 100% | 100% |

## Q027 Failure

> How should severe weather pressure and ambulance handover disruption be considered together?

Semantic retrieval found ambulance-handover evidence but missed severe-weather evidence. BM25 retrieved DOC-009 Severe Weather Operational Plan, and RRF-only preserved evidence for both concepts. Evidence sufficiency correctly marked the semantic/hybrid evidence INSUFFICIENT because the question required both subjects.

## Failed Global RRF Experiment

Replacing the normal hybrid reranker with an RRF-score-first reranker fixed Q027 but reduced overall Hybrid performance:

| Hybrid configuration | Top-1 | Top-k |
| --- | --- | --- |
| Original governed hybrid | 75.0% | 87.5% |
| Global RRF reranking | 70.8% | 75.0% |

Global RRF reranking removed useful semantic ordering and made Hybrid behave too similarly to RRF-only. The global replacement was rejected, and the original hybrid ranking path was restored.

## Final Design

Question → Scope Gate → Original Hybrid Retrieval → Evidence Sufficiency

- If sufficient → keep the original hybrid result unchanged.
- If insufficient → run RRF/BM25 rescue → add only enough missing evidence → re-check evidence sufficiency.
- If still insufficient → ABSTAIN.

Rescue preserves the strongest original evidence where possible, requires coverage gains without losing already covered topics, and respects `final_k`. It uses no arbitrary weighted semantic/RRF score. Existing scope, lifecycle, and evidence-sufficiency controls remain in place. Initial results, rescue candidates, rescued IDs, and evidence decisions are retained for auditability.

The benchmark evaluates `hybrid_rescue` as a separate experimental method; it does not replace the existing hybrid method.

## Q027 Rescue Result

- Initial evidence: INSUFFICIENT.
- Missing concept: `severe_weather`.
- Rescue attempted: True.
- Rescued document: DOC-009 Severe Weather Operational Plan.
- Final evidence: SUFFICIENT.
- Final evidence set: DOC-008, DOC-008, DOC-009.

The repeated DOC-008 entries represent separate retrieved chunks from the same document.

## Final 38-Case Benchmark

The completed experiment figures supplied for this record are:

| Method | Top-1 | Top-k | Abstention | Active-only |
| --- | --- | --- | --- | --- |
| Semantic | 75.0% | 87.5% | 100% | 100% |
| Keyword | 41.7% | 62.5% | 100% | 100% |
| Hybrid | 75.0% | 87.5% | 100% | 100% |
| RRF-only | 70.8% | 75.0% | 100% | 100% |
| Hybrid Rescue | 79.2% | 91.7% | 100% | 100% |

These results apply to the controlled evaluation set and do not establish production performance or general safety.

## Engineering Finding

"Targeted evidence-aware retrieval rescue outperformed globally changing the ranking strategy. Preserving the strongest baseline retrieval path and invoking alternate retrieval only when evidence coverage is incomplete improved both Top-1 and Top-k performance without reducing abstention or lifecycle safety."

This finding refers to the measured abstention and Active-only checks in this experiment.

## NHS Relevance

The system does not switch retrieval strategy for every question. It keeps the normal retrieval path when evidence is adequate, but when an operational question needs evidence from more than one subject area, it can recover missing authoritative evidence before deciding whether it is safe to answer. Concept coverage is still not proof that the evidence supports every proposed claim.

## Validation

Reported validation milestones:

- 11 focused rescue tests passed.
- 270 full project tests passed before benchmark integration.
- 272 tests passed after `hybrid_rescue` benchmark integration.
- 38 evaluation cases.

## Limitations

- Synthetic corpus.
- Small evaluation set.
- Deterministic concept vocabulary requires maintenance.
- No NHS subject-matter-expert validation.
- No production deployment.
- Rescue logic is experimental.
- A larger benchmark is needed before promotion to default retrieval.

## Next Step

Expand the evaluation set before deciding whether hybrid_rescue should become the default governed retrieval strategy.
