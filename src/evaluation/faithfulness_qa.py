from __future__ import annotations


def normalise_text(
    text: str,
) -> str:
    """
    Basic normalisation used by the prototype evaluator.
    """

    if not isinstance(text, str):
        raise TypeError(
            "text must be a string"
        )

    return " ".join(
        text.lower().split()
    )


def split_answer_into_claims(
    answer: str,
) -> list[str]:
    """
    Lightweight claim splitter.

    This prototype uses sentence boundaries.
    It is intentionally simple and transparent.
    """

    if (
        not isinstance(answer, str)
        or not answer.strip()
    ):
        raise ValueError(
            "answer must be a non-empty string"
        )

    cleaned = answer.replace(
        "\n",
        " ",
    )

    raw_claims = cleaned.split(
        "."
    )

    claims = [
        claim.strip()
        for claim in raw_claims
        if claim.strip()
    ]

    return claims


def build_evidence_text(
    evidence_results: list[dict],
) -> str:
    """
    Combine retrieved evidence text into one searchable corpus.
    """

    if not isinstance(
        evidence_results,
        list,
    ):
        raise TypeError(
            "evidence_results must be a list"
        )

    texts = []

    for evidence in evidence_results:
        if not isinstance(
            evidence,
            dict,
        ):
            raise TypeError(
                "each evidence record must be a dictionary"
            )

        text = evidence.get(
            "text"
        )

        if (
            isinstance(text, str)
            and text.strip()
        ):
            texts.append(
                text.strip()
            )

    return normalise_text(
        " ".join(texts)
    )


def claim_keyword_support(
    claim: str,
    evidence_text: str,
) -> bool:
    """
    Lightweight lexical support check.

    A claim is considered potentially supported when enough
    meaningful words from the claim appear in the evidence.

    This is NOT a full semantic faithfulness evaluator.
    """

    claim_normalised = normalise_text(
        claim
    )

    evidence_normalised = normalise_text(
        evidence_text
    )

    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "of",
        "to",
        "in",
        "on",
        "for",
        "with",
        "is",
        "are",
        "was",
        "were",
        "be",
        "should",
        "could",
        "would",
        "may",
        "must",
        "this",
        "that",
        "it",
        "from",
    }

    claim_words = [
        word.strip(
            ".,:;!?()[]{}"
        )
        for word in claim_normalised.split()
    ]

    meaningful_words = [
        word
        for word in claim_words
        if (
            len(word) >= 4
            and word not in stop_words
        )
    ]

    if not meaningful_words:
        return True

    matched = sum(
        1
        for word in meaningful_words
        if word in evidence_normalised
    )

    support_ratio = (
        matched
        / len(
            meaningful_words
        )
    )

    return support_ratio >= 0.6


def evaluate_answer_faithfulness(
    answer: str,
    evidence_results: list[dict],
) -> dict:
    """
    Evaluate lightweight claim-level support against evidence.

    This is a transparent prototype check, not a definitive
    semantic or clinical faithfulness judgement.
    """

    claims = split_answer_into_claims(
        answer
    )

    evidence_text = (
        build_evidence_text(
            evidence_results
        )
    )

    claim_results = []

    for claim in claims:
        supported = (
            claim_keyword_support(
                claim,
                evidence_text,
            )
        )

        claim_results.append(
            {
                "claim": claim,
                "supported": supported,
            }
        )

    supported_count = sum(
        1
        for result in claim_results
        if result[
            "supported"
        ]
    )

    total_claims = len(
        claim_results
    )

    faithfulness_rate = (
        supported_count
        / total_claims
        if total_claims
        else 1.0
    )

    return {
        "total_claims": total_claims,
        "supported_claims": supported_count,
        "unsupported_claims": (
            total_claims
            - supported_count
        ),
        "faithfulness_rate": (
            faithfulness_rate
        ),
        "claims": claim_results,
    }
