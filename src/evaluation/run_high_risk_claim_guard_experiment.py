from __future__ import annotations

import re


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
        "expected_guard": False,
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
        "expected_guard": True,
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
        "expected_guard": True,
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
        "expected_guard": True,
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
        "expected_guard": False,
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
        "expected_guard": False,
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
        "expected_guard": True,
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
        "expected_guard": True,
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
        "expected_guard": False,
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
        "expected_guard": True,
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
        "expected_guard": True,
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
        "expected_guard": False,
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
        "expected_guard": True,
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
        "expected_guard": False,
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
        "expected_guard": True,
    },
]


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


def extract_numbers(text: str) -> set[str]:
    return set(
        re.findall(
            r"\b\d+(?:\.\d+)?\b",
            normalise(text),
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


def main() -> None:
    print()
    print(
        "WEEK 19 HIGH-RISK CLAIM GUARD EXPERIMENT"
    )
    print("=" * 72)

    correct = 0

    false_blocks = 0
    missed_guards = 0

    for case in CASES:
        result = detect_high_risk_mismatch(
            case["claim"],
            case["evidence"],
        )

        actual = result[
            "guard_triggered"
        ]

        expected = case[
            "expected_guard"
        ]

        passed = actual == expected

        if passed:
            correct += 1

        if (
            expected is False
            and actual is True
        ):
            false_blocks += 1

        if (
            expected is True
            and actual is False
        ):
            missed_guards += 1

        print()
        print(
            f"{case['case_id']} "
            f"[{case['label']}]"
        )

        print(
            f"  Expected guard: {expected}"
        )

        print(
            f"  Actual guard:   {actual}"
        )

        print(
            f"  Reasons: {result['reasons']}"
        )

        print(
            "  Result: "
            + (
                "PASS"
                if passed
                else "FAIL"
            )
        )

    total = len(CASES)

    print()
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)

    print(
        f"Correct: {correct}/{total}"
    )

    print(
        f"Accuracy: {correct / total:.1%}"
    )

    print(
        f"False blocks: {false_blocks}"
    )

    print(
        f"Missed high-risk cases: {missed_guards}"
    )


if __name__ == "__main__":
    main()