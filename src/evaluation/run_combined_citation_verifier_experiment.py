from __future__ import annotations

import json
import re
from pathlib import Path

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from src.governance.citation_verification import verify_answer_citations


ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    ROOT
    / "data"
    / "synthetic"
    / "citation_evaluation_cases.json"
)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

LEXICAL_THRESHOLD = 0.60
SEMANTIC_RESCUE_THRESHOLD = 0.75


MANDATORY_TERMS = {
    "must",
    "mandatory",
    "requires",
    "required",
    "immediately",
}

PROHIBITION_TERMS = {
    "prohibits",
    "forbids",
    "forbidden",
    "must not",
    "cannot",
}

ACTOR_TERMS = {
    "chief executive",
    "executive",
    "manager",
    "managers",
}

ACTION_TERMS = {
    "suspend",
    "cancel",
    "redeploy",
    "restore",
    "open",
    "close",
}


def normalise(text: str) -> str:
    return re.sub(
        r"[^a-z0-9]+",
        " ",
        text.lower(),
    ).strip()


def remove_document_ids(text: str) -> str:
    return re.sub(
        r"\bDOC-\d+\b",
        "",
        text,
        flags=re.IGNORECASE,
    )


def extract_numbers(text: str) -> set[str]:
    cleaned = remove_document_ids(text)

    return set(
        re.findall(
            r"\b\d+(?:\.\d+)?\b",
            normalise(cleaned),
        )
    )


def contains_any(
    text: str,
    terms: set[str],
) -> set[str]:
    normalised = normalise(text)

    return {
        term
        for term in terms
        if term in normalised
    }


def detect_high_risk_mismatch(
    claim: str,
    evidence: str,
) -> dict:
    reasons = []

    claim_numbers = extract_numbers(claim)
    evidence_numbers = extract_numbers(evidence)

    unsupported_numbers = (
        claim_numbers - evidence_numbers
    )

    if unsupported_numbers:
        reasons.append(
            "unsupported_number"
        )

    claim_mandatory = contains_any(
        claim,
        MANDATORY_TERMS,
    )

    evidence_mandatory = contains_any(
        evidence,
        MANDATORY_TERMS,
    )

    if (
        claim_mandatory
        and not evidence_mandatory
    ):
        reasons.append(
            "unsupported_mandatory_wording"
        )

    claim_prohibition = contains_any(
        claim,
        PROHIBITION_TERMS,
    )

    evidence_prohibition = contains_any(
        evidence,
        PROHIBITION_TERMS,
    )

    if (
        claim_prohibition
        and not evidence_prohibition
    ):
        reasons.append(
            "unsupported_prohibition"
        )

    claim_actors = contains_any(
        claim,
        ACTOR_TERMS,
    )

    evidence_actors = contains_any(
        evidence,
        ACTOR_TERMS,
    )

    unsupported_actors = (
        claim_actors - evidence_actors
    )

    if unsupported_actors:
        reasons.append(
            "unsupported_actor"
        )

    claim_actions = contains_any(
        claim,
        ACTION_TERMS,
    )

    evidence_actions = contains_any(
        evidence,
        ACTION_TERMS,
    )

    unsupported_actions = (
        claim_actions - evidence_actions
    )

    if unsupported_actions:
        reasons.append(
            "unsupported_action"
        )

    claim_normalised = normalise(claim)
    evidence_normalised = normalise(evidence)

    if (
        " not " in f" {claim_normalised} "
        and " not " not in f" {evidence_normalised} "
    ):
        reasons.append(
            "negation_mismatch"
        )

    return {
        "guard_triggered": bool(reasons),
        "reasons": reasons,
    }


def get_evidence_item(
    evidence_items: list[dict],
    document_id: str,
    chunk_id: str | None,
) -> dict | None:
    for evidence in evidence_items:
        if (
            evidence.get("document_id") == document_id
            and evidence.get("chunk_id") == chunk_id
        ):
            return evidence

    return None


def semantic_similarity(
    model: SentenceTransformer,
    claim: str,
    evidence: str,
) -> float:
    embeddings = model.encode(
        [
            claim,
            evidence,
        ]
    )

    return float(
        cosine_similarity(
            [embeddings[0]],
            [embeddings[1]],
        )[0][0]
    )


