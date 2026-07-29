import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (wide layout is critical for correct column sizing)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PR Reviewer — AI Security Review",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS  — ONLY visual styling, zero layout overrides
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── base ── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background: #0D0F14 !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ── block container padding ── */
.block-container { padding: 2rem 3rem 4rem !important; max-width: 100% !important; }

/* ── dividers ── */
hr { border-color: rgba(255,255,255,0.06) !important; margin: 1.5rem 0 !important; }

/* ── Streamlit text overrides ── */
p, li, span, label { color: #CBD5E1 !important; }
h1, h2, h3 { color: #F1F5F9 !important; }

/* ── text_input ── */
div[data-testid="stTextInput"] input {
    background: #161B26 !important;
    border: 1px solid #2D3748 !important;
    border-radius: 8px !important;
    color: #E2E8F0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.875rem !important;
    padding: 10px 14px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #6366F1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    outline: none !important;
}
div[data-testid="stTextInput"] label {
    color: #94A3B8 !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
}

/* ── password input ── */
div[data-testid="stTextInput"] input[type="password"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── primary button ── */
button[kind="primary"],
div[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
    border: none !important;
    border-radius: 8px !important;
    color: #fff !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 10px 20px !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.4) !important;
    transition: opacity 0.15s, transform 0.1s !important;
}
button[kind="primary"]:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }

/* ── secondary / normal button ── */
div[data-testid="stButton"] button {
    background: #1E2535 !important;
    border: 1px solid #2D3748 !important;
    border-radius: 8px !important;
    color: #94A3B8 !important;
    font-weight: 500 !important;
    font-size: 0.84rem !important;
    padding: 8px 16px !important;
    transition: background 0.15s, border-color 0.15s !important;
}
div[data-testid="stButton"] button:hover {
    background: #252D3D !important;
    border-color: #4F5C78 !important;
    color: #E2E8F0 !important;
}

/* ── expander ── */
div[data-testid="stExpander"] {
    background: #161B26 !important;
    border: 1px solid #2D3748 !important;
    border-radius: 10px !important;
}
div[data-testid="stExpander"] summary {
    color: #94A3B8 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 12px 16px !important;
}

/* ── tabs ── */
div[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid #2D3748 !important;
    background: transparent !important;
    gap: 2px !important;
}
div[data-testid="stTabs"] [role="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: #64748B !important;
    padding: 8px 18px !important;
    border-radius: 6px 6px 0 0 !important;
    background: transparent !important;
    border: none !important;
    transition: color 0.15s !important;
}
div[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #E2E8F0 !important;
    background: rgba(99,102,241,0.08) !important;
    border-bottom: 2px solid #6366F1 !important;
}

/* ── code blocks ── */
pre, code {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
    background: #0A0C12 !important;
    border: 1px solid #1E2535 !important;
    border-radius: 8px !important;
    color: #94A3B8 !important;
}

/* ── status widget ── */
div[data-testid="stStatusWidget"] {
    background: #161B26 !important;
    border: 1px solid #2D3748 !important;
    border-radius: 10px !important;
}

/* ── st.caption ── */
div[data-testid="stCaptionContainer"] p { color: #475569 !important; font-size: 0.76rem !important; }

/* ── scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2D3748; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None
if "pr_url" not in st.session_state:
    st.session_state.pr_url = "https://github.com/vjsyam/imageforgerydetector/pull/1"

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS — pure-HTML snippets (display only, no layout)
# ─────────────────────────────────────────────────────────────────────────────
def badge(text: str, color: str, bg: str, border: str) -> str:
    return (
        f'<span style="display:inline-block;font-family:Inter,sans-serif;font-size:0.68rem;'
        f'font-weight:700;text-transform:uppercase;letter-spacing:0.5px;padding:3px 9px;'
        f'border-radius:4px;background:{bg};color:{color};border:1px solid {border};">{text}</span>'
    )

def severity_badge(sev: str) -> str:
    lut = {
        "HIGH":   ("#FCA5A5", "rgba(239,68,68,0.15)",  "rgba(239,68,68,0.35)"),
        "MEDIUM": ("#FCD34D", "rgba(245,158,11,0.12)", "rgba(245,158,11,0.35)"),
        "LOW":    ("#93C5FD", "rgba(59,130,246,0.12)",  "rgba(59,130,246,0.35)"),
    }
    c, bg, b = lut.get(sev.upper(), ("#94A3B8", "rgba(100,116,139,0.1)", "#2D3748"))
    return badge(sev, c, bg, b)

CAT_META = {
    "hardcoded_secret":       ("🔐", "Hardcoded Secret",       "#F59E0B"),
    "sql_injection":          ("💉", "SQL Injection",          "#EF4444"),
    "missing_input_validation":("🛡️","Input Validation",      "#3B82F6"),
    "missing_error_handling": ("⚠️", "Error Handling",         "#8B5CF6"),
}
SEVERITY_BORDER = {"HIGH": "#EF4444", "MEDIUM": "#F59E0B", "LOW": "#3B82F6"}

def finding_card(f: dict) -> str:
    sev   = f.get("severity", "MEDIUM").upper()
    cat   = f.get("category", "")
    icon, label, _ = CAT_META.get(cat, ("🔎", cat.replace("_", " ").title(), "#6366F1"))
    border = SEVERITY_BORDER.get(sev, "#4B5563")
    desc   = f.get("description", "")
    ffile  = f.get("file", "")
    line   = f.get("line", "")
    sug    = f.get("suggestion", "")
    return f"""
<div style="
    background:#161B26;
    border:1px solid #2D3748;
    border-left:3px solid {border};
    border-radius:10px;
    padding:16px 18px;
    margin-bottom:10px;
">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
    <span style="font-size:0.75rem;font-weight:600;color:#64748B;text-transform:uppercase;letter-spacing:0.5px;">
      {icon}&nbsp;&nbsp;{label}
    </span>
    {severity_badge(sev)}
  </div>
  <div style="font-size:0.88rem;color:#CBD5E1;line-height:1.55;margin-bottom:10px;">{desc}</div>
  <code style="font-size:0.75rem;background:rgba(99,102,241,0.1);color:#818CF8;
               border:1px solid rgba(99,102,241,0.2);border-radius:5px;
               padding:2px 8px;">{ffile} : {line}</code>
  <div style="margin-top:10px;font-size:0.8rem;color:#64748B;line-height:1.45;">
    <span style="color:#6366F1;margin-right:6px;">→</span>{sug}
  </div>
</div>"""

def stat_card(value, label: str, color: str = "#E2E8F0") -> None:
    st.markdown(f"""
<div style="background:#161B26;border:1px solid #2D3748;border-radius:10px;
            padding:18px 12px;text-align:center;">
  <div style="font-size:1.8rem;font-weight:800;letter-spacing:-0.5px;color:{color};
              font-family:Inter,sans-serif;">{value}</div>
  <div style="font-size:0.68rem;font-weight:600;color:#475569;text-transform:uppercase;
              letter-spacing:0.6px;margin-top:3px;">{label}</div>
</div>""", unsafe_allow_html=True)

def section_label(text: str) -> None:
    st.markdown(
        f'<p style="font-size:0.7rem;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:1.2px;color:#475569;margin:0 0 8px 0;">{text}</p>',
        unsafe_allow_html=True,
    )

def instr_step(num: str, heading: str, body: str) -> None:
    st.markdown(f"""
<div style="display:flex;gap:12px;align-items:flex-start;margin-bottom:18px;">
  <div style="min-width:26px;height:26px;border-radius:6px;background:rgba(99,102,241,0.12);
              border:1px solid rgba(99,102,241,0.25);color:#818CF8;font-size:0.72rem;
              font-weight:700;display:flex;align-items:center;justify-content:center;
              font-family:Inter,sans-serif;flex-shrink:0;">{num}</div>
  <div>
    <div style="font-size:0.82rem;font-weight:600;color:#CBD5E1;margin-bottom:3px;">{heading}</div>
    <div style="font-size:0.75rem;color:#475569;line-height:1.55;">{body}</div>
  </div>
</div>""", unsafe_allow_html=True)

def flag_row(icon: str, label: str, body: str) -> None:
    st.markdown(f"""
<div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:14px;">
  <span style="font-size:1rem;flex-shrink:0;margin-top:1px;">{icon}</span>
  <div>
    <div style="font-size:0.8rem;font-weight:600;color:#CBD5E1;">{label}</div>
    <div style="font-size:0.74rem;color:#475569;margin-top:2px;">{body}</div>
  </div>
</div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:32px;">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
    <div style="width:8px;height:8px;background:linear-gradient(135deg,#6366F1,#8B5CF6);
                border-radius:50%;flex-shrink:0;"></div>
    <span style="font-size:0.72rem;font-weight:700;text-transform:uppercase;
                 letter-spacing:1.4px;color:#6366F1;font-family:Inter,sans-serif;">
      Multi-Agent AI Code Review
    </span>
  </div>
  <h1 style="font-size:2.4rem;font-weight:800;letter-spacing:-1px;color:#F1F5F9;
             margin:0 0 10px 0;line-height:1.15;font-family:Inter,sans-serif;">
    PR Reviewer Agent Crew
  </h1>
  <p style="font-size:1rem;color:#64748B;max-width:600px;line-height:1.65;margin:0;
            font-family:Inter,sans-serif;">
    Paste any GitHub PR URL. Three AI agents fetch the diff, scan for
    security vulnerabilities, and generate a structured code review — in seconds.
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# TWO-COLUMN LAYOUT  (main 62% | sidebar 38%)
# ─────────────────────────────────────────────────────────────────────────────
main_col, side_col = st.columns([1.65, 1], gap="large")

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR COLUMN — instructions + config
# ══════════════════════════════════════════════════════════════════════════════
with side_col:

    # ── Config ────────────────────────────────────────────────────────────────
    with st.expander("⚙️  API Keys  (optional)", expanded=False):
        github_token = st.text_input(
            "GitHub Token",
            value=os.getenv("GITHUB_TOKEN", ""),
            type="password",
            placeholder="ghp_xxxx — avoids rate limits",
            key="gh_token",
        )
        gemini_key = st.text_input(
            "Gemini API Key",
            value=os.getenv("GEMINI_API_KEY", ""),
            type="password",
            placeholder="AIzaSy... — enables LLM deep review",
            key="gem_key",
        )
        if github_token:
            os.environ["GITHUB_TOKEN"] = github_token
        if gemini_key:
            os.environ["GEMINI_API_KEY"] = gemini_key
        st.caption("Without keys the heuristic scanner runs as fallback. With a Gemini key, LLM semantic analysis activates automatically.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── How to use ────────────────────────────────────────────────────────────
    section_label("How to use")
    instr_step("1", "Paste a GitHub PR URL",
               "Copy the URL of any public GitHub Pull Request.<br>"
               "<code style='font-family:JetBrains Mono,monospace;font-size:0.68rem;"
               "background:#0A0C12;color:#818CF8;padding:1px 5px;border-radius:3px;"
               "border:1px solid #2D3748;'>github.com/owner/repo/pull/N</code>")
    instr_step("2", "Add API keys (optional)",
               "<b style='color:#CBD5E1'>GitHub Token</b> — avoids rate limits.<br>"
               "<b style='color:#CBD5E1'>Gemini Key</b> — enables LLM mode.<br>"
               "Both are optional — heuristic analysis always runs.")
    instr_step("3", "Click Run Review",
               "The 3-node LangGraph pipeline runs:<br>"
               "<code style='font-family:JetBrains Mono,monospace;font-size:0.68rem;"
               "background:#0A0C12;color:#818CF8;padding:1px 5px;border-radius:3px;"
               "border:1px solid #2D3748;'>fetch_pr → review_pr → summarize_pr</code>")
    instr_step("4", "Read the findings",
               "Each finding shows the severity, file &amp; line, plain-English description, and an actionable fix suggestion.")

    st.markdown("---")

    # ── What gets flagged ─────────────────────────────────────────────────────
    section_label("What gets flagged")
    flag_row("🔐", "Hardcoded Secrets",   "API keys, passwords, bearer tokens in plaintext")
    flag_row("💉", "SQL Injection",       "String formatting / concatenation in SQL queries")
    flag_row("🛡️", "Input Validation",   "Unsanitized request params used directly")
    flag_row("⚠️", "Error Handling",     "Bare except: pass and empty catch blocks")

    st.markdown("---")

    # ── Sample PRs ────────────────────────────────────────────────────────────
    section_label("Sample PRs to try")
    st.caption("Click to pre-fill the URL input")

    samples = [
        ("imageforgerydetector #1 — SQLi + bare except",
         "https://github.com/vjsyam/imageforgerydetector/pull/1"),
        ("psf/requests #6700 — public open-source PR",
         "https://github.com/psf/requests/pull/6700"),
    ]
    for label, url in samples:
        if st.button(label, key=f"sample_{url}", use_container_width=True):
            st.session_state.pr_url = url
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# MAIN COLUMN — input + pipeline + results
# ══════════════════════════════════════════════════════════════════════════════
with main_col:

    # ── Pipeline node visualiser ──────────────────────────────────────────────
    result = st.session_state.result
    done   = result is not None and not result.get("error")

    def node_style(active: bool) -> str:
        if active:
            return ("background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.35);"
                    "box-shadow:0 0 12px rgba(16,185,129,0.15);")
        return "background:#161B26;border:1px solid #2D3748;"

    n1, a1, n2, a2, n3 = st.columns([1, 0.3, 1, 0.3, 1])
    with n1:
        st.markdown(f"""
<div style="{node_style(done)}border-radius:10px;padding:14px;text-align:center;">
  <div style="font-size:1.3rem;margin-bottom:4px;">📡</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;
              font-weight:600;color:{'#6EE7B7' if done else '#64748B'};">fetch_pr</div>
</div>""", unsafe_allow_html=True)
    with a1:
        st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:center;height:100%;">
  <div style="height:1px;width:100%;background:{'rgba(16,185,129,0.4)' if done else '#2D3748'};margin-top:4px;"></div>
</div>""", unsafe_allow_html=True)
    with n2:
        st.markdown(f"""
<div style="{node_style(done)}border-radius:10px;padding:14px;text-align:center;">
  <div style="font-size:1.3rem;margin-bottom:4px;">🤖</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;
              font-weight:600;color:{'#6EE7B7' if done else '#64748B'};">review_pr</div>
</div>""", unsafe_allow_html=True)
    with a2:
        st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:center;height:100%;">
  <div style="height:1px;width:100%;background:{'rgba(16,185,129,0.4)' if done else '#2D3748'};margin-top:4px;"></div>
</div>""", unsafe_allow_html=True)
    with n3:
        st.markdown(f"""
<div style="{node_style(done)}border-radius:10px;padding:14px;text-align:center;">
  <div style="font-size:1.3rem;margin-bottom:4px;">📝</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;
              font-weight:600;color:{'#6EE7B7' if done else '#64748B'};">summarize_pr</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── URL Input ─────────────────────────────────────────────────────────────
    section_label("GitHub Pull Request URL")
    url_col, btn_col = st.columns([5, 1])
    with url_col:
        pr_url = st.text_input(
            "pr_url",
            value=st.session_state.pr_url,
            placeholder="https://github.com/owner/repo/pull/42",
            label_visibility="collapsed",
            key="pr_url_field",
        )
    with btn_col:
        run_btn = st.button("Run Review →", type="primary",
                            use_container_width=True, key="run_btn")

    st.caption("Works with any public GitHub PR — authenticated or unauthenticated.")
    st.markdown("<br>", unsafe_allow_html=True)

    # ── EXECUTE PIPELINE ──────────────────────────────────────────────────────
    if run_btn:
        if not pr_url or "github.com" not in pr_url or "/pull/" not in pr_url:
            st.error("Please enter a valid GitHub PR URL — e.g. https://github.com/owner/repo/pull/42")
        else:
            st.session_state.pr_url = pr_url
            with st.status("Running LangGraph pipeline...", expanded=True) as status:
                st.write("**Step 1 / 3** — `fetch_pr`: Fetching PR diff & metadata from GitHub...")

                from graph import pr_review_graph
                from state import PRReviewState

                final_state = pr_review_graph.invoke({"pr_url": pr_url})

                if final_state.get("error"):
                    status.update(label="Pipeline failed", state="error", expanded=True)
                    st.session_state.result = final_state
                else:
                    st.write("**Step 2 / 3** — `review_pr`: Scanning for vulnerabilities...")
                    st.write("**Step 3 / 3** — `summarize_pr`: Generating review report...")
                    status.update(label="Review complete ✓", state="complete", expanded=False)
                    st.session_state.result = final_state

            st.rerun()

    # ── RESULTS ───────────────────────────────────────────────────────────────
    if st.session_state.result:
        res      = st.session_state.result
        findings = res.get("findings", [])
        n_high   = sum(1 for f in findings if f.get("severity") == "HIGH")
        n_med    = sum(1 for f in findings if f.get("severity") == "MEDIUM")
        n_low    = sum(1 for f in findings if f.get("severity") == "LOW")
        n_files  = len(res.get("files", []))

        if res.get("error"):
            st.error(f"**Error:** {res['error']}")
        else:
            # Status banner
            if not findings:
                st.success("✅  No issues found — this PR looks clean across all 4 audit categories.")
            elif n_high:
                st.error(f"🔴  **Action required** — {n_high} critical issue{'s' if n_high>1 else ''} found. Do not merge without review.")
            else:
                st.warning(f"🟡  **{len(findings)} minor issue{'s' if len(findings)>1 else ''} found** — review suggested before merging.")

            st.markdown("<br>", unsafe_allow_html=True)

            # Stats row — 5 native columns
            s1, s2, s3, s4, s5 = st.columns(5)
            with s1: stat_card(len(findings), "Total",         "#E2E8F0")
            with s2: stat_card(n_high,        "High",          "#EF4444")
            with s3: stat_card(n_med,         "Medium",        "#F59E0B")
            with s4: stat_card(n_low,         "Low",           "#3B82F6")
            with s5: stat_card(n_files,       "Files Changed", "#94A3B8")

            st.markdown("<br>", unsafe_allow_html=True)

            # Audit checklist — 2×2 native columns
            section_label("Audit Checklist")

            def chk_html(ok: bool) -> str:
                return ('<span style="color:#6EE7B7;font-weight:700;font-size:0.8rem;">✅ Clear</span>'
                        if ok else
                        '<span style="color:#FCA5A5;font-weight:700;font-size:0.8rem;">❌ Found</span>')

            cats = {f.get("category") for f in findings}

            def checklist_box(icon: str, label: str, cat: str) -> None:
                ok = cat not in cats
                st.markdown(f"""
<div style="background:#161B26;border:1px solid #2D3748;border-radius:8px;
            padding:12px 16px;display:flex;align-items:center;
            justify-content:space-between;">
  <span style="font-size:0.84rem;font-weight:500;color:#CBD5E1;">
    {icon}&nbsp; {label}
  </span>
  {chk_html(ok)}
</div>""", unsafe_allow_html=True)

            cl1, cl2 = st.columns(2)
            with cl1:
                checklist_box("🔐", "Hardcoded Secrets",   "hardcoded_secret")
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                checklist_box("🛡️", "Input Validation",    "missing_input_validation")
            with cl2:
                checklist_box("💉", "SQL Injection",        "sql_injection")
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                checklist_box("⚠️", "Error Handling",      "missing_error_handling")

            st.markdown("<br>", unsafe_allow_html=True)

            # Result tabs
            tab1, tab2, tab3 = st.tabs(["  Findings  ", "  Full Report  ", "  Raw Diff  "])

            with tab1:
                st.markdown("<br>", unsafe_allow_html=True)
                if findings:
                    for f in findings:
                        st.markdown(finding_card(f), unsafe_allow_html=True)
                else:
                    st.markdown("""
<div style="text-align:center;padding:48px 24px;color:#475569;">
  <div style="font-size:2.5rem;margin-bottom:12px;">✅</div>
  <div style="font-size:0.95rem;font-weight:600;color:#64748B;">All checks passed.</div>
  <div style="font-size:0.8rem;margin-top:6px;">No security issues detected in this PR.</div>
</div>""", unsafe_allow_html=True)

            with tab2:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(res.get("summary", ""))

            with tab3:
                st.markdown("<br>", unsafe_allow_html=True)
                diff = res.get("diff", "")
                if diff:
                    display = diff if len(diff) < 20000 else diff[:20000] + "\n\n# ... truncated"
                    st.code(display, language="diff")
                else:
                    st.info("No diff content available.")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("← Review another PR", key="reset_btn"):
                st.session_state.result = None
                st.rerun()
