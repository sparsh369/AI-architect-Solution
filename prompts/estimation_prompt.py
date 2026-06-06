"""Step 3 — Effort Estimation Agent prompts."""

SYSTEM = """You are an experienced Delivery Manager at an AI consulting firm.
You produce realistic effort estimates (in person-days) and recommend a lean
team structure for AI/software projects. Base estimates on the feature set and
integrations — more features and integrations mean more effort.
Always respond with ONLY a valid JSON object — no markdown, no commentary."""

USER_TEMPLATE = """Estimate the delivery effort for this project.

PROJECT NAME: {project_name}
KEY FEATURES: {key_features}
INTEGRATIONS: {integrations}
TECH STACK: {tech_stack}
CONSTRAINTS: {constraints}

Return a JSON object with exactly these keys:
{{
  "breakdown": [
    {{"phase": "Requirement Analysis", "days": 3}},
    {{"phase": "Backend Development", "days": 10}},
    {{"phase": "Frontend Development", "days": 8}},
    {{"phase": "AI / LLM Integration", "days": 6}},
    {{"phase": "Testing & QA", "days": 5}},
    {{"phase": "Deployment", "days": 2}}
  ],
  "total_days": 34,
  "team": [
    {{"role": "AI Engineer", "count": 1}},
    {{"role": "Backend Engineer", "count": 1}},
    {{"role": "Frontend Engineer", "count": 1}},
    {{"role": "QA Engineer", "count": 1}}
  ],
  "assumptions": ["key assumptions behind this estimate"]
}}

Make total_days equal the sum of the breakdown days. Tailor the phases and team
to the actual scope — do not just copy the example numbers."""
