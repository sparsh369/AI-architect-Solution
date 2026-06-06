"""
Optional FastAPI backend.

Exposes the AI Solution Architect pipeline as a small REST API. The Streamlit
UI works without this (it calls the orchestrator directly), but this backend is
included so the solution is a complete frontend + backend system and so the
pipeline can be consumed by other clients.

Run it with:
    uvicorn backend.main:app --reload --port 8000

Endpoints:
    GET  /health                 -> service + mode status
    POST /analyze                -> {"document": "..."} -> SolutionBlueprint
    POST /analyze/upload         -> multipart file (pdf/txt/md) -> SolutionBlueprint
    POST /report/pdf             -> SolutionBlueprint JSON -> PDF download
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make the project root importable when run as `uvicorn backend.main:app`.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, File, HTTPException, UploadFile  # noqa: E402
from fastapi.responses import Response  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from agents.base import llm_available  # noqa: E402
from orchestrator import generate_blueprint  # noqa: E402
from utils.pdf_utils import read_document  # noqa: E402
from utils.report import build_pdf  # noqa: E402
from utils.schemas import SolutionBlueprint  # noqa: E402

app = FastAPI(
    title="AI Solution Architect Agent",
    description="Turns a client requirement document into a full solution blueprint.",
    version="1.0.0",
)


class AnalyzeRequest(BaseModel):
    document: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "mode": "llm" if llm_available() else "demo",
        "message": "AI Solution Architect Agent is running.",
    }


@app.post("/analyze", response_model=SolutionBlueprint)
def analyze(req: AnalyzeRequest):
    try:
        return generate_blueprint(req.document)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/analyze/upload", response_model=SolutionBlueprint)
async def analyze_upload(file: UploadFile = File(...)):
    raw = await file.read()
    text = read_document(raw, file.filename or "document.txt")
    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from file.")
    return generate_blueprint(text)


@app.post("/report/pdf")
def report_pdf(bp: SolutionBlueprint):
    pdf_bytes = build_pdf(bp)
    name = bp.requirement.project_name.replace(" ", "_") or "solution_blueprint"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{name}.pdf"'},
    )
