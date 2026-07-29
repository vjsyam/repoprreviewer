from typing import TypedDict, List, Dict, Any, Optional

class Finding(TypedDict):
    file: str
    line: str
    category: str  # hardcoded_secret, missing_input_validation, sql_injection, missing_error_handling
    severity: str  # HIGH, MEDIUM, LOW
    description: str
    suggestion: str

class PRReviewState(TypedDict, total=False):
    pr_url: str
    owner: str
    repo: str
    pr_number: int
    pr_title: str
    diff: str
    files: List[Dict[str, Any]]
    findings: List[Finding]
    summary: str
    error: Optional[str]
