"""
Mermaid architecture-diagram generator.

`build_mermaid` produces a clean `graph TD` diagram from the recommended
architecture. It is used both as the demo fallback and to backfill a diagram
when the LLM omits one.
"""
from __future__ import annotations

import re

from utils.schemas import Architecture, RequirementAnalysis


def _node_id(label: str) -> str:
    """Make a Mermaid-safe node id from a label."""
    nid = re.sub(r"[^A-Za-z0-9]", "", label.title())
    return nid or "Node"


def build_mermaid(arch: Architecture, req: RequirementAnalysis) -> str:
    ts = arch.tech_stack
    lines = ["graph TD"]
    lines.append('    User([User])')
    lines.append(f'    Frontend["Frontend<br/>{ts.frontend or "Web UI"}"]')
    lines.append(f'    Backend["Backend<br/>{ts.backend or "API"}"]')
    lines.append(f'    LLM["LLM<br/>{ts.llm or "GPT-4o"}"]')

    lines.append("    User --> Frontend")
    lines.append("    Frontend --> Backend")
    lines.append("    Backend --> LLM")

    has_vector = bool(ts.vector_database) and "not required" not in ts.vector_database.lower()
    if has_vector:
        lines.append(f'    VectorDB[("Vector DB<br/>{ts.vector_database}")]')
        lines.append("    Backend --> VectorDB")

    if ts.database:
        lines.append(f'    Database[("Database<br/>{ts.database}")]')
        lines.append("    Backend --> Database")

    # Integration nodes.
    real_integrations = [
        i for i in req.integrations
        if i.lower() not in ("none specified", "none", "n/a", "")
    ]
    for integ in real_integrations[:5]:
        nid = _node_id(integ)
        lines.append(f'    {nid}["{integ}"]')
        lines.append(f"    Backend --> {nid}")

    # Light styling for readability.
    lines.append("    classDef ext fill:#eef,stroke:#88a,stroke-width:1px;")
    if real_integrations:
        ext_ids = " ".join(_node_id(i) for i in real_integrations[:5])
        lines.append(f"    class {ext_ids} ext;")

    return "\n".join(lines)
