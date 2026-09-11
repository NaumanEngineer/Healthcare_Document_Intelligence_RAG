from __future__ import annotations

from src.generation.evidence_formatter import (
    build_evidence_packet,
)

from src.generation.answer_generator import (
    generate_grounded_answer,
)

from src.evaluation.answer_qa import (
    validate_answer_result,
)


class DemoLLMClient:
    """
    Deterministic local demo client.

    This is not a production model.
    It lets us test the complete answer-generation flow
    without depending on an external API.
    """

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        return (
            "Answer:\n"
            "Operational leadership should review the current "
            "escalation conditions and follow the actions defined "
            "in the approved operational policy.\n\n"
            "Evidence:\n"
            "The supplied policy evidence supports escalation review "
            "by operational leadership.\n\n"
            "Sources:\n"
            "Operational Escalation Policy, Version 1.0, "
            "Page 3, Chunk DOC-001-V1.0-P003-C002."
        )


def build_demo_evidence() -> list[dict]:
    """
    Build deterministic evidence for the local demo.
    """

    return [
        {
            "chunk_id": "DOC-001-V1.0-P003-C002",
            "document_id": "DOC-001",
            "title": "Operational Escalation Policy",
            "version": "1.0",
            "status": "Active",
            "page": 3,
            "text": (
                "Operational leadership should review "
                "current escalation conditions and apply "
                "the actions defined in the escalation procedure."
            ),
            "source_file": "operational_escalation_policy.pdf",
        }
    ]


def run_demo() -> dict:
    """
    Run the complete grounded-answer demo.
    """

    question = (
        "What should operational leadership do "
        "during escalation?"
    )

    evidence = build_demo_evidence()

    evidence_packet = build_evidence_packet(
        evidence
    )

    client = DemoLLMClient()

    answer_result = generate_grounded_answer(
        question=question,
        evidence_packet=evidence_packet,
        llm_client=client,
    )

    qa_result = validate_answer_result(
        answer_result
    )

    return {
        "question": question,
        "answer_result": answer_result,
        "qa_result": qa_result,
    }


if __name__ == "__main__":
    result = run_demo()

    print(
        "QUESTION:"
    )
    print(
        result["question"]
    )

    print(
        "\nANSWER:"
    )
    print(
        result["answer_result"]["answer"]
    )

    print(
        "\nQA:"
    )
    print(
        result["qa_result"]
    )
