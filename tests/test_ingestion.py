from src.ingestion.load_documents import validate_pdf_path


def test_rejects_non_pdf_file(tmp_path):
    test_file = tmp_path / "example.txt"
    test_file.write_text("test")

    try:
        validate_pdf_path(test_file)
        assert False, "Expected ValueError"
    except ValueError:
        assert True
