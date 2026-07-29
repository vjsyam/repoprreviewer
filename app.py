import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="PR Reviewer — AI Code Review",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none; }

/* ── Root layout ── */
.app-root {
    background: #0A0B0F;
    min-height: 100vh;
    color: #E8EAF0;
}

/* ── Topbar ── */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 48px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    background: rgba(10,11,15,0.95);
    backdrop-filter: blur(12px);
    position: sticky;
    top: 0;
    z-index: 100;
}
.topbar-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 700;
    font-size: 1rem;
    color: #fff;
    letter-spacing: -0.3px;
}
.topbar-logo span.dot {
    width: 8px; height: 8px;
    background: linear-gradient(135deg, #6366F1, #8B5CF6);
    border-radius: 50%;
    display: inline-block;
}
.topbar-badge {
    font-size: 0.72rem;
    font-weight: 500;
    padding: 4px 10px;
    border-radius: 20px;
    background: rgba(99,102,241,0.15);
    color: #818CF8;
    border: 1px solid rgba(99,102,241,0.25);
    letter-spacing: 0.3px;
}

/* ── Hero Section ── */
.hero {
    padding: 72px 48px 48px;
    max-width: 860px;
}
.hero-eyebrow {
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #6366F1;
    margin-bottom: 16px;
}
.hero-title {
    font-size: 3.2rem;
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -1.5px;
    color: #FFFFFF;
    margin-bottom: 16px;
}
.hero-title .accent {
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #EC4899 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 1.1rem;
    font-weight: 400;
    color: #9CA3AF;
    line-height: 1.7;
    max-width: 560px;
}

/* ── Main Content Grid ── */
.content-grid {
    display: grid;
    grid-template-columns: 1fr 340px;
    gap: 0;
    min-height: calc(100vh - 200px);
    border-top: 1px solid rgba(255,255,255,0.05);
}
.main-panel {
    padding: 40px 48px;
    border-right: 1px solid rgba(255,255,255,0.05);
}
.side-panel {
    padding: 32px 28px;
    background: rgba(255,255,255,0.02);
}

/* ── Section Label ── */
.section-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #6B7280;
    margin-bottom: 12px;
}

/* ── URL Input Card ── */
.input-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;
    transition: border-color 0.2s;
}
.input-card:hover { border-color: rgba(99,102,241,0.3); }

/* ── Override Streamlit inputs ── */
div[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #E8EAF0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important;
    padding: 12px 16px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: rgba(99,102,241,0.6) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
    outline: none !important;
}
div[data-testid="stTextInput"] label {
    color: #9CA3AF !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    margin-bottom: 6px !important;
}

/* ── Run Button ── */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    padding: 12px 28px !important;
    letter-spacing: -0.2px !important;
    transition: opacity 0.2s, transform 0.1s !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.35) !important;
}
div[data-testid="stButton"] > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(99,102,241,0.45) !important;
}
div[data-testid="stButton"] > button:active { transform: translateY(0px) !important; }

/* ── Sample PR Chips ── */
.chip-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
.chip {
    font-size: 0.74rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
    padding: 5px 12px;
    border-radius: 20px;
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.2);
    color: #818CF8;
    cursor: pointer;
    transition: background 0.15s;
    white-space: nowrap;
}
.chip:hover { background: rgba(99,102,241,0.18); }

/* ── Pipeline Status ── */
.pipeline-row {
    display: flex;
    align-items: center;
    gap: 0;
    margin: 20px 0 28px;
}
.pipeline-node {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
}
.pipeline-icon {
    width: 40px; height: 40px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    font-weight: 700;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    transition: all 0.3s;
}
.pipeline-icon.active {
    background: rgba(99,102,241,0.2);
    border-color: rgba(99,102,241,0.5);
    box-shadow: 0 0 16px rgba(99,102,241,0.25);
}
.pipeline-icon.done {
    background: rgba(16,185,129,0.15);
    border-color: rgba(16,185,129,0.4);
}
.pipeline-label {
    font-size: 0.68rem;
    font-weight: 500;
    color: #6B7280;
    font-family: 'JetBrains Mono', monospace;
    text-align: center;
}
.pipeline-arrow {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(99,102,241,0.3), rgba(139,92,246,0.3));
    margin: 0 8px;
    margin-bottom: 24px;
    min-width: 20px;
}

