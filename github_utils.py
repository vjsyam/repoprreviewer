import re
import os
import requests
from typing import Dict, Any, Tuple, List
from dotenv import load_dotenv

load_dotenv()

def parse_pr_url(url: str) -> Tuple[str, str, int]:
    """
    Parses a GitHub PR URL and returns (owner, repo, pr_number).
    Example: https://github.com/psf/requests/pull/6700 -> ('psf', 'requests', 6700)
    """
    pattern = r"github\.com/([^/]+)/([^/]+)/pull/(\d+)"
    match = re.search(pattern, url)
    if not match:
        raise ValueError(f"Invalid GitHub PR URL: '{url}'. Expected format: https://github.com/owner/repo/pull/123")
    
    owner = match.group(1)
    repo = match.group(2)
    pr_number = int(match.group(3))
    return owner, repo, pr_number

def get_github_headers(accept_header: str = "application/vnd.github.v3+json") -> Dict[str, str]:
    headers = {
        "Accept": accept_header,
        "User-Agent": "PR-Reviewer-Agent-Crew"
    }
    token = os.getenv("GITHUB_TOKEN")
    if token and token.strip() and token.strip() != "your_github_token_here":
        headers["Authorization"] = f"token {token.strip()}"
    return headers

def parse_files_from_diff(diff_text: str) -> List[Dict[str, Any]]:
    """
    Parses changed filenames from raw git diff text when API is rate-limited.
    """
    files = []
    # Match diff --git a/path/to/file b/path/to/file
    matches = re.findall(r"diff --git a/(.*?) b/\1", diff_text)
    if not matches:
        matches = re.findall(r"\+\+\+ b/(.*)", diff_text)
    
    unique_files = list(set(matches))
    for fname in unique_files:
        files.append({
            "filename": fname,
            "status": "modified",
            "additions": 0,
            "deletions": 0,
            "changes": 0,
            "patch": ""
        })
    return files

def fetch_pr_details(owner: str, repo: str, pr_number: int) -> Tuple[str, str, List[Dict[str, Any]]]:
    """
    Fetches the PR title, raw diff, and modified files list from GitHub REST API or public .diff URL fallback.
    Returns: (title, diff, files_list)
    """
    headers_api = get_github_headers("application/vnd.github.v3+json")
    headers_diff = get_github_headers("application/vnd.github.v3.diff")
    
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    
    pr_title = f"Pull Request #{pr_number}"
    diff_text = ""
    files_list = []
    
    # 1. Attempt GitHub REST API first
    res_pr = requests.get(api_url, headers=headers_api, timeout=15)
    
    if res_pr.status_code == 200:
        pr_data = res_pr.json()
        pr_title = pr_data.get("title", f"PR #{pr_number}")
        
        # Fetch raw diff via API header
        res_diff = requests.get(api_url, headers=headers_diff, timeout=15)
        if res_diff.status_code == 200:
            diff_text = res_diff.text
            
        # Fetch changed files
        files_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
        res_files = requests.get(files_url, headers=headers_api, timeout=15)
        if res_files.status_code == 200:
            raw_files = res_files.json()
            for f in raw_files:
                files_list.append({
                    "filename": f.get("filename"),
                    "status": f.get("status"),
                    "additions": f.get("additions", 0),
                    "deletions": f.get("deletions", 0),
                    "changes": f.get("changes", 0),
                    "patch": f.get("patch", "")
                })
    
    # 2. Fallback to public web diff if API rate limited or failed
    if not diff_text:
        print("ℹ️ [github_utils] GitHub API rate-limited or unavailable. Using public web diff fallback...")
        diff_url = f"https://github.com/{owner}/{repo}/pull/{pr_number}.diff"
        res_web_diff = requests.get(diff_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        if res_web_diff.status_code == 200 and res_web_diff.text.strip():
            diff_text = res_web_diff.text
            files_list = parse_files_from_diff(diff_text)
        else:
            raise RuntimeError(f"Could not fetch diff for PR #{pr_number}. (HTTP {res_web_diff.status_code})")
            
    return pr_title, diff_text, files_list
