"""
Step 5 — Proposal Generation Agent.

Synthesises every prior step into a client-ready proposal.
"""
from __future__ import annotations

from agents.base import run_llm_json
from prompts import proposal_prompt
from utils.schemas import (
    Architecture,
    EffortEstimation,
    Proposal,
    RequirementAnalysis,
    RiskAnalysis,
)


def _team_to_str(est: EffortEstimation) -> str:
    return ", ".join(f"{m.count} {m.role}" for m in est.team) or "Lean delivery team"


def _demo_fallback(req: RequirementAnalysis, arch: Architecture,
                   est: EffortEstimation, risk: RiskAnalysis) -> Proposal:
    weeks = max(round(est.total_days / 5), 1)
    return Proposal(
        executive_summary=(
            f"We propose to build {req.project_name}, an AI-powered solution that "
            f"{req.business_goal.lower().rstrip('.')}. The solution can be "
            f"delivered in approximately {est.total_days:.0f} working days "
            f"(~{weeks} weeks) by a focused expert team."
        ),
        recommended_solution=(
            f"{arch.overview} The stack centres on {arch.tech_stack.llm} "
            f"orchestrated via {arch.tech_stack.ai_framework}, with a "
            f"{arch.tech_stack.backend} backend and a "
            f"{arch.tech_stack.frontend} frontend, deployed on "
            f"{arch.tech_stack.deployment}."
        ),
        timeline=f"Approximately {est.total_days:.0f} person-days (~{weeks} weeks) "
        "across analysis, build, testing and deployment.",
        team_structure=_team_to_str(est),
        assumptions=est.assumptions,
        risks=[f"{r.risk} — mitigated by {r.mitigation.lower()}" for r in risk.risks[:4]],
        next_steps=[
            "Confirm scope and success criteria in a kickoff workshop.",
            "Provision access to data sources and integration endpoints.",
            "Build a prototype of the core flow for early feedback.",
            "Agree commercial terms and sign off on the delivery plan.",
        ],
    )


def run(req: RequirementAnalysis, arch: Architecture,
        est: EffortEstimation, risk: RiskAnalysis) -> Proposal:
    """Generate the proposal. Falls back to demo mode."""
    data = run_llm_json(
        proposal_prompt.SYSTEM,
        proposal_prompt.USER_TEMPLATE.format(
            project_name=req.project_name,
            business_goal=req.business_goal,
            target_users=", ".join(req.target_users),
            key_features=", ".join(req.key_features),
            architecture_overview=arch.overview,
            tech_stack=arch.tech_stack.model_dump(),
            total_days=est.total_days,
            team=_team_to_str(est),
            risks=", ".join(r.risk for r in risk.risks[:5]),
        ),
    )
    if data is None:
        return _demo_fallback(req, arch, est, risk)
    try:
        return Proposal(**data)
    except Exception:
        return _demo_fallback(req, arch, est, risk)
