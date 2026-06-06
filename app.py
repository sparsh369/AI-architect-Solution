"""
AI Solution Architect Agent — Streamlit UI.

A single-page app that turns a client requirement document into a full solution
blueprint: requirement analysis, architecture + Mermaid diagram, tech stack,
effort estimate, risk register, and a client-ready proposal — with one-click
PDF / Markdown download.

Run with:
    streamlit run app.py
"""
from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from agents.base import llm_available
from orchestrator import generate_blueprint
from utils.pdf_utils import read_document
from utils.report import build_markdown, build_pdf

# ── Page config & styling ─────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Solution Architect Agent",
    page_icon="🧩",
    layout="wide",
)

# ── Load secrets on Streamlit Cloud ───────────────────────────────────────
# On Streamlit Community Cloud the OpenAI key is configured via the app's
# Settings -> Secrets (exposed through st.secrets). We copy those values into
# the environment so the rest of the code (which reads os.getenv) works
# unchanged. Locally you can still use a .env file instead — both work.
try:
    for _k in ("OPENAI_API_KEY", "OPENAI_MODEL", "OPENAI_TEMPERATURE"):
        if _k in st.secrets:
            os.environ[_k] = str(st.secrets[_k])
except Exception:
    pass  # no secrets configured (e.g. local run using .env) -> ignore

