"""Render all changed cases from the saved untuned benchmark, without inference."""
import json
from pathlib import Path


def render_report(output):
    lines = ["# Week 21 Day 1: untuned reranker comparison", "",
             "Changed means the ordered raw chunk IDs differ from ordinary Hybrid. Tables show post-gate top documents; raw tops are also given. No labels or thresholds were tuned.", "",
             "Top-1/Top-k denominators: 45 labelled cases; abstention: 26 designated cases; total: 75. Active compliance includes empty results. Four cases have neither a relevance label nor expected abstention.", "",
             "Single sequential run; fixed method order, not a repeated latency study. Regression overlapped startup. Total time includes corpus/model preparation; method times exclude evidence assessment (except Rescue's internal gate).", ""]
    def top(record, method):
        ids = record[method]["retrieved_document_ids"]
        return ids[0] if ids else "ABSTAIN"
    def rawtop(record, method):
        rows = record["raw_results"][method]
        return rows[0]["chunk_id"] if rows else "none"
    def change(record, baseline):
        changes = []
        for key, label in [("top1_success", "Top-1"), ("topk_success", "Top-k")]:
            before, after = record[baseline][key], record["hybrid_reranker"][key]
            if before is not None and before != after:
                changes.append(label + (" improved" if after else " worsened"))
        return "; ".join(changes) or "No scoring difference"
    for r in output["case_results"]:
        if [x["chunk_id"] for x in r["raw_results"]["hybrid"]] == [x["chunk_id"] for x in r["raw_results"]["hybrid_reranker"]]:
            continue
        lines += ["## " + r["query_id"], "", r["question"], "",
                  "Expected documents: " + (", ".join(r["hybrid"]["expected_document_ids"]) or "none specified") + ".",
                  "Expected chunk: " + str(r["expected"].get("expected_chunk_id", "not specified")) + ".", "",
                  "| Method | Post-gate top | Raw top chunk |", "|---|---|---|"]
        for method in ["hybrid", "hybrid_reranker", "hybrid_rescue"]:
            lines.append(f"| {method} | {top(r, method)} | {rawtop(r, method)} |")
        lines += ["", "Versus Hybrid: " + change(r, "hybrid") + ".",
                  "Versus Hybrid Rescue: " + change(r, "hybrid_rescue") + "."]
        gate = r["evidence_sufficiency"]["hybrid_reranker"]
        reason = "Relevance ordering changes the selected three-chunk set; this is an observed ordering effect, not proof of the model's reasoning."
        if gate and gate["decision"] != "SUFFICIENT":
            reason = "The unchanged evidence-sufficiency gate rejects the reranked set; ranking changes do not bypass abstention."
        lines += ["Reason: " + reason, ""]
    return "\n".join(lines)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    output = json.loads((root / "outputs/week21_day1_reranker_benchmark.json").read_text())
    (root / "outputs/week21_day1_reranker_case_analysis.md").write_text(render_report(output), encoding="utf-8")
