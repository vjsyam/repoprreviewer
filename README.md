# 🤖 PR Reviewer Agent Crew

> **Multi-agent Pull Request security reviewer powered by LangGraph, GitHub API, and LLMs.**
> Automatically flags hardcoded secrets, SQL injection, missing input validation, and swallowed exceptions in any GitHub PR — in seconds.

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1.x-6366F1?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-1.60-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini_AI-Powered-4285F4?style=for-the-badge&logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Quickstart](#-quickstart)
- [CLI Usage](#-cli-usage)
- [Streamlit UI](#-streamlit-ui)
- [Configuration](#-configuration)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Sample Output](#-sample-output)
- [Roadmap](#-roadmap)

---

## 🔍 Overview

**PR Reviewer Agent Crew** is an autonomous, multi-agent code review tool that analyzes any GitHub Pull Request for security vulnerabilities and code quality issues. It uses a **3-node LangGraph pipeline** to:

1. **Fetch** the raw diff and file list from GitHub
2. **Review** the diff with an LLM (Gemini 2.5 Flash by default) using a structured security-audit prompt
3. **Summarize** findings into a clean, GitHub PR-comment-style Markdown report

No more missing critical security bugs in code review — this agent crew acts as your automated security co-reviewer.

---

## 🏗️ Architecture

```
PR URL Input
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph StateGraph                     │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   fetch_pr   │───▶│  review_pr   │───▶│ summarize_pr │  │
│  │              │    │              │    │              │  │
│  │ GitHub REST  │    │ LLM Security │    │  Markdown    │  │
│  │ API / .diff  │    │ Code Review  │    │  Generator   │  │
│  │   fallback   │    │  + Heuristic │    │              │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                             │
│          PRReviewState flows through each node              │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
  PR Review Summary (Markdown)
```

### Node Responsibilities

| Node | Input | Output |
|------|-------|--------|
| `fetch_pr` | GitHub PR URL | Raw diff, file list, PR title/metadata |
| `review_pr` | Diff text | Structured findings list (file, line, severity, suggestion) |
| `summarize_pr` | Findings list | Full Markdown PR review comment |

### LangGraph State Schema

```python
class PRReviewState(TypedDict):
    pr_url: str          # Full GitHub PR URL
    owner: str           # Repo owner
    repo: str            # Repo name
    pr_number: int       # PR number
    pr_title: str        # PR title from GitHub
    diff: str            # Raw git diff text
    files: list          # Changed files with additions/deletions
    findings: list       # Structured security/quality findings
    summary: str         # Final Markdown report
    error: str | None    # Error message if any node fails
```

---

## ✨ Features

### 🔐 Security Audit Categories

| Category | What It Catches |
|----------|----------------|
| **Hardcoded Secrets** | API keys, DB passwords, bearer tokens, private keys in plaintext |
| **SQL Injection** | `%` string formatting in queries, string concatenation in SQL, f-string queries |
| **Missing Input Validation** | Direct use of `request.GET`, `req.body`, unsanitized user params |
| **Missing Error Handling** | Bare `except: pass`, empty catch blocks, swallowed exceptions |

### 🤖 Dual-Mode Analysis

- **LLM Mode** (with `GEMINI_API_KEY`): Deep semantic analysis using Gemini 2.5 Flash — understands context, logic, and subtle vulnerabilities
- **Heuristic Mode** (fallback): Fast regex-based static analysis — works without any API key, great for CI pipelines

### 🌐 Two Interfaces

- **CLI**: `python main.py <pr_url>` — perfect for CI/CD integration
- **Streamlit UI**: Interactive web app with diff viewer, findings breakdown, and raw output tabs

### 🔄 GitHub API + Fallback

- Authenticates with `GITHUB_TOKEN` for higher rate limits
- Falls back to public `.diff` URL for unauthenticated requests

---

## 🚀 Quickstart

### Prerequisites

- Python 3.10+
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/vjsyam/repoprreviewer.git
cd repoprreviewer
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy the example environment file and fill in your keys:

```bash
cp .env.example .env
```

```env
# .env
GITHUB_TOKEN=ghp_your_github_personal_access_token
GEMINI_API_KEY=your_gemini_api_key_here
LLM_MODEL=gemini-2.5-flash
```

> **GITHUB_TOKEN** is optional for public repos but strongly recommended to avoid rate limits.
> **GEMINI_API_KEY** is optional — without it, the heuristic analyzer is used as fallback.

---

## 💻 CLI Usage

Run the full pipeline from the command line:

```bash
python main.py https://github.com/owner/repo/pull/42
```

**Example against a real PR:**

```bash
python main.py https://github.com/vjsyam/imageforgerydetector/pull/1
```

**Sample output:**

```
======================================================================
🚀 Starting LangGraph PR Reviewer Agent Crew
Target PR: https://github.com/vjsyam/imageforgerydetector/pull/1
======================================================================

🔍 [fetch_pr] Fetching PR data for: https://github.com/vjsyam/imageforgerydetector/pull/1
✅ [fetch_pr] Successfully fetched PR #1: 'feat: add FastAPI model serving API layer' (1 files changed, diff size: 2566 chars)
🤖 [review_pr] Analyzing diff (2566 chars)...
📝 [summarize_pr] Generating PR review summary for 2 findings...

# 🤖 Automated PR Security & Quality Review

**Repository:** `vjsyam/imageforgerydetector` | **PR:** #1
**Files Changed:** 1 files | **Total Findings:** 2 (1 High, 1 Medium, 0 Low)

### 🔴 Review Status: ACTION REQUIRED (1 High Severity Issue)

## 🛡️ Audit Checklist
- [x] Hardcoded Secrets: ✅ Clear
- [x] Input Validation: ✅ Clear
- [x] SQL Injection: ❌ Found
- [x] Error Handling: ❌ Found

## 🔍 Detailed Findings & Recommendations

| Severity | Category | File & Line | Description & Suggestion |
|----------|----------|-------------|--------------------------|
| 🔴 HIGH | 💉 SQL Injection | src/api/api_server.py:L38 | % string formatting in SQL query → use parameterized queries |
| 🟡 MEDIUM | ⚠️ Exception Safety | src/api/api_server.py:L30 | Bare except: pass swallows errors → catch specific exceptions |
```

---

## 🌐 Streamlit UI

Launch the interactive web application:

```bash
streamlit run app.py
```

Then open your browser at: **http://localhost:8501**

### UI Features

- **PR URL input** with sample presets
- **Real-time pipeline status** with step-by-step progress
- **Three result tabs**:
  - 📋 **PR Review Summary** — Full Markdown report with severity badges
  - 🔍 **Findings Breakdown** — Raw JSON findings for programmatic use
  - 📄 **Raw Git Diff** — Syntax-highlighted diff view
- **Sidebar configuration** — Enter GitHub token and Gemini API key without touching `.env`

---

## ⚙️ Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GITHUB_TOKEN` | _(empty)_ | GitHub Personal Access Token — increases API rate limit from 60 to 5000 req/hour |
| `GEMINI_API_KEY` | _(empty)_ | Google Gemini API key — enables LLM-powered deep review |
| `LLM_MODEL` | `gemini-2.5-flash` | LLM model name (e.g. `gemini-2.5-pro`, `gemini-1.5-flash`) |

### Getting a GitHub Token

1. Go to [GitHub Settings → Tokens](https://github.com/settings/tokens)
2. Generate a **classic token** with `public_repo` scope (read-only is sufficient)
3. Add to your `.env` as `GITHUB_TOKEN=ghp_...`

### Getting a Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Create an API key
3. Add to your `.env` as `GEMINI_API_KEY=...`

---

## 📁 Project Structure

```
repoprreviewer/
├── main.py               # CLI entry point: python main.py <pr_url>
├── app.py                # Streamlit web UI
├── graph.py              # LangGraph StateGraph assembly
├── state.py              # PRReviewState TypedDict definition
├── github_utils.py       # GitHub REST API + public diff fallback fetcher
│
├── nodes/
│   ├── __init__.py
│   ├── fetch_node.py     # Node 1: Fetches PR diff & metadata from GitHub
│   ├── review_node.py    # Node 2: LLM security review + heuristic fallback
│   └── summarize_node.py # Node 3: Generates Markdown PR review comment
│
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variable template
└── README.md
```

---

## 🔬 How It Works

### Node 1: `fetch_pr`

Parses the GitHub URL to extract `owner`, `repo`, and `pr_number`. Makes two requests to the GitHub REST API:
- `GET /repos/{owner}/{repo}/pulls/{number}` with `Accept: application/vnd.github.v3.diff` → raw unified diff
- `GET /repos/{owner}/{repo}/pulls/{number}/files` → list of changed files with patch hunks

Falls back to fetching `https://github.com/{owner}/{repo}/pull/{number}.diff` directly if the API is rate-limited.

### Node 2: `review_pr`

**With LLM** (when `GEMINI_API_KEY` is set):
- Sends the raw diff to Gemini with a structured system prompt instructing it to output a JSON array of findings
- Parses the JSON response into a typed list of `Finding` objects

**Heuristic fallback** (no API key):
- Scans added lines (`+` prefix in diff) with regex patterns for secrets, SQL patterns, error handling gaps, and input validation issues
- Extracts file names and line numbers from diff `@@` hunk headers

### Node 3: `summarize_pr`

Formats findings into a rich Markdown document with:
- Overall status banner (✅ Approved / 🔴 Action Required / 🟡 Comment)
- Severity counts (High / Medium / Low)
- Audit checklist for each category
- Findings table with severity badges, file/line references, and actionable fix suggestions

---

## 📊 Sample Output

### When Issues Are Found

```markdown
# 🤖 Automated PR Security & Quality Review

**Repository:** `owner/repo` | **PR:** #42 - *"Add user auth module"*
**Files Changed:** 2 files | **Total Findings:** 3 (2 High, 1 Medium, 0 Low)

### 🔴 Review Status: ACTION REQUIRED (2 High Severity Issues)

## 🛡️ Audit Checklist
- [x] Hardcoded Secrets: ❌ Found
- [x] Input Validation: ✅ Clear
- [x] SQL Injection: ❌ Found
- [x] Error Handling: ❌ Found

## 🔍 Detailed Findings & Recommendations

| Severity | Category | File & Line | Issue Description & Suggestion |
| :---: | :--- | :--- | :--- |
| 🔴 HIGH | 🔐 Secret Leak | app/config.py:L12 | Hardcoded API key detected → Store in env vars |
| 🔴 HIGH | 💉 SQL Injection | app/db.py:L34 | % string formatting in query → Use parameterized queries |
| 🟡 MEDIUM | ⚠️ Exception Safety | app/db.py:L41 | Bare except swallows errors → Catch specific exceptions |
```

### When Clean

```markdown
### ✅ Review Status: APPROVED / NO ISSUES FOUND
No security vulnerabilities, hardcoded secrets, SQL injection patterns,
or missing error handlers were detected in this diff.
```

---

## 🗺️ Roadmap

- [ ] **GitHub PR Comment integration** — post review directly as a PR comment via GitHub API
- [ ] **CI/CD GitHub Action** — run automatically on every PR opened
- [ ] **OpenAI / Anthropic support** — plug in any LangChain-compatible LLM
- [ ] **Custom rule engine** — define YAML-based custom patterns per organization
- [ ] **Severity thresholds** — configurable pass/fail gates for CI pipelines
- [ ] **Multi-file diff chunking** — handle PRs with 50+ files via chunked LLM calls

---

## 🤝 Contributing

PRs welcome! To contribute:

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push and open a PR

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
Built with ❤️ using <strong>LangGraph</strong> · <strong>Google Gemini</strong> · <strong>Streamlit</strong>
</div>
