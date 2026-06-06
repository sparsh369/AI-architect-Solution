"""
Generate a mentor-ready explainer PDF for the AI Solution Architect Agent.

Run:  python make_explainer_pdf.py
Output: AI_Solution_Architect_Explainer.pdf
"""
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

BRAND = colors.HexColor("#1d4ed8")
BRAND_DARK = colors.HexColor("#1e3a8a")
LIGHT = colors.HexColor("#eef2ff")
GREY = colors.HexColor("#64748b")
ROWALT = colors.HexColor("#f8fafc")

styles = getSampleStyleSheet()

H_TITLE = ParagraphStyle("HTitle", parent=styles["Title"], fontSize=26,
                         textColor=BRAND, spaceAfter=6, leading=30)
H_SUB = ParagraphStyle("HSub", parent=styles["Normal"], fontSize=12.5,
                       textColor=GREY, alignment=TA_CENTER, spaceAfter=4)
H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=15,
                    textColor=BRAND_DARK, spaceBefore=14, spaceAfter=6)
H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=12,
                    textColor=colors.black, spaceBefore=8, spaceAfter=4)
BODY = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10.5,
                      leading=15, spaceAfter=6)
SMALL = ParagraphStyle("Small", parent=styles["Normal"], fontSize=9.5,
                       leading=13, textColor=GREY)
CELL = ParagraphStyle("Cell", parent=styles["Normal"], fontSize=9.5, leading=13)
CELL_B = ParagraphStyle("CellB", parent=CELL, fontName="Helvetica-Bold")
CELL_W = ParagraphStyle("CellW", parent=CELL, textColor=colors.white,
                        fontName="Helvetica-Bold")
CODE = ParagraphStyle("Code", parent=styles["Normal"], fontName="Courier",
                      fontSize=9, leading=12, backColor=colors.HexColor("#0f172a"),
                      textColor=colors.HexColor("#e2e8f0"), borderPadding=8,
                      leftIndent=2, spaceAfter=6)

story = []


def p(text, style=BODY):
    story.append(Paragraph(text, style))


def bullets(items, style=BODY):
    story.append(ListFlowable(
        [ListItem(Paragraph(i, style), leftIndent=10) for i in items],
        bulletType="bullet", start="•", bulletColor=BRAND, leftIndent=14,
    ))
    story.append(Spacer(1, 4))


def rule():
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#dbe3f0")))
    story.append(Spacer(1, 2))


def table(header, rows, widths):
    data = [[Paragraph(h, CELL_W) for h in header]]
    for r in rows:
        data.append([Paragraph(c, CELL) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), BRAND),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), ROWALT))
    t.setStyle(TableStyle(style))
    story.append(t)
    story.append(Spacer(1, 8))


# ── COVER ─────────────────────────────────────────────────────────────────
story.append(Spacer(1, 1.2 * cm))
p("AI Solution Architect Agent", H_TITLE)
p("Project Explainer &mdash; Logic, Tech Stack &amp; Agent Roles", H_SUB)
p("A fast, mentor-ready walkthrough of what the project does and how it works", H_SUB)
story.append(Spacer(1, 0.4 * cm))
story.append(HRFlowable(width="60%", thickness=1.5, color=BRAND, hAlign="CENTER"))
story.append(Spacer(1, 0.5 * cm))

# One-liner box
box = Table([[Paragraph(
    "<b>In one line:</b> Upload a client requirement (even a messy email or PDF) "
    "and the system returns a complete, structured solution blueprint &mdash; "
    "requirement analysis, architecture, tech stack, effort estimate, risks, and "
    "a client-ready proposal &mdash; in minutes.", BODY)]], colWidths=[16 * cm])
box.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
    ("BOX", (0, 0), (-1, -1), 1, BRAND),
    ("TOPPADDING", (0, 0), (-1, -1), 12),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ("LEFTPADDING", (0, 0), (-1, -1), 14),
    ("RIGHTPADDING", (0, 0), (-1, -1), 14),
]))
story.append(box)
story.append(Spacer(1, 0.5 * cm))

# ── 1. AGENDA / PROBLEM ─────────────────────────────────────────────────
p("1 &middot; The Agenda &mdash; Why This Project Exists", H1)
p("Today, when a client shares a requirement document, presales teams and "
  "solution architects spend <b>hours to days</b> manually doing the same work: "
  "reading the requirement, choosing technologies, estimating effort, drawing "
  "architecture, listing risks, and writing a proposal.", BODY)
p("<b>The goal:</b> automate that entire presales / solution-design process so a "
  "consulting firm (e.g. Algo8) can produce a professional solution blueprint in "
  "minutes instead of hours &mdash; cutting cost and turnaround time.", BODY)
p("<b>Who uses it:</b> Presales teams, Solution Architects, Delivery Managers, "
  "and Technical Consultants.", BODY)

rule()

# ── 2. HOW IT WORKS ─────────────────────────────────────────────────────
p("2 &middot; How It Works &mdash; The Core Idea", H1)
p("The system is a <b>lightweight pipeline of 5 specialised agents</b> that run "
  "one after another. Each agent is an expert at one job and passes its output to "
  "the next. There is no complex multi-agent orchestration &mdash; just a clean, "
  "explainable sequence.", BODY)
