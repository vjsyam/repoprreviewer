import os
import streamlit as st
from graph import pr_review_graph
from state import PRReviewState
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="PR Reviewer Agent Crew",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555;
        margin-bottom: 1.5rem;
    }
    .stButton button {
        background-color: #1E88E5;
        color: white;
        font-weight: 600;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🤖 PR Reviewer Agent Crew</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Multi-agent automated pull request reviewer built with <b>LangGraph</b>, <b>GitHub REST/MCP</b>, and <b>LLMs</b>.</div>', unsafe_allow_html=True)

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Configuration")
    github_token = st.text_input("GitHub Personal Access Token (Optional)", value=os.getenv("GITHUB_TOKEN", ""), type="password")
    gemini_key = st.text_input("Gemini / LLM API Key", value=os.getenv("GEMINI_API_KEY", ""), type="password")
    
    if github_token:
        os.environ["GITHUB_TOKEN"] = github_token
    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key
        
    st.divider()
    st.markdown("### 🧩 Pipeline Architecture")
    st.markdown("""
    1. **`fetch_pr`**: Pulls raw diff & metadata via GitHub API/MCP.
    2. **`review_pr`**: Scans for secrets, input validation, SQLi & exception handling.
    3. **`summarize_pr`**: Generates PR-comment-style Markdown report.
    """)

# Input section
st.subheader("🔍 Analyze Pull Request")
col1, col2 = st.columns([4, 1])

default_url = "https://github.com/psf/requests/pull/6700"
with col1:
    pr_url = st.text_input("GitHub PR URL", value=default_url, placeholder="https://github.com/owner/repo/pull/123")

with col2:
    st.write(" ")
    st.write(" ")
    run_btn = st.button("🚀 Run Review", use_container_width=True)

# Preset examples
st.caption("Sample PRs to test: `https://github.com/psf/requests/pull/6700` | `https://github.com/pallets/flask/pull/5000`")

if run_btn:
    if not pr_url:
        st.error("Please enter a valid GitHub PR URL.")
    else:
        with st.status("🚀 Running LangGraph PR Reviewer Agent Crew...", expanded=True) as status:
            st.write("📡 **Step 1/3 (fetch_pr):** Retrieving PR diff and file list from GitHub...")
            initial_state: PRReviewState = {"pr_url": pr_url}
            
            # Execute pipeline
            final_state = pr_review_graph.invoke(initial_state)
            
            if final_state.get("error"):
                status.update(label="❌ Review Failed", state="error")
                st.error(final_state["error"])
            else:
                st.write("🤖 **Step 2/3 (review_pr):** Analyzing code changes for security vulnerabilities & bugs...")
                st.write("📝 **Step 3/3 (summarize_pr):** Formatting Markdown PR review comment...")
                status.update(label="✅ PR Review Complete!", state="complete", expanded=False)
                
                # Results display
                tab1, tab2, tab3 = st.tabs(["📋 PR Review Summary", "🔍 Findings Breakdown", "📄 Raw Git Diff"])
                
                with tab1:
                    st.markdown(final_state.get("summary", ""))
                    
                with tab2:
                    findings = final_state.get("findings", [])
                    if findings:
                        st.json(findings)
                    else:
                        st.info("No security defects or code issues flagged!")
                        
                with tab3:
                    diff = final_state.get("diff", "")
                    st.code(diff if len(diff) < 20000 else diff[:20000] + "\n... [diff truncated]", language="diff")