def evaluate_case(
    model: SentenceTransformer,
    case: dict,
) -> dict:
    baseline = verify_answer_citations(
        case["claims"],
        case["evidence_items"],
        support_threshold=LEXICAL_THRESHOLD,
    )

    if baseline["decision"] == "PASS":
        return {
            "decision": "PASS",
            "method": "lexical_pass",
            "rescued_claims": [],
            "blocked_claims": [],
            "unresolved_claims": [],
        }

    rescued_claims = []
    blocked_claims = []
    unresolved_claims = []

    for claim_result, claim in zip(
        baseline["claim_results"],
        case["claims"],
    ):
        status = claim_result["status"]

        if status == "SUPPORTED":
            continue

        # ----------------------------------------------------------
        # Hard safety rule:
        # citation mismatches can NEVER be semantic-rescued.
        # ----------------------------------------------------------

        if status == "CITATION_MISMATCH":
            blocked_claims.append(
                {
                    "claim_id": claim["claim_id"],
                    "reasons": [
                        "citation_or_lifecycle_mismatch"
                    ],
                }
            )
            continue

        citation = claim.get("citation")

        if not isinstance(citation, dict):
            unresolved_claims.append(
                claim["claim_id"]
            )
            continue

        evidence = get_evidence_item(
            case["evidence_items"],
            citation.get("document_id"),
            citation.get("chunk_id"),
        )

        if evidence is None:
            unresolved_claims.append(
                claim["claim_id"]
            )
            continue

        # ----------------------------------------------------------
        # Semantic rescue only works with Active evidence.
        # ----------------------------------------------------------

        if evidence.get("status") != "Active":
            blocked_claims.append(
                {
                    "claim_id": claim["claim_id"],
                    "reasons": [
                        "non_active_evidence"
                    ],
                }
            )
            continue

        evidence_text = str(
            evidence.get("text", "")
        ).strip()

        if not evidence_text:
            unresolved_claims.append(
                claim["claim_id"]
            )
            continue

        guard = detect_high_risk_mismatch(
            claim["claim_text"],
            evidence_text,
        )

        if guard["guard_triggered"]:
            blocked_claims.append(
                {
                    "claim_id": claim["claim_id"],
                    "reasons": guard["reasons"],
                }
            )
            continue

        score = semantic_similarity(
            model,
            claim["claim_text"],
            evidence_text,
        )

        if score >= SEMANTIC_RESCUE_THRESHOLD:
            rescued_claims.append(
                {
                    "claim_id": claim["claim_id"],
                    "semantic_score": score,
                }
            )
        else:
            unresolved_claims.append(
                claim["claim_id"]
            )

    if (
        not blocked_claims
        and not unresolved_claims
    ):
        return {
            "decision": "PASS",
            "method": "semantic_rescue",
            "rescued_claims": rescued_claims,
            "blocked_claims": [],
            "unresolved_claims": [],
        }

    return {
        "decision": "REVIEW_REQUIRED",
        "method": "review",
        "rescued_claims": rescued_claims,
        "blocked_claims": blocked_claims,
        "unresolved_claims": unresolved_claims,
    }


def main() -> None:
    with INPUT_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        cases = json.load(file)

    model = SentenceTransformer(
        MODEL_NAME
    )

    correct = 0
    false_acceptances = 0
    false_rejections = 0

    print()
    print(
        "WEEK 19 COMBINED CITATION VERIFIER EXPERIMENT"
    )
    print("=" * 80)

    for case in cases:
        result = evaluate_case(
            model,
            case,
        )

        actual = result["decision"]
        expected = case["expected_decision"]

        passed = actual == expected

        if passed:
            correct += 1

        if (
            expected != "PASS"
            and actual == "PASS"
        ):
            false_acceptances += 1

        if (
            expected == "PASS"
            and actual != "PASS"
        ):
            false_rejections += 1

        print()
        print(
            f"{case['case_id']} "
            f"[{case['category']}]"
        )
        print(
            f"  Expected: {expected}"
        )
        print(
            f"  Actual:   {actual}"
        )
        print(
            f"  Method:   {result['method']}"
        )
        print(
            "  Result:   "
            + (
                "PASS"
                if passed
                else "FAIL"
            )
        )

        if result["rescued_claims"]:
            print(
                f"  Rescued:  "
                f"{result['rescued_claims']}"
            )

        if result["blocked_claims"]:
            print(
                f"  Blocked:  "
                f"{result['blocked_claims']}"
            )

        if result["unresolved_claims"]:
            print(
                f"  Unresolved: "
                f"{result['unresolved_claims']}"
            )

    total = len(cases)

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print(
        f"Correct: {correct}/{total}"
    )
    print(
        f"Accuracy: {correct / total:.1%}"
    )
    print(
        f"False acceptances: {false_acceptances}"
    )
    print(
        f"False rejections: {false_rejections}"
    )


if __name__ == "__main__":
    main()