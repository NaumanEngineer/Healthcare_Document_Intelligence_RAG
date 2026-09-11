from src.evaluation.faithfulness_qa import (
    normalise_text,
    split_answer_into_claims,
    build_evidence_text,
    claim_keyword_support,
    evaluate_answer_faithfulness,
)


def build_evidence() -> list[dict]:
    return [
        {
            "text": (
                "Operational leadership should review "
                "current escalation conditions and apply "
                "the actions defined in the escalation procedure."
            )
        }
    ]


def test_normalise_text():
    result = normalise_text(
        "  Operational   Leadership  "
    )

    assert (
        result
        == "operational leadership"
    )


def test_split_answer_into_claims():
    claims = split_answer_into_claims(
        "Leadership should review pressure. "
        "The escalation procedure should be followed."
    )

    assert len(claims) == 2


def test_build_evidence_text():
    result = build_evidence_text(
        build_evidence()
    )

    assert (
        "operational leadership"
        in result
    )


def test_supported_claim():
    evidence_text = (
        build_evidence_text(
            build_evidence()
        )
    )

    claim = (
        "Operational leadership should review "
        "current escalation conditions"
    )

    assert (
        claim_keyword_support(
            claim,
            evidence_text,
        )
        is True
    )


def test_unsupported_claim():
    evidence_text = (
        build_evidence_text(
            build_evidence()
        )
    )

    claim = (
        "Operational leadership should cancel "
        "all elective surgery immediately"
    )

    assert (
        claim_keyword_support(
            claim,
            evidence_text,
        )
        is False
    )


def test_faithfulness_report():
    answer = (
        "Operational leadership should review "
        "current escalation conditions."
    )

    report = (
        evaluate_answer_faithfulness(
            answer=answer,
            evidence_results=build_evidence(),
        )
    )

    assert (
        report[
            "faithfulness_rate"
        ]
        == 1.0
    )

    assert (
        report[
            "unsupported_claims"
        ]
        == 0
    )
