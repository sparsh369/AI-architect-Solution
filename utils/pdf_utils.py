"""
PDF / text extraction helpers (PyPDF).
"""
from __future__ import annotations

import io
from typing import Union


def extract_text_from_pdf(source: Union[str, bytes, io.BytesIO]) -> str:
    """
    Extract plain text from a PDF.

    `source` may be a file path, raw bytes, or a file-like object (e.g. a
    Streamlit UploadedFile or FastAPI UploadFile stream).
    """
    from pypdf import PdfReader

    if isinstance(source, (bytes, bytearray)):
        source = io.BytesIO(source)

    reader = PdfReader(source)
    chunks = []
    for page in reader.pages:
        try:
            chunks.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(chunks).strip()


def read_document(file_bytes: bytes, filename: str) -> str:
    """Dispatch on file extension: PDF via PyPDF, everything else as UTF-8 text."""
    if filename.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    return file_bytes.decode("utf-8", errors="ignore").strip()
