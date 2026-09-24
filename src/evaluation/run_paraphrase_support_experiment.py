from __future__ import annotations

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


CASES = [
    {
        "case_id": "P001",
        "label": "grounded_paraphrase_business_continuity",
        "claim": (
            "Essential services should be kept running when usual "
            "arrangements are disrupted."
        ),
        "evidence": (
            "Business continuity arrangements maintain essential services "
            "when routine services are disrupted."
        ),
        "expected": "SUPPORTED",
    },
    {
        "case_id": "P002",
        "label": "invented_deadline",
        "claim": (
            "Business continuity arrangements must restore all essential "
            "services within 30 minutes."
        ),
        "evidence": (
            "Business continuity arrangements maintain essential services "
            "when routine services are disrupted."
        ),
        "expected": "UNSUPPORTED",
    },
    {
        "case_id": "P003",
        "label": "invented_action",
        "claim": (
            "Teams should prepare before severe weather disruption and "
            "suspend all outpatient clinics."
        ),
        "evidence": (
            "The severe weather operational plan supports preparation before "
            "weather disruption affects service delivery."
        ),
        "expected": "UNSUPPORTED",
    },
    {
        "case_id": "P004",
        "label": "wrong_number",
        "claim": (
            "Hospital bed occupancy should be reviewed and 95 percent "
            "occupancy requires escalation."
        ),
        "evidence": (
            "Operational teams should review hospital bed capacity "
            "and occupancy."
        ),
        "expected": "UNSUPPORTED",
    },
    {
        "case_id": "P005",
        "label": "grounded_paraphrase_weather",
        "claim": (
            "Teams should make preparations before forecast weather starts "
            "to disrupt services."
        ),
        "evidence": (
            "The severe weather operational plan supports preparation before "
            "weather disruption affects service delivery."
        ),
        "expected": "SUPPORTED",
    },
    {
        "case_id": "P006",
        "label": "grounded_paraphrase_handover",
        "claim": (
            "Operational teams should keep track of delays when ambulance "
            "crews transfer patients into hospital care."
        ),
        "evidence": (
            "Operational teams should monitor ambulance handover delays "
            "and persistent transfer delays."
        ),
        "expected": "SUPPORTED",
    },
    {
        "case_id": "P007",
        "label": "wrong_actor",
        "claim": (
            "The chief executive must personally manage every ambulance "
            "handover delay."
        ),
        "evidence": (
            "Operational teams should monitor ambulance handover delays "
            "and persistent transfer delays."
        ),
        "expected": "UNSUPPORTED",
    },
    {
        "case_id": "P008",
        "label": "wrong_mandatory_action",
        "claim": (
            "Managers must immediately redeploy all available staff whenever "
            "workforce pressure is identified."
        ),
        "evidence": (
            "Operational teams should review workforce pressure, staffing "
            "gaps and available escalation options."
        ),
        "expected": "UNSUPPORTED",
    },
    {
        "case_id": "P009",
        "label": "grounded_paraphrase_workforce",
        "claim": (
            "Teams should assess staffing shortages and available escalation "
            "options when workforce pressure increases."
        ),
        "evidence": (
            "Operational teams should review workforce pressure, staffing "
            "gaps and available escalation options."
        ),
        "expected": "SUPPORTED",
    },
    {
        "case_id": "P010",
        "label": "negation_flip",
        "claim": (
            "Operational teams should not monitor ambulance handover delays."
        ),
        "evidence": (
            "Operational teams should monitor ambulance handover delays "
            "and persistent transfer delays."
        ),
        "expected": "UNSUPPORTED",
    },
    {
        "case_id": "P011",
        "label": "wrong_deadline_weather",
        "claim": (
            "Severe weather preparation must be completed exactly two hours "
            "before disruption begins."
        ),
        "evidence": (
            "The severe weather operational plan supports preparation before "
            "weather disruption affects service delivery."
        ),
        "expected": "UNSUPPORTED",
    },
    {
        "case_id": "P012",
        "label": "grounded_paraphrase_bed_capacity",
        "claim": (
            "Teams should keep reviewing hospital bed availability and "
            "occupancy levels."
        ),
        "evidence": (
            "Operational teams should review hospital bed capacity "
            "and occupancy."
        ),
        "expected": "SUPPORTED",
    },
    {
        "case_id": "P013",
        "label": "wrong_threshold_bed_capacity",
        "claim": (
            "Bed occupancy above 92 percent requires immediate executive "
            "escalation."
        ),
        "evidence": (
            "Operational teams should review hospital bed capacity "
            "and occupancy."
        ),
        "expected": "UNSUPPORTED",
    },
    {
        "case_id": "P014",
        "label": "grounded_paraphrase_site_flow",
        "claim": (
            "Teams should identify flow bottlenecks and keep track of "
            "ownership and progress."
        ),
        "evidence": (
            "Site flow teams should identify bottlenecks, record ownership "
            "and review progress."
        ),
        "expected": "SUPPORTED",
    },
    {
        "case_id": "P015",
        "label": "fabricated_prohibition",
        "claim": (
            "The severe weather plan prohibits use of business continuity "
            "arrangements during disruption."
        ),
        "evidence": (
            "The severe weather operational plan complements wider business "
            "continuity arrangements during weather disruption."
        ),
        "expected": "UNSUPPORTED",
    },
]


THRESHOLDS = [
    0.50,
    0.55,
    0.60,
    0.65,
    0.70,
    0.72,
    0.74,
    0.75,
    0.76,
    0.78,
    0.80,
]


def main() -> None:
    print()
    print("WEEK 19 EXPANDED PARAPHRASE SUPPORT EXPERIMENT")
    print("=" * 80)

    model = SentenceTransformer(
        MODEL_NAME
    )

    for case in CASES:
        embeddings = model.encode(
            [
                case["claim"],
                case["evidence"],
            ]
        )

        score = cosine_similarity(
            [embeddings[0]],
            [embeddings[1]],
        )[0][0]

        case["score"] = float(score)

        print()
        print(
            f"{case['case_id']} "
            f"[{case['label']}]"
        )
        print(
            f"  Expected: {case['expected']}"
        )
        print(
            f"  Semantic similarity: {score:.4f}"
        )

    print()
    print("=" * 80)
    print("THRESHOLD SWEEP")
    print("=" * 80)

    for threshold in THRESHOLDS:
        correct = 0
        false_acceptances = 0
        false_rejections = 0
        failures = []

        for case in CASES:
            actual = (
                "SUPPORTED"
                if case["score"] >= threshold
                else "UNSUPPORTED"
            )

            if actual == case["expected"]:
                correct += 1
            else:
                failures.append(
                    (
                        case["case_id"],
                        case["label"],
                        case["expected"],
                        actual,
                        case["score"],
                    )
                )

            if (
                case["expected"] == "UNSUPPORTED"
                and actual == "SUPPORTED"
            ):
                false_acceptances += 1

            if (
                case["expected"] == "SUPPORTED"
                and actual == "UNSUPPORTED"
            ):
                false_rejections += 1

        print(
            f"Threshold {threshold:.2f} | "
            f"Correct {correct}/{len(CASES)} | "
            f"False Accept {false_acceptances} | "
            f"False Reject {false_rejections}"
        )

        for failure in failures:
            print(
                "  "
                f"{failure[0]} "
                f"[{failure[1]}] "
                f"expected={failure[2]} "
                f"actual={failure[3]} "
                f"score={failure[4]:.4f}"
            )


if __name__ == "__main__":
    main()