import tempfile
import os
from markitdown import MarkItDown
from pypdf import PdfReader


def convert_docx(file_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        md = MarkItDown()
        result = md.convert(tmp_path)
        return result.text_content
    finally:
        os.unlink(tmp_path)


def convert_pdf(file_bytes: bytes) -> tuple[str, bool]:
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        reader = PdfReader(tmp_path)
        num_pages = len(reader.pages)

        md = MarkItDown()
        result = md.convert(tmp_path)
        text = result.text_content

        is_scanned = num_pages > 0 and len(text.strip()) < (50 * num_pages)
        return text, is_scanned
    finally:
        os.unlink(tmp_path)