/* ── Findings Cards ── */
.findings-grid { display: flex; flex-direction: column; gap: 12px; margin-top: 8px; }
.finding-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 16px 18px;
    transition: border-color 0.2s, transform 0.15s;
}
.finding-card:hover { border-color: rgba(255,255,255,0.14); transform: translateX(2px); }
.finding-card.high { border-left: 3px solid #EF4444; }
.finding-card.medium { border-left: 3px solid #F59E0B; }
.finding-card.low { border-left: 3px solid #3B82F6; }
.finding-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.finding-category {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: #6B7280;
}
.severity-badge {
    font-size: 0.66rem;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 4px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.severity-badge.high { background: rgba(239,68,68,0.15); color: #FCA5A5; border: 1px solid rgba(239,68,68,0.3); }
.severity-badge.medium { background: rgba(245,158,11,0.12); color: #FCD34D; border: 1px solid rgba(245,158,11,0.3); }
.severity-badge.low { background: rgba(59,130,246,0.12); color: #93C5FD; border: 1px solid rgba(59,130,246,0.3); }
.finding-desc { font-size: 0.88rem; color: #D1D5DB; line-height: 1.5; margin-bottom: 8px; }
.finding-file {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #6366F1;
    background: rgba(99,102,241,0.08);
    padding: 2px 8px;
    border-radius: 4px;
    display: inline-block;
    margin-bottom: 6px;
}
.finding-suggestion {
    font-size: 0.8rem;
    color: #9CA3AF;
    display: flex;
    align-items: flex-start;
    gap: 6px;
    line-height: 1.4;
}
.finding-suggestion::before { content: "→"; color: #6366F1; flex-shrink: 0; margin-top: 1px; }

/* ── Summary Stats Bar ── */
.stats-row { display: flex; gap: 12px; margin-bottom: 24px; }
.stat-box {
    flex: 1;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 14px;
    text-align: center;
}
.stat-number { font-size: 1.6rem; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 2px; }
.stat-label { font-size: 0.7rem; font-weight: 500; color: #6B7280; text-transform: uppercase; letter-spacing: 0.5px; }
.stat-number.high { color: #EF4444; }
.stat-number.medium { color: #F59E0B; }
.stat-number.low { color: #3B82F6; }
.stat-number.total { color: #E8EAF0; }

/* ── Status Banners ── */
.status-banner {
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    font-weight: 600;
    font-size: 0.92rem;
}
.status-banner.approved { background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.25); color: #6EE7B7; }
.status-banner.action { background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.25); color: #FCA5A5; }
.status-banner.comment { background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.25); color: #FCD34D; }

/* ── Audit Checklist ── */
.checklist { display: flex; flex-direction: column; gap: 8px; margin-bottom: 24px; }
.checklist-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 14px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px;
    font-size: 0.85rem;
}
.checklist-label { color: #D1D5DB; font-weight: 500; }
.checklist-ok { color: #6EE7B7; font-weight: 600; font-size: 0.78rem; }
.checklist-fail { color: #FCA5A5; font-weight: 600; font-size: 0.78rem; }

/* ── Instructions Panel (sidebar) ── */
.instr-title {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #4B5563;
    margin-bottom: 16px;
}
.instr-step {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
    align-items: flex-start;
}
.instr-num {
    width: 24px; height: 24px;
    border-radius: 6px;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.25);
    color: #818CF8;
    font-size: 0.72rem;
    font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    margin-top: 1px;
}
.instr-content { flex: 1; }
.instr-heading { font-size: 0.82rem; font-weight: 600; color: #D1D5DB; margin-bottom: 3px; }
.instr-body { font-size: 0.76rem; color: #6B7280; line-height: 1.5; }
.instr-code {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 5px;
    padding: 2px 6px;
    color: #A78BFA;
    display: inline-block;
    margin-top: 3px;
}
.instr-divider { border: none; border-top: 1px solid rgba(255,255,255,0.05); margin: 20px 0; }

/* ── Sample PRs in sidebar ── */
.sample-pr {
    padding: 10px 12px;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.07);
    background: rgba(255,255,255,0.02);
    margin-bottom: 8px;
    cursor: pointer;
    transition: background 0.15s, border-color 0.15s;
}
.sample-pr:hover { background: rgba(99,102,241,0.08); border-color: rgba(99,102,241,0.2); }
.sample-pr-name { font-size: 0.78rem; font-weight: 600; color: #D1D5DB; }
.sample-pr-url { font-family: 'JetBrains Mono', monospace; font-size: 0.66rem; color: #6B7280; margin-top: 2px; word-break: break-all; }
.sample-pr-tags { display: flex; gap: 4px; margin-top: 6px; flex-wrap: wrap; }
.pr-tag {
    font-size: 0.62rem;
    font-weight: 600;
    padding: 2px 7px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}
.pr-tag.sqli { background: rgba(239,68,68,0.12); color: #FCA5A5; }
.pr-tag.secret { background: rgba(245,158,11,0.12); color: #FCD34D; }
.pr-tag.clean { background: rgba(16,185,129,0.12); color: #6EE7B7; }
.pr-tag.err { background: rgba(99,102,241,0.12); color: #A78BFA; }

/* ── Diff Viewer ── */
div[data-testid="stCode"] {
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    background: rgba(0,0,0,0.3) !important;
}
div[data-testid="stCode"] code {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
}

/* ── Tabs ── */
div[data-testid="stTabs"] [role="tablist"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(255,255,255,0.07) !important;
    gap: 4px !important;
}
div[data-testid="stTabs"] [role="tab"] {
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: #6B7280 !important;
    padding: 8px 16px !important;
    border-radius: 6px 6px 0 0 !important;
    border: none !important;
    background: transparent !important;
}
div[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #E8EAF0 !important;
    background: rgba(99,102,241,0.1) !important;
    border-bottom: 2px solid #6366F1 !important;
}

/* ── Error box ── */
div[data-testid="stAlert"] {
    border-radius: 10px !important;
    border: 1px solid rgba(239,68,68,0.3) !important;
    background: rgba(239,68,68,0.07) !important;
}

/* ── Spinner text ── */
div[data-testid="stStatusWidget"] { color: #9CA3AF !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None
if "running" not in st.session_state:
    st.session_state.running = False
if "pr_url_input" not in st.session_state:
    st.session_state.pr_url_input = "https://github.com/vjsyam/imageforgerydetector/pull/1"

# ─────────────────────────────────────────────────────────────────────────────
# TOPBAR
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-root">
<div class="topbar">
  <div class="topbar-logo">
    <span class="dot"></span>
    PR Reviewer Agent Crew
  </div>
  <span class="topbar-badge">Powered by LangGraph + Gemini</span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">Multi-Agent AI Code Review</div>
  <div class="hero-title">
    Catch security bugs<br>
    before they <span class="accent">hit production.</span>
  </div>
  <div class="hero-sub">
    Paste any GitHub PR URL. Three AI agents fetch the diff, scan for
    vulnerabilities, and generate a structured review — in seconds.
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONTENT GRID — left main, right instructions
# ─────────────────────────────────────────────────────────────────────────────
col_main, col_side = st.columns([2.2, 1], gap="small")

# ── RIGHT PANEL: Instructions ─────────────────────────────────────────────────
with col_side:
    st.markdown("""
    <div class="side-panel">
      <div class="instr-title">How to use</div>

      <div class="instr-step">
        <div class="instr-num">1</div>
        <div class="instr-content">
          <div class="instr-heading">Paste a GitHub PR URL</div>
          <div class="instr-body">
            Copy the URL of any public GitHub Pull Request.<br>
            Format: <span class="instr-code">github.com/owner/repo/pull/N</span>
          </div>
        </div>
      </div>

      <div class="instr-step">
        <div class="instr-num">2</div>
        <div class="instr-content">
          <div class="instr-heading">Add API keys (optional)</div>
          <div class="instr-body">
            <b style="color:#D1D5DB">GitHub Token</b> — avoids rate limits on GitHub API.<br>
            <b style="color:#D1D5DB">Gemini Key</b> — enables LLM deep-review mode.<br>
            Without keys, heuristic analysis still works.
          </div>
        </div>
      </div>

      <div class="instr-step">
        <div class="instr-num">3</div>
        <div class="instr-content">
          <div class="instr-heading">Click Run Review</div>
          <div class="instr-body">
            The 3-node LangGraph pipeline runs:<br>
            <span class="instr-code">fetch_pr</span> →
            <span class="instr-code">review_pr</span> →
            <span class="instr-code">summarize_pr</span>
          </div>
        </div>
      </div>

      <div class="instr-step">
        <div class="instr-num">4</div>
        <div class="instr-content">
          <div class="instr-heading">Read the findings</div>
          <div class="instr-body">
            Each finding shows the severity, exact file &amp; line, a plain-English description, and an actionable fix suggestion.
          </div>
        </div>
      </div>

      <hr class="instr-divider">
      <div class="instr-title">What gets flagged</div>

      <div class="instr-step">
        <div class="instr-num" style="background:rgba(245,158,11,0.12);border-color:rgba(245,158,11,0.25);color:#FCD34D;">🔐</div>
        <div class="instr-content">
          <div class="instr-heading">Hardcoded Secrets</div>
          <div class="instr-body">API keys, passwords, bearer tokens in plaintext</div>
        </div>
      </div>

      <div class="instr-step">
        <div class="instr-num" style="background:rgba(239,68,68,0.12);border-color:rgba(239,68,68,0.25);color:#FCA5A5;">💉</div>
        <div class="instr-content">
          <div class="instr-heading">SQL Injection</div>
          <div class="instr-body">String formatting / concatenation in SQL queries</div>
        </div>
      </div>

      <div class="instr-step">
        <div class="instr-num" style="background:rgba(59,130,246,0.12);border-color:rgba(59,130,246,0.25);color:#93C5FD;">🛡️</div>
        <div class="instr-content">
          <div class="instr-heading">Missing Input Validation</div>
          <div class="instr-body">Unsanitized request params used directly</div>
        </div>
      </div>

      <div class="instr-step">
        <div class="instr-num" style="background:rgba(99,102,241,0.12);border-color:rgba(99,102,241,0.25);color:#A78BFA;">⚠️</div>
        <div class="instr-content">
          <div class="instr-heading">Missing Error Handling</div>
          <div class="instr-body">Bare <span class="instr-code">except: pass</span> and empty catch blocks</div>
        </div>
      </div>

      <hr class="instr-divider">
      <div class="instr-title">Sample PRs to try</div>
    """, unsafe_allow_html=True)

    sample_prs = [
        {
            "name": "imageforgerydetector #1",
            "url": "https://github.com/vjsyam/imageforgerydetector/pull/1",
            "desc": "FastAPI serving layer — real SQLi + exception smells",
            "tags": [("💉 SQLi", "sqli"), ("⚠️ Error", "err")],
        },
        {
            "name": "psf/requests #6700",
            "url": "https://github.com/psf/requests/pull/6700",
            "desc": "Public open-source PR — typically clean",
            "tags": [("✅ Clean", "clean")],
        },
    ]

    for pr in sample_prs:
        if st.button(f"▶ {pr['name']}", key=f"sample_{pr['name']}", use_container_width=True):
            st.session_state.pr_url_input = pr["url"]
            st.rerun()

        tags_html = "".join(f'<span class="pr-tag {t[1]}">{t[0]}</span>' for t in pr["tags"])
        st.markdown(f"""
        <div style="font-size:0.72rem;color:#4B5563;margin:-8px 0 12px 0;padding:6px 2px;">
          {pr['desc']}<br>
          <span style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#374151;">{pr['url']}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ── LEFT PANEL: Main interaction ───────────────────────────────────────────────
with col_main:
    st.markdown('<div class="main-panel">', unsafe_allow_html=True)

    # ── Config expander (API keys) ─────────────────────────────────────────
    with st.expander("⚙️  API Keys & Configuration", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            github_token = st.text_input(
                "GitHub Personal Access Token",
                value=os.getenv("GITHUB_TOKEN", ""),
                type="password",
                placeholder="ghp_xxxx  (optional — increases rate limit)",
                help="Get one at github.com/settings/tokens (public_repo scope)"
            )
        with c2:
            gemini_key = st.text_input(
                "Gemini API Key",
                value=os.getenv("GEMINI_API_KEY", ""),
                type="password",
                placeholder="AIzaSy...  (optional — enables LLM mode)",
                help="Get one at aistudio.google.com"
            )
        if github_token:
            os.environ["GITHUB_TOKEN"] = github_token
        if gemini_key:
            os.environ["GEMINI_API_KEY"] = gemini_key

        st.markdown("""
        <div style="font-size:0.76rem;color:#4B5563;margin-top:8px;">
          Without keys: heuristic regex scanner runs as fallback.<br>
          With Gemini key: LLM semantic analysis mode activates automatically.
        </div>
        """, unsafe_allow_html=True)

    # ── Pipeline architecture visual ───────────────────────────────────────
    result = st.session_state.result
    done = result is not None and not result.get("error")

    st.markdown(f"""
    <div class="pipeline-row">
      <div class="pipeline-node">
        <div class="pipeline-icon {'done' if done else ''}">📡</div>
        <div class="pipeline-label">fetch_pr</div>
      </div>
      <div class="pipeline-arrow"></div>
      <div class="pipeline-node">
        <div class="pipeline-icon {'done' if done else ''}">🤖</div>
        <div class="pipeline-label">review_pr</div>
      </div>
      <div class="pipeline-arrow"></div>
      <div class="pipeline-node">
        <div class="pipeline-icon {'done' if done else ''}">📝</div>
        <div class="pipeline-label">summarize_pr</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── URL input + Run button ──────────────────────────────────────────────
    st.markdown('<div class="section-label">GitHub Pull Request URL</div>', unsafe_allow_html=True)

    input_col, btn_col = st.columns([5, 1])
    with input_col:
        pr_url = st.text_input(
            "pr_url",
            value=st.session_state.pr_url_input,
            placeholder="https://github.com/owner/repo/pull/42",
            label_visibility="collapsed",
            key="pr_url_field"
        )
    with btn_col:
        run_btn = st.button("Run Review →", use_container_width=True, key="run_btn")

    st.markdown("""
    <div style="font-size:0.72rem;color:#374151;margin-top:6px;">
      Works with any public GitHub PR — authenticated or unauthenticated.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── RUN PIPELINE ────────────────────────────────────────────────────────
    if run_btn:
        if not pr_url or "github.com" not in pr_url or "/pull/" not in pr_url:
            st.error("Please enter a valid GitHub PR URL — e.g. https://github.com/owner/repo/pull/42")
        else:
            st.session_state.pr_url_input = pr_url
            with st.status("Running pipeline...", expanded=True) as status:
                st.write("**Step 1 / 3** — `fetch_pr`: Fetching PR diff from GitHub...")

                from graph import pr_review_graph
                from state import PRReviewState

                final_state = pr_review_graph.invoke({"pr_url": pr_url})

                if final_state.get("error"):
                    status.update(label="Pipeline failed", state="error", expanded=True)
                    st.session_state.result = final_state
                else:
                    st.write("**Step 2 / 3** — `review_pr`: Scanning for vulnerabilities...")
                    st.write("**Step 3 / 3** — `summarize_pr`: Generating review report...")
                    status.update(label="Review complete", state="complete", expanded=False)
                    st.session_state.result = final_state

            st.rerun()

    # ── RESULTS ─────────────────────────────────────────────────────────────
    if st.session_state.result:
        res = st.session_state.result

        if res.get("error"):
            st.markdown(f"""
            <div class="status-banner action">
              ❌&nbsp; <span>{res["error"]}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            findings = res.get("findings", [])
            high = sum(1 for f in findings if f.get("severity") == "HIGH")
            med  = sum(1 for f in findings if f.get("severity") == "MEDIUM")
            low  = sum(1 for f in findings if f.get("severity") == "LOW")

            # Status banner
            if not findings:
                st.markdown('<div class="status-banner approved">✅ &nbsp; No issues found — this PR looks clean!</div>', unsafe_allow_html=True)
            elif high:
                st.markdown(f'<div class="status-banner action">🔴 &nbsp; Action required — {high} critical issue{"s" if high>1 else ""} found. Do not merge without review.</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="status-banner comment">🟡 &nbsp; {len(findings)} minor issue{"s" if len(findings)>1 else ""} found — review suggested before merging.</div>', unsafe_allow_html=True)

            # Stats row
            st.markdown(f"""
            <div class="stats-row">
              <div class="stat-box">
                <div class="stat-number total">{len(findings)}</div>
                <div class="stat-label">Total</div>
              </div>
              <div class="stat-box">
                <div class="stat-number high">{high}</div>
                <div class="stat-label">High</div>
              </div>
              <div class="stat-box">
                <div class="stat-number medium">{med}</div>
                <div class="stat-label">Medium</div>
              </div>
              <div class="stat-box">
                <div class="stat-number low">{low}</div>
                <div class="stat-label">Low</div>
              </div>
              <div class="stat-box">
                <div class="stat-number" style="color:#9CA3AF;">{len(res.get("files",[]))}</div>
                <div class="stat-label">Files Changed</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Audit checklist
            def chk(cat):
                found = any(f.get("category") == cat for f in findings)
                return f'<span class="checklist-fail">❌ Found</span>' if found else f'<span class="checklist-ok">✅ Clear</span>'

            st.markdown(f"""
            <div class="checklist">
              <div class="checklist-row"><span class="checklist-label">🔐 Hardcoded Secrets</span>{chk("hardcoded_secret")}</div>
              <div class="checklist-row"><span class="checklist-label">💉 SQL Injection</span>{chk("sql_injection")}</div>
              <div class="checklist-row"><span class="checklist-label">🛡️ Input Validation</span>{chk("missing_input_validation")}</div>
              <div class="checklist-row"><span class="checklist-label">⚠️ Error Handling</span>{chk("missing_error_handling")}</div>
            </div>
            """, unsafe_allow_html=True)

            # Tabs: Findings | Summary | Diff
            tab1, tab2, tab3 = st.tabs(["Findings", "Full Report", "Raw Diff"])

            with tab1:
                if findings:
                    cat_icons = {
                        "hardcoded_secret": "🔐 Hardcoded Secret",
                        "sql_injection": "💉 SQL Injection",
                        "missing_input_validation": "🛡️ Input Validation",
                        "missing_error_handling": "⚠️ Error Handling",
                    }
                    cards_html = '<div class="findings-grid">'
                    for f in findings:
                        sev = f.get("severity", "MEDIUM").lower()
                        cat = cat_icons.get(f.get("category",""), f.get("category",""))
                        cards_html += f"""
                        <div class="finding-card {sev}">
                          <div class="finding-header">
                            <span class="finding-category">{cat}</span>
                            <span class="severity-badge {sev}">{f.get("severity","MEDIUM")}</span>
                          </div>
                          <div class="finding-desc">{f.get("description","")}</div>
                          <div class="finding-file">{f.get("file","unknown")} : {f.get("line","")}</div>
                          <div class="finding-suggestion">{f.get("suggestion","")}</div>
                        </div>"""
                    cards_html += "</div>"
                    st.markdown(cards_html, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="text-align:center;padding:48px;color:#4B5563;">
                      <div style="font-size:2.5rem;margin-bottom:12px;">✅</div>
                      <div style="font-size:0.95rem;font-weight:600;color:#6B7280;">No findings — this PR is clean.</div>
                      <div style="font-size:0.8rem;color:#374151;margin-top:6px;">All 4 audit categories passed.</div>
                    </div>
                    """, unsafe_allow_html=True)

            with tab2:
                st.markdown(res.get("summary", ""))

            with tab3:
                diff = res.get("diff", "")
                if diff:
                    display_diff = diff if len(diff) < 20000 else diff[:20000] + "\n\n# ... diff truncated (showing first 20 000 chars)"
                    st.code(display_diff, language="diff")
                else:
                    st.info("No diff content available.")

            # Reset button
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("← Review another PR", key="reset_btn"):
                st.session_state.result = None
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)  # close app-root
