import os
import re
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.converter import convert_docx, convert_pdf

app = FastAPI()

STATIC_DIR = Path(__file__).parent / "static"
MAX_FILE_UPLOAD_SIZE_MB = 100

SUPPORTED_EXTENSIONS = {".docx", ".pdf"}
SUPPORTED_MIME_TYPES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/pdf",
}


@app.post("/convert")
async def convert(file: UploadFile = File(...)):
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS or file.content_type not in SUPPORTED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="unsupported_type")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail="file_too_large")

    stem = Path(filename).stem.lstrip(".")
    stem = re.sub(r'[<>:"/\\|?*]', "_", stem).strip()
    output_filename = (stem or "converted_markdown_file") + ".md"

    try:
        csp_value = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; font-src 'self'; connect-src 'self'; frame-src 'none'; object-src 'none'; base-uri 'self'; form-action 'self';"
        if ext == ".docx":
            markdown = convert_docx(file_bytes)
            return JSONResponse(headers={"Content-Security-Policy": csp_value}, content={"markdown": markdown, "filename": output_filename, "warning": None})

        # PDF
        markdown, is_scanned = convert_pdf(file_bytes)
        warning = "scanned_pdf" if is_scanned else None
        return JSONResponse(headers={"Content-Security-Policy": csp_value}, content={"markdown": markdown, "filename": output_filename, "warning": warning})
    except Exception:
        raise HTTPException(status_code=422, detail="conversion_failed")


app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
