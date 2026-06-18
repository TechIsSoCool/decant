from io import BytesIO

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
PDF_MIME = "application/pdf"
JPG_MIME = "image/jpeg"


def test_docx_convert_success(client, docx_bytes):
    response = client.post(
        "/convert",
        files={"file": ("docx-markdown-style-test.docx", BytesIO(docx_bytes), DOCX_MIME)},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "docx-markdown-style-test.md"
    assert len(data["markdown"]) > 0
    assert data["warning"] is None


def test_pdf_convert_success(client, pdf_bytes):
    response = client.post(
        "/convert",
        files={"file": ("pdf-markdown-style-test.pdf", BytesIO(pdf_bytes), PDF_MIME)},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "pdf-markdown-style-test.md"
    assert len(data["markdown"]) > 0
    assert data["warning"] is None


def test_jpg_rejected(client, jpg_bytes):
    response = client.post(
        "/convert",
        files={"file": ("photo.jpg", BytesIO(jpg_bytes), JPG_MIME)},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "unsupported_type"


def test_mime_mismatch_rejected(client, jpg_bytes):
    # .docx extension but wrong content-type — MIME check should reject it
    response = client.post(
        "/convert",
        files={"file": ("photo.docx", BytesIO(jpg_bytes), JPG_MIME)},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "unsupported_type"


def test_corrupt_docx_returns_empty_markdown(client, invalid_docx_bytes):
    # JPEG renamed as .docx — passes type/MIME check; markitdown handles it
    # gracefully (no exception) but returns empty content
    response = client.post(
        "/convert",
        files={"file": ("corrupt.docx", BytesIO(invalid_docx_bytes), DOCX_MIME)},
    )
    assert response.status_code == 200
    assert response.json()["markdown"].strip() == ""


def test_file_too_large(client):
    big = BytesIO(b"x" * (101 * 1024 * 1024))
    response = client.post(
        "/convert",
        files={"file": ("big.docx", big, DOCX_MIME)},
    )
    assert response.status_code == 413
    assert response.json()["detail"] == "file_too_large"


def test_empty_stem_fallback(client, pdf_bytes):
    # "   .pdf" has suffix=".pdf" and stem="   "; after sanitization stem is empty
    # so the filename should fall back to the default
    response = client.post(
        "/convert",
        files={"file": ("   .pdf", BytesIO(pdf_bytes), PDF_MIME)},
    )
    assert response.status_code == 200
    assert response.json()["filename"] == "converted_markdown_file.md"


def test_csp_header_present(client, pdf_bytes):
    response = client.post(
        "/convert",
        files={"file": ("test.pdf", BytesIO(pdf_bytes), PDF_MIME)},
    )
    assert response.status_code == 200
    assert "Content-Security-Policy" in response.headers
