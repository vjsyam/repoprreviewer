from langgraph.graph import StateGraph, START, END
from state import PRReviewState
from nodes import fetch_pr_node, review_pr_node, summarize_pr_node

def build_pr_reviewer_graph():
    """
    Constructs and compiles the 3-node LangGraph workflow:
    fetch_pr -> review_pr -> summarize_pr
    """
    workflow = StateGraph(PRReviewState)
    
    # 1. Register Nodes
    workflow.add_node("fetch_pr", fetch_pr_node)
    workflow.add_node("review_pr", review_pr_node)
    workflow.add_node("summarize_pr", summarize_pr_node)
    
    # 2. Wire Linear Flow
    workflow.add_edge(START, "fetch_pr")
    workflow.add_edge("fetch_pr", "review_pr")
    workflow.add_edge("review_pr", "summarize_pr")
    workflow.add_edge("summarize_pr", END)
    
    # 3. Compile Workflow
    app = workflow.compile()
    return app

# Singleton compiled graph instance
pr_review_graph = build_pr_reviewer_graph()
