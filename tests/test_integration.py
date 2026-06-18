"""
Browser integration tests using Playwright.

Requirements:
    pip install playwright && playwright install chromium

These tests are skipped automatically if playwright is not installed.
They require the app to be running at http://localhost:8080 (docker compose up).
"""

from pathlib import Path
import pytest

pytest.importorskip("playwright", reason="playwright not installed — skipping browser integration tests")

from playwright.sync_api import sync_playwright  # noqa: E402

TESTS_DIR = Path(__file__).parent
BASE_URL = "http://localhost:8080"


@pytest.fixture(scope="session", autouse=True)
def require_server():
    import httpx
    try:
        httpx.get(BASE_URL, timeout=3)
    except Exception:
        pytest.skip("App not reachable at http://localhost:8080 — start with: docker compose up")


def test_page_loads():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(BASE_URL)
        assert "docx / pdf" in page.title()
        browser.close()


def test_drop_zone_visible():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(BASE_URL)
        assert page.locator("#dropZone").is_visible()
        browser.close()


def test_unsupported_file_shows_error_toast():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(BASE_URL)
        page.set_input_files("#fileInput", str(TESTS_DIR / "peter-thomas-CHXBk2102ac-unsplash.jpg"))
        toast = page.locator(".toast.error")
        toast.wait_for(state="visible", timeout=4000)
        assert "supported" in toast.text_content().lower()
        browser.close()


def test_multiple_files_shows_error_toast():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(BASE_URL)
        # Synthesize a drop event with two files via JS DataTransfer
        page.evaluate("""() => {
            const dt = new DataTransfer();
            const f1 = new File(['a'], 'a.pdf', { type: 'application/pdf' });
            const f2 = new File(['b'], 'b.pdf', { type: 'application/pdf' });
            dt.items.add(f1);
            dt.items.add(f2);
            const zone = document.getElementById('dropZone');
            zone.dispatchEvent(new DragEvent('drop', { dataTransfer: dt, bubbles: true }));
        }""")
        toast = page.locator(".toast.error")
        toast.wait_for(state="visible", timeout=4000)
        assert "one file" in toast.text_content().lower()
        browser.close()


def test_docx_triggers_download():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(BASE_URL)
        with page.expect_download(timeout=15000) as dl:
            page.set_input_files("#fileInput", str(TESTS_DIR / "docx-markdown-style-test.docx"))
        assert dl.value.suggested_filename.endswith(".md")
        browser.close()


def test_pdf_triggers_download():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(BASE_URL)
        with page.expect_download(timeout=15000) as dl:
            page.set_input_files("#fileInput", str(TESTS_DIR / "pdf-markdown-style-test.pdf"))
        assert dl.value.suggested_filename.endswith(".md")
        browser.close()