p("<b>Unstructured in -&gt; Structured out.</b> The first agent uses GPT-4o to "
  "turn ANY messy text (email, notes, PDF) into structured fields. Every later "
  "agent builds on that structure.", BODY)

p("The flow:", H2)
flow = Table([[
    Paragraph("Requirement<br/>Document<br/>(PDF / text)", CELL_B),
    Paragraph("-&gt;", H2),
    Paragraph("5 Agents<br/>run in<br/>sequence", CELL_B),
    Paragraph("-&gt;", H2),
    Paragraph("Solution<br/>Blueprint<br/>+ PDF report", CELL_B),
]], colWidths=[3.5 * cm, 1 * cm, 3.5 * cm, 1 * cm, 3.5 * cm])
flow.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (0, 0), LIGHT),
    ("BACKGROUND", (2, 0), (2, 0), LIGHT),
    ("BACKGROUND", (4, 0), (4, 0), LIGHT),
    ("BOX", (0, 0), (0, 0), 1, BRAND),
    ("BOX", (2, 0), (2, 0), 1, BRAND),
    ("BOX", (4, 0), (4, 0), 1, BRAND),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 10),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
]))
story.append(flow)
story.append(Spacer(1, 8))

p("Behind the scenes, a single <b>orchestrator</b> (orchestrator.py) calls each "
  "agent in order and assembles one final object called the "
  "<b>SolutionBlueprint</b>. Both the Streamlit UI and the optional FastAPI "
  "backend use this same orchestrator &mdash; one source of truth.", BODY)

story.append(PageBreak())

# ── 3. THE 5 AGENTS ─────────────────────────────────────────────────────
p("3 &middot; The 5 Agents &mdash; Who Does What", H1)
p("Each agent lives in its own file under <font face='Courier'>agents/</font> and "
  "exposes one <font face='Courier'>run()</font> function.", BODY)

table(
    ["#", "Agent", "Takes In", "Produces"],
    [
        ["1", "<b>Requirement Agent</b><br/>requirement_agent.py",
         "Raw requirement text (from PDF / email / paste)",
         "Project name, business goal, target users, key features, integrations, constraints"],
        ["2", "<b>Architecture Agent</b><br/>architecture_agent.py",
         "The structured requirement",
         "Recommended architecture, full tech stack, and a Mermaid architecture diagram"],
        ["3", "<b>Estimation Agent</b><br/>estimation_agent.py",
         "Requirement + architecture",
         "Effort per phase (person-days), total, and the recommended team structure"],
        ["4", "<b>Risk Agent</b><br/>risk_agent.py",
         "Requirement + architecture",
         "A risk register: each risk with impact, likelihood, and a mitigation"],
        ["5", "<b>Proposal Agent</b><br/>proposal_agent.py",
         "All of the above combined",
         "Client-ready proposal: executive summary, solution, timeline, assumptions, next steps"],
    ],
    [0.8 * cm, 4.2 * cm, 4.5 * cm, 6.5 * cm],
)

p("<b>Key design detail:</b> every agent first tries GPT-4o; if that fails or no "
  "API key is set, it falls back to a built-in rule-based generator so the demo "
  "<i>never breaks</i>. (See section 6: Two Modes.)", SMALL)

rule()

# ── 4. TECH STACK ───────────────────────────────────────────────────────
p("4 &middot; Tech Stack &mdash; What We Use &amp; Why", H1)
table(
    ["Layer", "Technology", "Why we chose it"],
    [
        ["Frontend / UI", "<b>Streamlit</b>",
         "Builds a clean, modern single-page web UI in pure Python &mdash; no HTML/JS needed. Perfect for fast demos."],
        ["Backend (optional API)", "<b>FastAPI</b>",
         "Lightweight, fast Python web framework. Exposes the pipeline as REST endpoints for other apps."],
        ["AI Framework", "<b>LangChain</b>",
         "Standard toolkit to talk to LLMs cleanly &mdash; manages prompts and model calls."],
        ["LLM (the brain)", "<b>OpenAI GPT-4o</b>",
         "Does the actual understanding: reads messy text and reasons about architecture, effort, and risks."],
        ["PDF input", "<b>PyPDF</b>",
         "Extracts text from uploaded requirement PDFs."],
        ["PDF output", "<b>fpdf2</b>",
         "Generates the downloadable solution-blueprint report."],
        ["Data models", "<b>Pydantic</b>",
         "Defines a typed contract for every agent's output &mdash; keeps data clean and predictable."],
        ["Diagram", "<b>Mermaid</b>",
         "Text-based diagrams &mdash; the architecture diagram is generated as code and rendered in the browser."],
    ],
    [3.3 * cm, 3.2 * cm, 9.5 * cm],
)
p("<b>Deliberately kept simple:</b> no authentication, no Docker, no Kubernetes, "
  "no cloud setup &mdash; so it is easy to run locally and easy to explain.", SMALL)

story.append(PageBreak())

