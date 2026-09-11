import pytest

from src.generation.answer_generator import (
    validate_generated_answer,
    generate_grounded_answer,
)


class FakeLLMClient:
    def __init__(
        self,
        response: str,
    ):
        self.response = response
        self.call_count = 0
        self.last_system_prompt = None
        self.last_user_prompt = None

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        self.call_count += 1
        self.last_system_prompt = (
            system_prompt
        )
        self.last_user_prompt = (
            user_prompt
        )

        return self.response


def build_valid_packet() -> dict:
    return {
        "has_evidence": True,
        "evidence_count": 1,
        "formatted_context": (
            "[EVIDENCE 1]\n"
            "Document ID: DOC-001\n"
            "Title: Operational Escalation Policy\n"
            "Version: 1.0\n"
            "Status: Active\n"
            "Page: 3\n"
            "Chunk ID: DOC-001-V1.0-P003-C002\n"
            "Text:\n"
            "Operational leadership should review "
            "the escalation conditions.\n"
            "[/EVIDENCE 1]"
        ),
        "citations": [
            {
                "chunk_id": "DOC-001-V1.0-P003-C002",
                "document_id": "DOC-001",
                "title": "Operational Escalation Policy",
                "version": "1.0",
                "page": 3,
            }
        ],
    }


def build_empty_packet() -> dict:
    return {
        "has_evidence": False,
        "evidence_count": 0,
        "formatted_context": "",
        "citations": [],
    }


def test_validate_generated_answer_accepts_valid_answer():
    validate_generated_answer(
        "Operational leadership should review the escalation conditions."
    )


def test_validate_generated_answer_rejects_blank_answer():
    with pytest.raises(
        ValueError,
        match="generated answer must be a non-empty string",
    ):
        validate_generated_answer(
            "   "
        )


def test_generate_grounded_answer_calls_model_with_evidence():
    client = FakeLLMClient(
        response=(
            "Answer:\n"
            "Operational leadership should review "
            "the escalation conditions.\n\n"
            "Evidence:\n"
            "The supplied policy supports this action.\n\n"
            "Sources:\n"
            "Operational Escalation Policy, "
            "Version 1.0, Page 3, "
            "Chunk DOC-001-V1.0-P003-C002"
        )
    )

    result = generate_grounded_answer(
        question=(
            "What should operational leadership do?"
        ),
        evidence_packet=build_valid_packet(),
        llm_client=client,
    )

    assert result["status"] == "generated"
    assert result["generation_used"] is True
    assert client.call_count == 1
    assert len(result["citations"]) == 1
    assert result["answer"]


def test_model_receives_system_and_user_prompts():
    client = FakeLLMClient(
        response="Grounded answer."
    )

    generate_grounded_answer(
        question=(
            "What should operational leadership do?"
        ),
        evidence_packet=build_valid_packet(),
        llm_client=client,
    )

    assert client.last_system_prompt
    assert client.last_user_prompt
    assert (
        "APPROVED EVIDENCE:"
        in client.last_user_prompt
    )


def test_generate_grounded_answer_does_not_call_model_without_evidence():
    client = FakeLLMClient(
        response="This should never be used."
    )

    result = generate_grounded_answer(
        question=(
            "What medication should be prescribed?"
        ),
        evidence_packet=build_empty_packet(),
        llm_client=client,
    )

    assert (
        result["status"]
        == "insufficient_evidence"
    )
    assert result[
        "generation_used"
    ] is False
    assert client.call_count == 0
    assert result["citations"] == []


def test_generate_requires_client_when_evidence_exists():
    with pytest.raises(
        ValueError,
        match="llm_client is required",
    ):
        generate_grounded_answer(
            question=(
                "What should operational leadership do?"
            ),
            evidence_packet=build_valid_packet(),
            llm_client=None,
        )
