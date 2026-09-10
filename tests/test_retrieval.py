import math

import pytest

from src.retrieval.embeddings import (
    create_text_hash,
    validate_vector,
)


def test_text_hash_is_deterministic():
    text = "Operational escalation guidance."

    first = create_text_hash(text)
    second = create_text_hash(text)

    assert first == second


def test_text_hash_changes_when_text_changes():
    first = create_text_hash(
        "Operational escalation guidance."
    )

    second = create_text_hash(
        "Updated operational escalation guidance."
    )

    assert first != second


def test_empty_text_hash_raises_error():
    with pytest.raises(ValueError):
        create_text_hash("")


def test_valid_vector_passes():
    validate_vector(
        [0.1, 0.2, 0.3]
    )


def test_zero_vector_fails():
    with pytest.raises(ValueError):
        validate_vector(
            [0.0, 0.0, 0.0]
        )


def test_nonfinite_vector_fails():
    with pytest.raises(ValueError):
        validate_vector(
            [0.1, math.inf]
        )


def test_boolean_vector_value_fails():
    with pytest.raises(TypeError):
        validate_vector(
            [0.1, True]
        )
