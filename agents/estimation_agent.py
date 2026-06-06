"""
Step 3 — Effort Estimation Agent.

Estimates effort in person-days and proposes a team from the requirement and
architecture.
"""
from __future__ import annotations

from agents.base import run_llm_json
from prompts import estimation_prompt
from utils.schemas import (
    Architecture,
    EffortEstimation,
    EffortItem,
    RequirementAnalysis,
    TeamMember,
)


def _demo_fallback(req: RequirementAnalysis, arch: Architecture) -> EffortEstimation:
    """Scale a baseline estimate by feature & integration count."""
    n_features = max(len(req.key_features), 1)
    n_integrations = len([i for i in req.integrations if i.lower() != "none specified"])
    uses_rag = "chroma" in arch.tech_stack.vector_database.lower() or \
        "vector" in arch.tech_stack.vector_database.lower()

    backend = 6 + 1.5 * n_features + 2 * n_integrations
    frontend = 5 + 1.0 * n_features
    ai = 4 + (4 if uses_rag else 1) + 0.5 * n_features

    breakdown = [
        EffortItem(phase="Requirement Analysis", days=3),
        EffortItem(phase="Backend Development", days=round(backend)),
        EffortItem(phase="Frontend Development", days=round(frontend)),
        EffortItem(phase="AI / LLM Integration", days=round(ai)),
        EffortItem(phase="Testing & QA", days=round((backend + frontend + ai) * 0.25)),
        EffortItem(phase="Deployment", days=2),
    ]
    total = sum(i.days for i in breakdown)

    return EffortEstimation(
        breakdown=breakdown,
        total_days=total,
        team=[
            TeamMember(role="AI Engineer", count=1),
            TeamMember(role="Backend Engineer", count=1),
            TeamMember(role="Frontend Engineer", count=1),
            TeamMember(role="QA Engineer", count=1),
        ],
        assumptions=[
            "Estimate assumes a single environment and no major scope changes.",
            "Client provides timely access to data and integration endpoints.",
            "Effort is in person-days for a focused delivery team.",
        ],
    )


def run(req: RequirementAnalysis, arch: Architecture) -> EffortEstimation:
    """Estimate effort + team. Falls back to demo mode."""
    data = run_llm_json(
        estimation_prompt.SYSTEM,
        estimation_prompt.USER_TEMPLATE.format(
            project_name=req.project_name,
            key_features=", ".join(req.key_features),
            integrations=", ".join(req.integrations),
            tech_stack=arch.tech_stack.model_dump(),
            constraints=", ".join(req.constraints),
        ),
    )
    if data is None:
        return _demo_fallback(req, arch)
    try:
        est = EffortEstimation(**data)
        # Keep the total consistent with the breakdown.
        if est.breakdown:
            est.total_days = sum(i.days for i in est.breakdown)
        return est
    except Exception:
        return _demo_fallback(req, arch)
