from src.generation.demo_pipeline import (
    run_demo,
)


def test_demo_pipeline_runs_end_to_end():
    result = run_demo()

    assert result["question"]

    answer_result = result[
        "answer_result"
    ]

    qa_result = result[
        "qa_result"
    ]

    assert (
        answer_result["status"]
        == "generated"
    )

    assert (
        answer_result["generation_used"]
        is True
    )

    assert answer_result[
        "citations"
    ]

    assert (
        qa_result[
            "citation_validation_passed"
        ]
        is True
    )
