from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class GitHubUser(BaseModel):
    """GitHub user model."""
    login: str
    id: int
    avatar_url: str
    type: str


class GitHubLabel(BaseModel):
    """GitHub label model."""
    id: int
    name: str
    color: str
    description: Optional[str] = None


class GitHubIssue(BaseModel):
    """GitHub issue model."""
    id: int
    number: int
    title: str
    body: Optional[str] = None
    state: str
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    user: GitHubUser
    assignee: Optional[GitHubUser] = None
    assignees: List[GitHubUser] = []
    labels: List[GitHubLabel] = []
    repository: Optional[Dict[str, Any]] = None


class GitHubWebhookPayload(BaseModel):
    """GitHub webhook payload model."""
    action: str
    issue: GitHubIssue
    repository: Dict[str, Any]
    sender: GitHubUser


class GitHubComment(BaseModel):
    """GitHub comment model."""
    id: int
    body: str
    user: GitHubUser
    created_at: datetime
    updated_at: datetime


class GitHubFile(BaseModel):
    """GitHub file model."""
    name: str
    path: str
    sha: str
    size: int
    url: str
    html_url: str
    git_url: str
    download_url: Optional[str] = None
    type: str
    content: Optional[str] = None
    encoding: Optional[str] = None


class GitHubBlameEntry(BaseModel):
    """GitHub blame entry model."""
    commit: str
    author: str
    line_number: int
    file_path: str


class IssueAnalysis(BaseModel):
    """AI analysis result for an issue."""
    issue_type: str = Field(description="Type of issue (bug, feature, documentation, etc.)")
    priority: str = Field(description="Priority level (low, medium, high, critical)")
    suggested_labels: List[str] = Field(description="Suggested labels for the issue")
    suggested_assignee: Optional[str] = Field(description="Suggested assignee username")
    summary: str = Field(description="Brief summary of the issue")
    reasoning: str = Field(description="Reasoning behind the analysis")
    confidence: float = Field(description="Confidence score (0-1)") 