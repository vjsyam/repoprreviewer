import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import json
import re
from typing import List
from state import PRReviewState, Finding
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are an expert Senior Security Code Reviewer.
Your task is to analyze git diffs for code changes in Pull Requests and flag security vulnerabilities and code quality defects.

Specifically focus on flagging the following 4 categories:
1. hardcoded_secret: Plaintext API keys, tokens, credentials, DB passwords, private keys.
2. missing_input_validation: Unsanitized user input, lack of bounds/type checking, path traversal risks.
3. sql_injection: Unsafe SQL string formatting, unparameterized raw queries.
4. missing_error_handling: Swallowed exceptions (empty except/catch), missing try-except on IO/network calls, unsafe dereferencing.

CRITICAL INSTRUCTIONS:
- Analyze ONLY added/modified lines (prefixed with '+') in the diff.
- Return a JSON array of findings.
- Each finding MUST be an object with these exact keys:
  - "file": string (path to modified file)
  - "line": string (line number or range from diff header e.g. "L45")
  - "category": string (one of: "hardcoded_secret", "missing_input_validation", "sql_injection", "missing_error_handling")
  - "severity": string ("HIGH", "MEDIUM", or "LOW")
  - "description": string (clear concise explanation of the flaw)
  - "suggestion": string (actionable recommendation or code fix)

If no defects are found in those 4 categories, return an empty JSON array: []
Respond ONLY with raw valid JSON (no markdown block wrapper or explanatory text).
"""

def heuristic_diff_analysis(diff: str, files: list) -> List[Finding]:
    """
    Rule-based static analysis fallback when LLM API key is not configured.
    Detects basic patterns in diffs for testing without API keys.
    """
    findings: List[Finding] = []
    current_file = "unknown"
    line_num = 1
    
    secret_patterns = [
        (r"(?i)(api[_-]?key|secret|password|bearer|auth[_-]?token|aws[_-]?secret[_-]?key)\s*=\s*['\"][A-Za-z0-9_\-]{8,}['\"]", "hardcoded_secret", "HIGH", "Potential hardcoded secret or API key assignment detected in code.", "Store sensitive credentials in environment variables or secure key vaults."),
        (r"-----BEGIN (RSA|OPENSSH|EC|PRIVATE) KEY-----", "hardcoded_secret", "HIGH", "Hardcoded private key detected.", "Remove raw private key material from source code.")
    ]
    
    sql_patterns = [
        (r"(?i)(SELECT|INSERT|UPDATE|DELETE)\s+.*\s*%\s*", "sql_injection", "HIGH", "Possible SQL injection via % string formatting in query.", "Use parameterized queries or ORM query builders instead of raw string formatting."),
        (r"(?i)(SELECT|INSERT|UPDATE|DELETE)\s+.*\+\s*[\w_]+", "sql_injection", "HIGH", "Possible SQL injection via string concatenation in query.", "Use query parameters (e.g. cursor.execute(query, (param,))) instead of string concatenation."),
        (r"(?i)f['\"].*(SELECT|INSERT|UPDATE|DELETE).*{.*}", "sql_injection", "HIGH", "Possible SQL injection via Python f-string query formatting.", "Pass parameters bound separately to the query engine.")
    ]
    
    error_patterns = [
        (r"except\s*:\s*(pass|\n|\Z)", "missing_error_handling", "MEDIUM", "Bare except block swallows errors silently without logging.", "Catch specific exception types and log or handle the error appropriately."),
        (r"except\s+\w+.*:\s*pass", "missing_error_handling", "MEDIUM", "Empty exception handler (pass) suppresses failure feedback.", "Add proper error recovery or log the exception stack trace."),
        (r"catch\s*\([^)]*\)\s*\{\s*\}", "missing_error_handling", "MEDIUM", "Empty catch block swallows errors silently.", "Log or rethrow error with context.")
    ]
    
    validation_patterns = [
        (r"(?i)(request\.GET|request\.POST|req\.body|req\.GET|params\[).*\[", "missing_input_validation", "LOW", "Direct user input access detected; verify validation/sanitization is performed.", "Sanitize and validate all incoming request parameters before internal processing.")
    ]
    
    all_rules = secret_patterns + sql_patterns + error_patterns + validation_patterns

    lines = diff.splitlines()
    for line in lines:
        if line.startswith("+++ b/"):
            current_file = line[6:].strip()
        elif line.startswith("@@"):
            match = re.search(r"\+(\d+)", line)
            if match:
                line_num = int(match.group(1))
        elif line.startswith("+") and not line.startswith("+++"):
            code_line = line[1:]
            for pattern, cat, sev, desc, sug in all_rules:
                if re.search(pattern, code_line):
                    findings.append({
                        "file": current_file,
                        "line": f"L{line_num}",
                        "category": cat,
                        "severity": sev,
                        "description": desc,
                        "suggestion": sug
                    })
            line_num += 1
        elif not line.startswith("-"):
            line_num += 1
            
    return findings


def review_pr_node(state: PRReviewState) -> PRReviewState:
    """
    Node 2: review_pr
    Analyzes the PR diff using LLM (Gemini / LangChain) or rule-based fallback.
    """
    diff = state.get("diff", "")
    files = state.get("files", [])
    
    if not diff:
        print("⚠️ [review_pr] Empty diff provided. Skipping analysis.")
        return {**state, "findings": []}

    print(f"🤖 [review_pr] Analyzing diff ({len(diff)} chars)...")
    
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY")
    findings: List[Finding] = []
    
    if api_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.messages import SystemMessage, HumanMessage
            
            # Limit diff size to prevent context overflow if diff is massive
            truncated_diff = diff[:40000] if len(diff) > 40000 else diff
            
            llm = ChatGoogleGenerativeAI(
                model=os.getenv("LLM_MODEL", "gemini-2.5-flash"),
                google_api_key=api_key,
                temperature=0.1
            )
            
            prompt = f"PR Title: {state.get('pr_title', '')}\n\nGIT DIFF:\n{truncated_diff}"
            response = llm.invoke([
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ])
            
            content = response.content.strip()
            # Clean json code block markers if present
            if content.startswith("```"):
                content = re.sub(r"^```(?:json)?\n?", "", content)
                content = re.sub(r"\n?```$", "", content)
                
            raw_findings = json.loads(content)
            for item in raw_findings:
                findings.append({
                    "file": str(item.get("file", "Unknown")),
                    "line": str(item.get("line", "N/A")),
                    "category": str(item.get("category", "other")),
                    "severity": str(item.get("severity", "MEDIUM")).upper(),
                    "description": str(item.get("description", "")),
                    "suggestion": str(item.get("suggestion", ""))
                })
            print(f"✨ [review_pr] LLM analysis completed: found {len(findings)} findings.")
        except Exception as e:
            print(f"⚠️ [review_pr] LLM call failed ({e}). Falling back to heuristic analysis.")
            findings = heuristic_diff_analysis(diff, files)
    else:
        print("ℹ️ [review_pr] No API key detected in environment. Using heuristic diff analyzer.")
        findings = heuristic_diff_analysis(diff, files)
        
    return {
        **state,
        "findings": findings
    }
