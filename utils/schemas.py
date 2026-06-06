"""
Pydantic data models shared across every agent.

These give the whole pipeline a single, typed contract: each agent returns one
of these objects, the orchestrator stitches them into a `SolutionBlueprint`,
and both the Streamlit UI and the FastAPI backend consume that same object.
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


# ── Step 1: Requirement Analysis ──────────────────────────────────────────
class RequirementAnalysis(BaseModel):
    project_name: str = Field(default="Untitled Project")
    business_goal: str = ""
    target_users: List[str] = Field(default_factory=list)
    key_features: List[str] = Field(default_factory=list)
    integrations: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    summary: str = ""


# ── Step 2: Architecture ──────────────────────────────────────────────────
class TechStack(BaseModel):
    frontend: str = ""
    backend: str = ""
    llm: str = ""
    ai_framework: str = ""
    vector_database: str = ""
    database: str = ""
    deployment: str = ""
    other: List[str] = Field(default_factory=list)


class Architecture(BaseModel):
    overview: str = ""
    tech_stack: TechStack = Field(default_factory=TechStack)
    components: List[str] = Field(default_factory=list)
    data_flow: str = ""
    mermaid_diagram: str = ""


# ── Step 3: Effort Estimation ─────────────────────────────────────────────
class EffortItem(BaseModel):
    phase: str
    days: float


class TeamMember(BaseModel):
    role: str
    count: int = 1


class EffortEstimation(BaseModel):
    breakdown: List[EffortItem] = Field(default_factory=list)
    total_days: float = 0
    team: List[TeamMember] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)


# ── Step 4: Risk Analysis ─────────────────────────────────────────────────
class RiskItem(BaseModel):
    risk: str
    impact: str = "Medium"      # Low | Medium | High
    likelihood: str = "Medium"  # Low | Medium | High
    mitigation: str = ""


class RiskAnalysis(BaseModel):
    risks: List[RiskItem] = Field(default_factory=list)


# ── Step 5: Proposal ──────────────────────────────────────────────────────
class Proposal(BaseModel):
    executive_summary: str = ""
    recommended_solution: str = ""
    timeline: str = ""
    team_structure: str = ""
    assumptions: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)


# ── Final assembled output ────────────────────────────────────────────────
class SolutionBlueprint(BaseModel):
    requirement: RequirementAnalysis
    architecture: Architecture
    estimation: EffortEstimation
    risk: RiskAnalysis
    proposal: Proposal
    generated_with_llm: bool = False