# ── 5. CODE STRUCTURE ───────────────────────────────────────────────────
p("5 &middot; Code Structure &mdash; The Key Files", H1)
table(
    ["File / Folder", "What it does"],
    [
        ["<font face='Courier'>app.py</font>",
         "The Streamlit UI &mdash; upload box, the 9 result sections, and download buttons."],
        ["<font face='Courier'>orchestrator.py</font>",
         "The 'conductor'. Runs all 5 agents in order and builds the final SolutionBlueprint."],
        ["<font face='Courier'>agents/</font>",
         "The 5 agent files (+ base.py, which holds the shared LLM connection and demo-mode logic)."],
        ["<font face='Courier'>prompts/</font>",
         "One prompt template per agent &mdash; the instructions we give GPT-4o. Easy to read and tune."],
        ["<font face='Courier'>utils/schemas.py</font>",
         "Pydantic data models &mdash; the typed shape of every agent's output."],
        ["<font face='Courier'>utils/pdf_utils.py</font>",
         "Reads text out of uploaded PDF / TXT / MD files."],
        ["<font face='Courier'>utils/mermaid.py</font>",
         "Builds the architecture diagram as Mermaid code."],
        ["<font face='Courier'>utils/report.py</font>",
         "Exports the final blueprint as a downloadable PDF and Markdown."],
        ["<font face='Courier'>backend/main.py</font>",
         "Optional FastAPI REST API (the UI works without it)."],
        ["<font face='Courier'>sample/</font>",
         "A ready-made sample requirement so you can demo instantly."],
    ],
    [4.8 * cm, 11.2 * cm],
)

rule()

# ── 6. TWO MODES ────────────────────────────────────────────────────────
p("6 &middot; Two Modes &mdash; GPT-4o vs Demo", H1)
bullets([
    "<b>GPT-4o mode</b> (an OpenAI API key is set in the .env file): real LLM "
    "intelligence &mdash; handles messy, unstructured input and produces tailored output.",
    "<b>Demo mode</b> (no key): each agent falls back to smart keyword-based rules, "
    "so the app still produces a full blueprint completely offline &mdash; ideal for a "
    "guaranteed workshop demo.",
])
p("The app shows a banner at the top telling you which mode is active.", SMALL)

rule()

# ── 7. HOW TO RUN ───────────────────────────────────────────────────────
p("7 &middot; How To Run It", H1)
p("1) Activate the environment and start the app:", BODY)
p("cd AI_Architect_Solution<br/>.venv\\Scripts\\activate<br/>streamlit run app.py", CODE)
p("2) Open <b>http://localhost:8501</b> -&gt; paste a requirement (or click "
  "<i>Load sample</i>) -&gt; click <b>Generate Solution Blueprint</b> -&gt; "
  "download the PDF.", BODY)

story.append(PageBreak())

# ── 8. TALK TRACK ───────────────────────────────────────────────────────
p("8 &middot; 2-Minute Talk Track for Your Mentor", H1)
p("Use this script to explain the project confidently:", BODY)

bullets([
    "<b>The problem:</b> 'Presales teams spend hours turning a client requirement "
    "into a proposal. I automated that.'",
    "<b>The idea:</b> 'You upload any requirement &mdash; even a messy email &mdash; "
    "and my system returns a full structured solution blueprint in minutes.'",
    "<b>How:</b> 'It's a pipeline of 5 specialised agents. Each does one job and "
    "feeds the next, coordinated by a single orchestrator.'",
    "<b>The 5 agents:</b> 'Requirement -&gt; Architecture -&gt; Estimation "
    "-&gt; Risk -&gt; Proposal. The first one uses GPT-4o to convert unstructured "
    "text into structured data; the rest build on it.'",
    "<b>The tech:</b> 'Streamlit for the UI, FastAPI for the API, LangChain + "
    "GPT-4o for the AI, PyPDF to read PDFs, fpdf2 to generate the report, and "
    "Pydantic to keep the data clean.'",
    "<b>The smart bit:</b> 'Every agent has a fallback, so the demo works even "
    "without an internet connection or API key.'",
    "<b>The output:</b> 'On screen you see requirement analysis, an architecture "
    "diagram, the tech stack, effort &amp; team, a risk table, and a proposal "
    "&mdash; all downloadable as a PDF.'",
])

rule()
p("End of explainer &mdash; AI Solution Architect Agent", SMALL)


# ── BUILD ───────────────────────────────────────────────────────────────
def _footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#dbe3f0"))
    canvas.line(2 * cm, 1.3 * cm, A4[0] - 2 * cm, 1.3 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GREY)
    canvas.drawString(2 * cm, 0.9 * cm, "AI Solution Architect Agent  -  Project Explainer")
    canvas.drawRightString(A4[0] - 2 * cm, 0.9 * cm, f"Page {doc.page}")
    canvas.restoreState()


doc = SimpleDocTemplate(
    "AI_Solution_Architect_Explainer.pdf", pagesize=A4,
    leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.6 * cm, bottomMargin=1.8 * cm,
    title="AI Solution Architect Agent - Project Explainer",
)
doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
print("OK -> AI_Solution_Architect_Explainer.pdf")
