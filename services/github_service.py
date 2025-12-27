import os
from typing import List, Dict, Any, Optional
from github import Github, GithubException

from config import settings


class GitHubService:
    """Service for interacting with GitHub API."""
    
    def __init__(self):
        self.github = Github(settings.github_access_token)
        self.repo = None
    
    def get_repository(self, owner: str, repo_name: str):
        """Get a GitHub repository."""
        repo_full_name = f"{owner}/{repo_name}"
        self.repo = self.github.get_repo(repo_full_name)
        return self.repo
    
    def get_issue(self, issue_number: int):
        """Get a specific issue by number."""
        if not self.repo:
            raise ValueError("Repository not initialized. Call get_repository() first.")
        return self.repo.get_issue(issue_number)
    
    def get_all_issues(self, state: str = "open") -> List:
        """Get all issues from the repository."""
        if not self.repo:
            raise ValueError("Repository not initialized. Call get_repository() first.")
        return list(self.repo.get_issues(state=state))
    
    def get_labels(self) -> List:
        """Get all labels from the repository."""
        if not self.repo:
            raise ValueError("Repository not initialized. Call get_repository() first.")
        return list(self.repo.get_labels())
    
    def create_label(self, name: str, color: str, description: str = ""):
        """Create a new label."""
        if not self.repo:
            raise ValueError("Repository not initialized. Call get_repository() first.")
        try:
            return self.repo.create_label(name, color, description)
        except GithubException as e:
            if e.status == 422:  # Label already exists
                return self.repo.get_label(name)
            raise
    
    def add_labels_to_issue(self, issue_number: int, labels: List[str]) -> None:
        """Add labels to an issue."""
        if not self.repo:
            raise ValueError("Repository not initialized. Call get_repository() first.")
        issue = self.get_issue(issue_number)
        issue.add_to_labels(*labels)
    
    def assign_issue(self, issue_number: int, assignee: str) -> None:
        """Assign an issue to a user."""
        if not self.repo:
            raise ValueError("Repository not initialized. Call get_repository() first.")
        issue = self.get_issue(issue_number)
        issue.add_to_assignees(assignee)
    
    def add_comment_to_issue(self, issue_number: int, comment: str) -> None:
        """Add a comment to an issue."""
        if not self.repo:
            raise ValueError("Repository not initialized. Call get_repository() first.")
        issue = self.get_issue(issue_number)
        issue.create_comment(comment)
    
    def get_file_content(self, path: str) -> str:
        """Get the content of a specific file."""
        if not self.repo:
            raise ValueError("Repository not initialized. Call get_repository() first.")
        try:
            content = self.repo.get_contents(path)
            if isinstance(content, list):
                raise ValueError(f"Path {path} is a directory, not a file")
            return content.decoded_content.decode('utf-8')
        except GithubException as e:
            if e.status == 404:
                raise FileNotFoundError(f"File {path} not found")
            raise
    
    def get_contributors(self) -> List:
        """Get repository contributors."""
        if not self.repo:
            raise ValueError("Repository not initialized. Call get_repository() first.")
        return list(self.repo.get_contributors())
    
    def get_repository_context(self) -> Dict[str, Any]:
        """Get comprehensive repository context for AI analysis."""
        if not self.repo:
            raise ValueError("Repository not initialized. Call get_repository() first.")
        
        context = {
            "name": self.repo.name,
            "full_name": self.repo.full_name,
            "description": self.repo.description or "No description",
            "topics": list(self.repo.get_topics()),
            "language": self.repo.language or "Unknown",
            "labels": [label.name for label in self.get_labels()],
            "contributors": [user.login for user in self.get_contributors()],
            "files": {}
        }
        
        # Get important files
        important_files = [
            "README.md", "CONTRIBUTING.md", "CHANGELOG.md", 
            "docs/README.md", "docs/CONTRIBUTING.md"
        ]
        
        for file_path in important_files:
            try:
                content = self.get_file_content(file_path)
                context["files"][file_path] = content[:2000]  # Limit content size
            except FileNotFoundError:
                continue
        
        return context 