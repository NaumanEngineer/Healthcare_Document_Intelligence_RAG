from src.ingestion.load_documents import validate_pdf_path


def test_rejects_non_pdf_file(tmp_path):
    test_file = tmp_path / "example.txt"
    test_file.write_text("test")

    try:
        validate_pdf_path(test_file)
        assert False, "Expected ValueError"
    except ValueError:
        assert True


from src.preprocessing.clean_text import clean_text


def test_clean_text_reduces_extra_spaces():
    raw = "Operational   escalation   requires review."
    cleaned = clean_text(raw)

    assert cleaned == "Operational escalation requires review."


def test_clean_text_reduces_excess_blank_lines():
    raw = "Section one\n\n\n\nSection two"
    cleaned = clean_text(raw)

    assert cleaned == "Section one\n\nSection two"


def test_clean_text_handles_empty_string():
    assert clean_text("") == ""

def test_clean_text_preserves_policy_meaning():
    raw = "OPEL 4 requires executive review."
    cleaned = clean_text(raw)

    assert "OPEL 4" in cleaned
    assert "executive review" in cleaned
