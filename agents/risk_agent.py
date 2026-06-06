"""
Step 4 — Risk Analysis Agent.

Identifies delivery / technical / cost / adoption risks with mitigations.
"""
from __future__ import annotations

from agents.base import run_llm_json
from prompts import risk_prompt
from utils.schemas import Architecture, RequirementAnalysis, RiskAnalysis, RiskItem


def _demo_fallback(req: RequirementAnalysis, arch: Architecture) -> RiskAnalysis:
    risks = [
        RiskItem(
            risk="High LLM usage cost at scale",
            impact="High", likelihood="Medium",
            mitigation="Cache frequent responses, use smaller models for simple "
            "tasks, and set per-user rate limits and token budgets.",
        ),
        RiskItem(
            risk="LLM hallucination / inaccurate answers",
            impact="High", likelihood="Medium",
            mitigation="Ground responses with retrieval (RAG), add citations, "
            "and include a human-in-the-loop for sensitive actions.",
        ),
        RiskItem(
            risk="Unclear or evolving requirements",
            impact="Medium", likelihood="High",
            mitigation="Run a short requirement workshop and validate with a "
            "clickable prototype before full build.",
        ),
        RiskItem(
            risk="Integration complexity with external systems",
            impact="Medium", likelihood="Medium",
            mitigation="Confirm API access and credentials early; build thin "
            "adapter layers and mock integrations during development.",
        ),
        RiskItem(
            risk="Data privacy & compliance",
            impact="High", likelihood="Low",
            mitigation="Mask/redact PII, restrict data residency, and review "
            "the data flow with the client's security team.",
        ),
        RiskItem(
            risk="Low user adoption",
            impact="Medium", likelihood="Medium",
            mitigation="Co-design with end users, ship an intuitive UI, and "
            "run a guided pilot with feedback loops.",
        ),
    ]
    # Drop the privacy risk if nothing in scope hints at sensitive data.
    text = (req.business_goal + " ".join(req.constraints) + " ".join(req.key_features)).lower()
    if not any(k in text for k in ["data", "privacy", "secur", "employee", "customer", "patient"]):
        risks = [r for r in risks if "privacy" not in r.risk.lower()]
    return RiskAnalysis(risks=risks)


def run(req: RequirementAnalysis, arch: Architecture) -> RiskAnalysis:
    """Generate a risk register. Falls back to demo mode."""
    data = run_llm_json(
        risk_prompt.SYSTEM,
        risk_prompt.USER_TEMPLATE.format(
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
        return RiskAnalysis(**data)
    except Exception:
        return _demo_fallback(req, arch)
