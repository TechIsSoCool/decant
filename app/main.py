import os
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.converter import convert_docx, convert_pdf

app = FastAPI()

STATIC_DIR = Path(__file__).parent / "static"

SUPPORTED_EXTENSIONS = {".docx", ".pdf"}
SUPPORTED_MIME_TYPES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/pdf",
}


@app.post("/convert")
async def convert(file: UploadFile = File(...)):
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="unsupported_type")

    file_bytes = await file.read()
    stem = Path(filename).stem
    output_filename = stem + ".md"

    if ext == ".docx":
        markdown = convert_docx(file_bytes)
        return JSONResponse({"markdown": markdown, "filename": output_filename, "warning": None})

    # PDF
    markdown, is_scanned = convert_pdf(file_bytes)
    warning = "scanned_pdf" if is_scanned else None
    return JSONResponse({"markdown": markdown, "filename": output_filename, "warning": warning})


app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
