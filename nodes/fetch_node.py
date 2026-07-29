import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from state import PRReviewState
from github_utils import parse_pr_url, fetch_pr_details

def fetch_pr_node(state: PRReviewState) -> PRReviewState:
    """
    Node 1: fetch_pr
    Takes a GitHub PR URL from state, retrieves the raw diff, title, and changed file list.
    """
    pr_url = state.get("pr_url", "")
    if not pr_url:
        return {**state, "error": "No pr_url provided in input state."}

    print(f"🔍 [fetch_pr] Fetching PR data for: {pr_url}")
    try:
        owner, repo, pr_number = parse_pr_url(pr_url)
        title, diff, files = fetch_pr_details(owner, repo, pr_number)
        
        print(f"✅ [fetch_pr] Successfully fetched PR #{pr_number}: '{title}' ({len(files)} files changed, diff size: {len(diff)} chars)")
        
        return {
            **state,
            "owner": owner,
            "repo": repo,
            "pr_number": pr_number,
            "pr_title": title,
            "diff": diff,
            "files": files,
            "error": None
        }
    except Exception as e:
        error_msg = f"Failed to fetch PR: {str(e)}"
        print(f"❌ [fetch_pr] Error: {error_msg}")
        return {**state, "error": error_msg}
