"""
Step 2 — Architecture Agent.

Recommends an architecture + tech stack and produces a Mermaid diagram from a
`RequirementAnalysis`.
"""
from __future__ import annotations

from agents.base import run_llm_json
from prompts import architecture_prompt
from utils.mermaid import build_mermaid
from utils.schemas import Architecture, RequirementAnalysis, TechStack


def _demo_fallback(req: RequirementAnalysis) -> Architecture:
    """Sensible default modern AI stack for the offline demo."""
    needs_rag = any(
        k in " ".join(req.key_features).lower()
        for k in ["search", "faq", "q&a", "summar", "document"]
    )

    tech = TechStack(
        frontend="Streamlit (demo) / React (production)",
        backend="FastAPI (Python)",
        llm="OpenAI GPT-4o",
        ai_framework="LangChain",
        vector_database="ChromaDB" if needs_rag else "Not required",
        database="PostgreSQL",
        deployment="Azure App Service",
        other=["Redis (response caching)", "Application Insights (monitoring)"],
    )

    components = ["Web UI", "API Gateway / Backend", "LLM Orchestration Layer"]
    if needs_rag:
        components += ["Document Ingestion Pipeline", "Vector Store (RAG)"]
    components += ["Relational Database", "Integration Connectors"]

    arch = Architecture(
        overview="A retrieval-augmented architecture: a lightweight frontend "
        "talks to a FastAPI backend that orchestrates GPT-4o via LangChain, "
        "grounding answers in a vector store and persisting state in PostgreSQL."
        if needs_rag else
        "A clean client-server architecture: a lightweight frontend talks to a "
        "FastAPI backend that orchestrates GPT-4o via LangChain and persists "
        "state in PostgreSQL.",
        tech_stack=tech,
        components=components,
        data_flow="User → Frontend → Backend → (Vector DB for context) → LLM → "
        "Backend → Frontend, with PostgreSQL storing application data and "
        "external systems reached through integration connectors.",
        mermaid_diagram="",  # filled in below
    )
    arch.mermaid_diagram = build_mermaid(arch, req)
    return arch


def run(req: RequirementAnalysis) -> Architecture:
    """Generate architecture + tech stack. Falls back to demo mode."""
    data = run_llm_json(
        architecture_prompt.SYSTEM,
        architecture_prompt.USER_TEMPLATE.format(
            project_name=req.project_name,
            business_goal=req.business_goal,
            target_users=", ".join(req.target_users),
            key_features=", ".join(req.key_features),
            integrations=", ".join(req.integrations),
            constraints=", ".join(req.constraints),
        ),
    )
    if data is None:
        return _demo_fallback(req)
    try:
        arch = Architecture(**data)
        # If the model omitted or produced an empty diagram, generate one.
        if not arch.mermaid_diagram.strip():
            arch.mermaid_diagram = build_mermaid(arch, req)
        return arch
    except Exception:
        return _demo_fallback(req)
