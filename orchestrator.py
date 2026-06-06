"""
Pipeline orchestrator.

This is the heart of the system: it runs the five specialised agents in
sequence, feeding each one the outputs of the previous steps, and assembles a
single `SolutionBlueprint`. Both the Streamlit UI and the FastAPI backend call
into here, so there is exactly one source of truth for the workflow.

The optional `on_step` callback lets the UI show live progress.
"""
from __future__ import annotations

from typing import Callable, Optional

from agents import (
    architecture_agent,
    estimation_agent,
    proposal_agent,
    requirement_agent,
    risk_agent,
)
from agents.base import llm_available
from utils.schemas import SolutionBlueprint

ProgressCallback = Optional[Callable[[str, int, int], None]]

_STEPS_TOTAL = 5


def generate_blueprint(document: str, on_step: ProgressCallback = None) -> SolutionBlueprint:
    """Run the full presales pipeline over a requirement document."""

    def _tick(label: str, n: int):
        if on_step:
            on_step(label, n, _STEPS_TOTAL)

    if not document or not document.strip():
        raise ValueError("Requirement document is empty.")

    _tick("Analysing requirements", 1)
    requirement = requirement_agent.run(document)

    _tick("Designing architecture", 2)
    architecture = architecture_agent.run(requirement)

    _tick("Estimating effort", 3)
    estimation = estimation_agent.run(requirement, architecture)

    _tick("Analysing risks", 4)
    risk = risk_agent.run(requirement, architecture)

    _tick("Writing proposal", 5)
    proposal = proposal_agent.run(requirement, architecture, estimation, risk)

    return SolutionBlueprint(
        requirement=requirement,
        architecture=architecture,
        estimation=estimation,
        risk=risk,
        proposal=proposal,
        generated_with_llm=llm_available(),
    )
