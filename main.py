import sys
import os
import argparse

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
from graph import pr_review_graph
from state import PRReviewState

load_dotenv()

def run_pr_review(pr_url: str):
    print("\n" + "="*70)
    print("🚀 Starting LangGraph PR Reviewer Agent Crew")
    print(f"Target PR: {pr_url}")
    print("="*70 + "\n")
    
    initial_state: PRReviewState = {
        "pr_url": pr_url
    }
    
    # Run the compiled graph
    final_state = pr_review_graph.invoke(initial_state)
    
    summary = final_state.get("summary", "")
    print("\n" + "="*70)
    print("📋 PR REVIEW SUMMARY OUTPUT")
    print("="*70 + "\n")
    print(summary)
    print("\n" + "="*70)
    print("✨ Workflow Complete")
    print("="*70 + "\n")
    return final_state

def main():
    parser = argparse.ArgumentParser(description="Multi-Agent PR Review Tool powered by LangGraph")
    parser.add_argument("pr_url", nargs="?", help="Full GitHub PR URL (e.g. https://github.com/owner/repo/pull/123)")
    
    args = parser.parse_args()
    
    pr_url = args.pr_url
    if not pr_url:
        # Default sample open-source PR for testing if none provided
        pr_url = input("Enter GitHub PR URL (or press Enter for default sample PR 'https://github.com/psf/requests/pull/6700'): ").strip()
        if not pr_url:
            pr_url = "https://github.com/psf/requests/pull/6700"
            
    run_pr_review(pr_url)

if __name__ == "__main__":
    main()
