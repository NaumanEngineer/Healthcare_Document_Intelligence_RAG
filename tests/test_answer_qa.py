import pytest

from src.evaluation.answer_qa import (
    build_allowed_citation_index,
    extract_chunk_ids_from_answer,
    extract_document_ids_from_answer,
    find_unsupported_chunk_ids,
    find_unsupported_document_ids,
    validate_answer_citations,
    validate_answer_result,
)


def build_citations() -> list[dict]:
    return [
        {
            "chunk_id": (
                "DOC-001-V1.0-P003-C002"
            ),
            "document_id": "DOC-001",
            "title": (
                "Operational Escalation Policy"
            ),
            "version": "1.0",
            "page": 3,
        }
    ]


def test_build_allowed_citation_index():
    index = build_allowed_citation_index(
        build_citations()
    )

    assert (
        "DOC-001"
        in index["document_ids"]
    )

    assert (
        "DOC-001-V1.0-P003-C002"
        in index["chunk_ids"]
    )

    assert 3 in index["pages"]


def test_extract_chunk_ids_from_answer():
    answer = (
        "Source: DOC-001-V1.0-P003-C002"
    )

    result = extract_chunk_ids_from_answer(
        answer
    )

    assert result == {
        "DOC-001-V1.0-P003-C002"
    }


def test_extract_document_ids_from_answer():
    answer = (
        "The supporting document is DOC-001."
    )

    result = (
        extract_document_ids_from_answer(
            answer
        )
    )

    assert "DOC-001" in result


def test_supported_chunk_citation_passes():
    unsupported = (
        find_unsupported_chunk_ids(
            answer=(
                "Source: "
                "DOC-001-V1.0-P003-C002"
            ),
            citations=build_citations(),
        )
    )

    assert unsupported == set()


def test_unsupported_chunk_citation_detected():
    unsupported = (
        find_unsupported_chunk_ids(
            answer=(
                "Source: "
                "DOC-999-V1.0-P001-C001"
            ),
            citations=build_citations(),
        )
    )

    assert (
        "DOC-999-V1.0-P001-C001"
        in unsupported
    )


def test_unsupported_document_citation_detected():
    unsupported = (
        find_unsupported_document_ids(
            answer="Source document: DOC-999",
            citations=build_citations(),
        )
    )

    assert "DOC-999" in unsupported


def test_validate_answer_citations_accepts_supported_sources():
    answer = (
        "The operational guidance is supported by "
        "DOC-001 and chunk "
        "DOC-001-V1.0-P003-C002."
    )

    validate_answer_citations(
        answer=answer,
        citations=build_citations(),
    )


def test_validate_answer_citations_rejects_invented_chunk():
    answer = (
        "Source: DOC-999-V1.0-P001-C001"
    )

    with pytest.raises(
        ValueError,
        match="Unsupported chunk citation",
    ):
        validate_answer_citations(
            answer=answer,
            citations=build_citations(),
        )


def test_validate_generated_answer_result():
    answer_result = {
        "status": "generated",
        "answer": (
            "Operational leadership should review "
            "the escalation conditions. "
            "Source: DOC-001, "
            "DOC-001-V1.0-P003-C002."
        ),
        "citations": build_citations(),
        "generation_used": True,
    }

    qa = validate_answer_result(
        answer_result
    )

    assert qa[
        "citation_validation_passed"
    ] is True

    assert qa["citation_count"] == 1


def test_validate_insufficient_evidence_result():
    answer_result = {
        "status": (
            "insufficient_evidence"
        ),
        "answer": (
            "The available operational evidence "
            "is insufficient to answer this "
            "question reliably."
        ),
        "citations": [],
        "generation_used": False,
    }

    qa = validate_answer_result(
        answer_result
    )

    assert qa[
        "citation_validation_passed"
    ] is True

    assert qa["citation_count"] == 0


def test_insufficient_evidence_cannot_have_citations():
    answer_result = {
        "status": (
            "insufficient_evidence"
        ),
        "answer": (
            "The available evidence is insufficient."
        ),
        "citations": build_citations(),
        "generation_used": False,
    }

    with pytest.raises(
        ValueError,
        match=(
            "insufficient_evidence "
            "must not contain citations"
        ),
    ):
        validate_answer_result(
            answer_result
        )
