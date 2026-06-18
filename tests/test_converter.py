import pytest
from app.converter import convert_docx, convert_pdf


def test_convert_docx_returns_text(docx_bytes):
    text = convert_docx(docx_bytes)
    assert isinstance(text, str)
    assert len(text.strip()) > 0


def test_convert_docx_contains_markdown_formatting(docx_bytes):
    text = convert_docx(docx_bytes)
    assert any(marker in text for marker in ("#", "**", "*", "---")), (
        "Expected at least one markdown formatting marker in DOCX output"
    )


def test_convert_pdf_returns_text(pdf_bytes):
    text, _ = convert_pdf(pdf_bytes)
    assert isinstance(text, str)
    assert len(text.strip()) > 0


def test_convert_pdf_not_flagged_as_scanned(pdf_bytes):
    _, is_scanned = convert_pdf(pdf_bytes)
    assert is_scanned is False


def test_convert_docx_returns_empty_on_corrupt_file(invalid_docx_bytes):
    # markitdown handles a JPEG-as-DOCX gracefully rather than raising;
    # the output should be empty rather than meaningful markdown
    text = convert_docx(invalid_docx_bytes)
    assert text.strip() == ""