st.markdown(
    """
    <style>
      .main { background-color: #fbfcfe; }
      .block-container { padding-top: 2rem; max-width: 1200px; }
      .hero {
        background: linear-gradient(110deg, #1d4ed8 0%, #4f46e5 100%);
        color: white; padding: 1.6rem 2rem; border-radius: 16px; margin-bottom: 1.4rem;
      }
      .hero h1 { color: white; margin: 0; font-size: 1.9rem; }
      .hero p  { color: #dbeafe; margin: .35rem 0 0; font-size: 1.02rem; }
      .metric-card {
        background: white; border: 1px solid #e6e8ee; border-radius: 14px;
        padding: 1rem 1.2rem; text-align: center;
      }
      .metric-card .v { font-size: 1.7rem; font-weight: 700; color: #1d4ed8; }
      .metric-card .l { font-size: .82rem; color: #64748b; text-transform: uppercase; letter-spacing:.04em; }
      .pill {
        display:inline-block; background:#eef2ff; color:#3730a3; border-radius:999px;
        padding:.18rem .7rem; margin:.15rem .2rem; font-size:.85rem;
      }
      .section-card {
        background:white; border:1px solid #e6e8ee; border-radius:14px;
        padding:1.2rem 1.4rem; margin-bottom:1rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Helpers ───────────────────────────────────────────────────────────────
def render_mermaid(code: str, height: int = 420):
    """Render a Mermaid diagram via the official CDN."""
    html = f"""
    <div class="mermaid" style="text-align:center;">{code}</div>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
      mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});
    </script>
    """
    components.html(html, height=height, scrolling=True)


def pills(items):
    return " ".join(f'<span class="pill">{i}</span>' for i in items)


SAMPLE_PATH = Path(__file__).parent / "sample" / "sample_requirement.md"


# ── Hero ──────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero">
      <h1>🧩 AI Solution Architect Agent</h1>
      <p>Upload a client requirement and get a complete solution blueprint —
      architecture, tech stack, effort, risks &amp; a proposal — in minutes.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

mode_msg = ("🟢 **GPT-4o mode** — using your OpenAI key."
            if llm_available()
            else "🟡 **Demo mode** — no OpenAI key found; producing realistic sample output. "
                 "Add `OPENAI_API_KEY` to a `.env` file for live LLM generation.")
st.info(mode_msg)


# ── Section 1: Upload / input ─────────────────────────────────────────────
st.subheader("1 · Upload Requirement Document")

col_u, col_t = st.columns([1, 1])
document_text = ""

with col_u:
    uploaded = st.file_uploader("Upload a PDF / TXT / Markdown file", type=["pdf", "txt", "md"])
    if uploaded is not None:
        document_text = read_document(uploaded.getvalue(), uploaded.name)
        st.success(f"Loaded **{uploaded.name}** ({len(document_text):,} characters).")
    if st.button("📄 Load sample requirement", use_container_width=True):
        if SAMPLE_PATH.exists():
            st.session_state["pasted"] = SAMPLE_PATH.read_text(encoding="utf-8")
            st.rerun()

with col_t:
    pasted = st.text_area(
        "…or paste the requirement text",
        value=st.session_state.get("pasted", ""),
        height=220,
        placeholder="Build an AI-powered HR Assistant that can answer employee "
        "questions, search company documents, integrate with Teams, and create "
        "support tickets.",
    )
    if pasted.strip():
        document_text = pasted


# ── Section 2: Generate ───────────────────────────────────────────────────
st.subheader("2 · Generate Solution")
generate = st.button("🚀 Generate Solution Blueprint", type="primary", use_container_width=True)

if generate:
    if not document_text.strip():
        st.error("Please upload a document or paste requirement text first.")
    else:
        progress = st.progress(0.0, text="Starting…")

        def on_step(label, n, total):
            progress.progress(n / total, text=f"Step {n}/{total}: {label}…")

        with st.spinner("Running the agent pipeline…"):
            blueprint = generate_blueprint(document_text, on_step=on_step)
        progress.empty()
        st.session_state["blueprint"] = blueprint
        st.session_state["doc_used"] = document_text
        st.success("Solution blueprint generated!")


# ── Render results ────────────────────────────────────────────────────────
bp = st.session_state.get("blueprint")

if bp:
    r, a, e, k, p = bp.requirement, bp.architecture, bp.estimation, bp.risk, bp.proposal
    ts = a.tech_stack

    # Headline metrics.
    m1, m2, m3, m4 = st.columns(4)
    weeks = max(round(e.total_days / 5), 1)
    headcount = sum(m.count for m in e.team)
    for col, value, label in [
        (m1, f"{e.total_days:g}", "Total Person-Days"),
        (m2, f"~{weeks}", "Weeks"),
        (m3, str(headcount), "Team Size"),
        (m4, str(len(k.risks)), "Risks Identified"),
    ]:
        col.markdown(
            f'<div class="metric-card"><div class="v">{value}</div>'
            f'<div class="l">{label}</div></div>',
            unsafe_allow_html=True,
        )
    st.write("")

    # 3 · Requirement Analysis
    st.subheader("3 · Requirement Analysis")
    with st.container():
        st.markdown(f"### {r.project_name}")
        st.markdown(f"**🎯 Business Goal:** {r.business_goal}")
        st.markdown(f"**👥 Target Users:** {pills(r.target_users)}", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**✨ Key Features**")
            for f in r.key_features:
                st.markdown(f"- {f}")
        with c2:
            st.markdown("**🔌 Integrations**")
            for i in r.integrations:
                st.markdown(f"- {i}")
            st.markdown("**⚠️ Constraints**")
            for c in r.constraints:
                st.markdown(f"- {c}")
        if r.summary:
            st.caption(r.summary)

    # 4 · Architecture Recommendation
    st.subheader("4 · Architecture Recommendation")
    st.markdown(a.overview)
    render_mermaid(a.mermaid_diagram)
    with st.expander("View Mermaid source"):
        st.code(a.mermaid_diagram, language="text")
    cc1, cc2 = st.columns(2)
    with cc1:
        st.markdown("**🧱 Components**")
        for c in a.components:
            st.markdown(f"- {c}")
    with cc2:
        st.markdown("**🔄 Data Flow**")
        st.markdown(a.data_flow)

    # 5 · Tech Stack
    st.subheader("5 · Tech Stack Recommendation")
    stack_rows = [
        ("Frontend", ts.frontend), ("Backend", ts.backend), ("LLM", ts.llm),
        ("AI Framework", ts.ai_framework), ("Vector Database", ts.vector_database),
        ("Database", ts.database), ("Deployment", ts.deployment),
    ]
    cols = st.columns(3)
    for idx, (label, val) in enumerate([x for x in stack_rows if x[1]]):
        with cols[idx % 3]:
            st.markdown(
                f'<div class="section-card"><div class="l" style="color:#64748b;font-size:.8rem">'
                f'{label}</div><div style="font-weight:600;font-size:1.05rem">{val}</div></div>',
                unsafe_allow_html=True,
            )
    if ts.other:
        st.markdown(f"**Other:** {pills(ts.other)}", unsafe_allow_html=True)

    # 6 · Effort Estimation
    st.subheader("6 · Effort Estimation")
    ec1, ec2 = st.columns([2, 1])
    with ec1:
        st.markdown("**Effort by phase (person-days)**")
        chart_data = {item.phase: item.days for item in e.breakdown}
        st.bar_chart(chart_data, horizontal=True, color="#1d4ed8")
    with ec2:
        st.markdown("**Recommended Team**")
        for m in e.team:
            st.markdown(f"- {m.count} × {m.role}")
        st.markdown(f"**Total:** {e.total_days:g} days")
    if e.assumptions:
        with st.expander("Estimation assumptions"):
            for x in e.assumptions:
                st.markdown(f"- {x}")

    # 7 · Risk Analysis
    st.subheader("7 · Risk Analysis")
    risk_table = [
        {"Risk": ri.risk, "Impact": ri.impact, "Likelihood": ri.likelihood,
         "Mitigation": ri.mitigation}
        for ri in k.risks
    ]
    st.dataframe(risk_table, use_container_width=True, hide_index=True)

    # 8 · Proposal Output
    st.subheader("8 · Proposal Output")
    st.markdown(f"**Executive Summary**\n\n{p.executive_summary}")
    st.markdown(f"**Recommended Solution**\n\n{p.recommended_solution}")
    pc1, pc2 = st.columns(2)
    with pc1:
        st.markdown(f"**⏱️ Timeline**\n\n{p.timeline}")
        if p.assumptions:
            st.markdown("**Assumptions**")
            for x in p.assumptions:
                st.markdown(f"- {x}")
    with pc2:
        st.markdown(f"**👥 Team Structure**\n\n{p.team_structure}")
        if p.next_steps:
            st.markdown("**Next Steps**")
            for x in p.next_steps:
                st.markdown(f"- {x}")

    # 9 · Download
    st.subheader("9 · Download Report")
    project_slug = (r.project_name or "solution_blueprint").replace(" ", "_")
    d1, d2 = st.columns(2)
    with d1:
        st.download_button(
            "⬇️ Download PDF Report",
            data=build_pdf(bp),
            file_name=f"{project_slug}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    with d2:
        st.download_button(
            "⬇️ Download Markdown",
            data=build_markdown(bp),
            file_name=f"{project_slug}.md",
            mime="text/markdown",
            use_container_width=True,
        )
else:
    st.caption("👆 Upload or paste a requirement, then click **Generate Solution Blueprint**.")
