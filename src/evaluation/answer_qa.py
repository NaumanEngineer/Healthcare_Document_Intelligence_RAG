from __future__ import annotations

import re


def build_allowed_citation_index(
    citations: list[dict],
) -> dict:
    """
    Build lookup sets for citation validation.
    """

    if not isinstance(citations, list):
        raise TypeError(
            "citations must be a list"
        )

    allowed = {
        "document_ids": set(),
        "titles": set(),
        "versions": set(),
        "pages": set(),
        "chunk_ids": set(),
    }

    for citation in citations:
        if not isinstance(citation, dict):
            raise TypeError(
                "each citation must be a dictionary"
            )

        document_id = citation.get(
            "document_id"
        )
        title = citation.get(
            "title"
        )
        version = citation.get(
            "version"
        )
        page = citation.get(
            "page"
        )
        chunk_id = citation.get(
            "chunk_id"
        )

        if isinstance(
            document_id,
            str,
        ) and document_id.strip():
            allowed["document_ids"].add(
                document_id.strip()
            )

        if isinstance(
            title,
            str,
        ) and title.strip():
            allowed["titles"].add(
                title.strip()
            )

        if isinstance(
            version,
            str,
        ) and version.strip():
            allowed["versions"].add(
                version.strip()
            )

        if (
            isinstance(page, int)
            and not isinstance(page, bool)
            and page > 0
        ):
            allowed["pages"].add(
                page
            )

        if isinstance(
            chunk_id,
            str,
        ) and chunk_id.strip():
            allowed["chunk_ids"].add(
                chunk_id.strip()
            )

    return allowed


def extract_chunk_ids_from_answer(
    answer: str,
) -> set[str]:
    """
    Extract chunk IDs using the canonical project pattern.
    """

    if not isinstance(answer, str):
        raise TypeError(
            "answer must be a string"
        )

    pattern = (
        r"\bDOC-\d+-V[0-9.]+-P\d+-C\d+\b"
    )

    return set(
        re.findall(
            pattern,
            answer,
        )
    )


def extract_document_ids_from_answer(
    answer: str,
) -> set[str]:
    """
    Extract document IDs such as DOC-001.
    """

    if not isinstance(answer, str):
        raise TypeError(
            "answer must be a string"
        )

    pattern = r"\bDOC-\d+\b"

    return set(
        re.findall(
            pattern,
            answer,
        )
    )


def find_unsupported_chunk_ids(
    answer: str,
    citations: list[dict],
) -> set[str]:
    """
    Return chunk IDs present in the answer but absent from
    the approved citation set.
    """

    allowed = build_allowed_citation_index(
        citations
    )

    used = extract_chunk_ids_from_answer(
        answer
    )

    return used - allowed[
        "chunk_ids"
    ]


def find_unsupported_document_ids(
    answer: str,
    citations: list[dict],
) -> set[str]:
    """
    Return document IDs present in the answer but absent
    from the approved citation set.
    """

    allowed = build_allowed_citation_index(
        citations
    )

    used = extract_document_ids_from_answer(
        answer
    )

    return used - allowed[
        "document_ids"
    ]


def validate_answer_citations(
    answer: str,
    citations: list[dict],
) -> None:
    """
    Reject generated answers that reference unsupported
    document IDs or chunk IDs.
    """

    if (
        not isinstance(answer, str)
        or not answer.strip()
    ):
        raise ValueError(
            "answer must be a non-empty string"
        )

    unsupported_chunks = (
        find_unsupported_chunk_ids(
            answer,
            citations,
        )
    )

    if unsupported_chunks:
        raise ValueError(
            "Unsupported chunk citation(s): "
            + ", ".join(
                sorted(
                    unsupported_chunks
                )
            )
        )

    unsupported_documents = (
        find_unsupported_document_ids(
            answer,
            citations,
        )
    )

    if unsupported_documents:
        raise ValueError(
            "Unsupported document citation(s): "
            + ", ".join(
                sorted(
                    unsupported_documents
                )
            )
        )


def validate_answer_result(
    answer_result: dict,
) -> dict:
    """
    Validate one structured answer-generator result.

    Expected states:

    generated
    or
    insufficient_evidence
    """

    if not isinstance(
        answer_result,
        dict,
    ):
        raise TypeError(
            "answer_result must be a dictionary"
        )

    required_fields = (
        "status",
        "answer",
        "citations",
        "generation_used",
    )

    for field in required_fields:
        if field not in answer_result:
            raise ValueError(
                f"Missing answer result field: {field}"
            )

    status = answer_result[
        "status"
    ]

    answer = answer_result[
        "answer"
    ]

    citations = answer_result[
        "citations"
    ]

    generation_used = answer_result[
        "generation_used"
    ]

    if status not in {
        "generated",
        "insufficient_evidence",
    }:
        raise ValueError(
            f"Unsupported answer status: {status}"
        )

    if (
        not isinstance(answer, str)
        or not answer.strip()
    ):
        raise ValueError(
            "answer must be a non-empty string"
        )

    if not isinstance(
        citations,
        list,
    ):
        raise TypeError(
            "citations must be a list"
        )

    if not isinstance(
        generation_used,
        bool,
    ):
        raise TypeError(
            "generation_used must be a boolean"
        )

    if status == "generated":
        if not generation_used:
            raise ValueError(
                "generated status requires generation_used=True"
            )

        if not citations:
            raise ValueError(
                "generated status requires citations"
            )

        validate_answer_citations(
            answer=answer,
            citations=citations,
        )

    if status == "insufficient_evidence":
        if generation_used:
            raise ValueError(
                "insufficient_evidence requires generation_used=False"
            )

        if citations:
            raise ValueError(
                "insufficient_evidence must not contain citations"
            )

    return {
        "status": status,
        "citation_validation_passed": True,
        "generation_used": generation_used,
        "citation_count": len(
            citations
        ),
    }
