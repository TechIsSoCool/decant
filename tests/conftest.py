from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app

TESTS_DIR = Path(__file__).parent


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture(scope="session")
def docx_bytes():
    return (TESTS_DIR / "docx-markdown-style-test.docx").read_bytes()


@pytest.fixture(scope="session")
def pdf_bytes():
    return (TESTS_DIR / "pdf-markdown-style-test.pdf").read_bytes()


@pytest.fixture(scope="session")
def invalid_docx_bytes():
    return (TESTS_DIR / "jpg-renamed-as-docx.docx").read_bytes()


@pytest.fixture(scope="session")
def jpg_bytes():
    return (TESTS_DIR / "peter-thomas-CHXBk2102ac-unsplash.jpg").read_bytes()
