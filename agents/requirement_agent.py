"""
Step 1 — Requirement Analysis Agent.

Turns a raw requirement document (text extracted from PDF or pasted) into a
structured `RequirementAnalysis`.
"""
from __future__ import annotations

import re

from agents.base import run_llm_json
from prompts import requirement_prompt
from utils.schemas import RequirementAnalysis


# Keyword → integration name, used by the offline demo fallback.
_INTEGRATION_HINTS = {
    "teams": "Microsoft Teams",
    "slack": "Slack",
    "servicenow": "ServiceNow",
    "salesforce": "Salesforce",
    "sap": "SAP",
    "zoho": "Zoho",
    "jira": "Jira",
    "sharepoint": "SharePoint",
    "outlook": "Outlook",
    "whatsapp": "WhatsApp",
    "gmail": "Gmail",
    "sql": "SQL Database",
    "s3": "AWS S3",
}

_FEATURE_HINTS = {
    "search": "Document / Knowledge Search",
    "ticket": "Support Ticket Creation",
    "faq": "FAQ / Q&A",
    "chat": "Conversational Chat Interface",
    "summar": "Document Summarisation",
    "recommend": "Recommendations",
    "report": "Report Generation",
    "dashboard": "Analytics Dashboard",
    "translat": "Translation",
    "voice": "Voice Interface",
    "ocr": "OCR / Document Extraction",
    "predict": "Prediction / Forecasting",
}


def _demo_fallback(document: str) -> RequirementAnalysis:
    """Heuristic analysis so the demo works fully offline."""
    text = document.lower()

    # Project name: first non-empty line, trimmed.
    first_line = next((ln.strip() for ln in document.splitlines() if ln.strip()), "")
    first_line = re.sub(r"^(project|title|subject)\s*[:\-]\s*", "", first_line, flags=re.I)
    project_name = (first_line[:60] or "AI Solution").strip()

    features = sorted({label for key, label in _FEATURE_HINTS.items() if key in text})
    integrations = sorted({label for key, label in _INTEGRATION_HINTS.items() if key in text})

    users = []
    for role in ["employee", "customer", "hr", "admin", "agent", "manager", "student", "patient"]:
        if role in text:
            users.append(role.upper() if len(role) <= 2 else role.capitalize())
    if not users:
        users = ["End Users", "Internal Team"]

    constraints = []
    if "budget" in text:
        constraints.append("Budget sensitivity")
    if "secur" in text or "privacy" in text or "gdpr" in text:
        constraints.append("Data security & privacy")
    if "deadline" in text or "timeline" in text or "month" in text:
        constraints.append("Fixed timeline")
    if not constraints:
        constraints = ["No major constraints specified"]

    return RequirementAnalysis(
        project_name=project_name,
        business_goal="Deliver an AI-powered solution that automates the "
        "described workflow and reduces manual effort.",
        target_users=users,
        key_features=features or ["Core AI Capability", "User Interface", "Integrations"],
        integrations=integrations or ["None specified"],
        constraints=constraints,
        summary=(document.strip()[:280] + "…") if len(document) > 280 else document.strip(),
    )


def run(document: str) -> RequirementAnalysis:
    """Analyse a requirement document. Falls back to demo mode without a key."""
    data = run_llm_json(
        requirement_prompt.SYSTEM,
        requirement_prompt.USER_TEMPLATE.format(document=document[:12000]),
    )
    if data is None:
        return _demo_fallback(document)
    try:
        return RequirementAnalysis(**data)
    except Exception:
        return _demo_fallback(document)
