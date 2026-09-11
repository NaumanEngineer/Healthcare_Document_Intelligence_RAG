from __future__ import annotations

from typing import Protocol

from src.generation.prompt_builder import (
    build_grounded_prompt,
)


class LLMClient(Protocol):
    """
    Minimal interface required from any language-model client.

    This keeps generation logic independent from a specific
    provider such as Azure OpenAI or another model API.
    """

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        ...


def validate_generated_answer(
    answer: str,
) -> None:
    """
    Validate a model-generated answer.
    """

    if (
        not isinstance(answer, str)
        or not answer.strip()
    ):
        raise ValueError(
            "generated answer must be a non-empty string"
        )


def generate_grounded_answer(
    question: str,
    evidence_packet: dict,
    llm_client: LLMClient,
) -> dict:
    """
    Generate a grounded answer from validated evidence.

    If the evidence packet is empty, the LLM is not called.

    Returns a structured result containing:

    - status
    - answer
    - citations
    - generation_used
    """

    prompt_package = build_grounded_prompt(
        question=question,
        evidence_packet=evidence_packet,
    )

    if not prompt_package[
        "should_generate"
    ]:
        return {
            "status": "insufficient_evidence",
            "answer": prompt_package[
                "fallback_response"
            ],
            "citations": [],
            "generation_used": False,
        }

    if llm_client is None:
        raise ValueError(
            "llm_client is required when evidence is available"
        )

    answer = llm_client.generate(
        system_prompt=prompt_package[
            "system_prompt"
        ],
        user_prompt=prompt_package[
            "user_prompt"
        ],
    )

    validate_generated_answer(
        answer
    )

    return {
        "status": "generated",
        "answer": answer.strip(),
        "citations": prompt_package[
            "citations"
        ],
        "generation_used": True,
    }
