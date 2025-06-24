import logging
from typing import Dict, Any, Optional
from datetime import datetime

from services.github_service import GitHubService
from services.ai_service import AIService
from services.vector_service import VectorService
from models.github import IssueAnalysis
from config import settings


class IssueProcessor:
    """Main processor for handling GitHub issues with AI analysis."""
    
    def __init__(self):
        self.github_service = GitHubService()
        self.ai_service = AIService()
        self.vector_service = VectorService()
        self.logger = logging.getLogger(__name__)
        
        # Initialize repository
        self.github_service.get_repository(
            settings.default_repo_owner,
            settings.default_repo_name
        )
    
    def process_new_issue(self, issue_data: Dict[str, Any], auto_apply: bool = False) -> Dict[str, Any]:
        """Process a new GitHub issue with AI analysis."""
        try:
            self.logger.info(f"Processing new issue #{issue_data.get('number')}")
            
            # Get repository context
            repo_context = self.github_service.get_repository_context()
            
            # Analyze issue with AI
            analysis = self.ai_service.analyze_issue(issue_data, repo_context)
            
            # Store in vector database if available
            if self.vector_service.is_available():
                self._store_issue_in_vector_db(issue_data, analysis)
            
            # Apply actions if auto_apply is enabled
            if auto_apply:
                self._apply_analysis_results(issue_data, analysis)
            
            # Generate summary comment
            summary_comment = self.ai_service.generate_issue_summary(issue_data, analysis)
            
            # Add comment to issue
            self.github_service.add_comment_to_issue(
                issue_data.get('number'),
                summary_comment
            )
            
            return {
                "success": True,
                "issue_number": issue_data.get('number'),
                "analysis": analysis.dict(),
                "actions_applied": auto_apply,
                "summary_comment": summary_comment
            }
            
        except Exception as e:
            self.logger.error(f"Error processing issue: {e}")
            return {
                "success": False,
                "error": str(e),
                "issue_number": issue_data.get('number')
            }
    
    def process_existing_issue(self, issue_number: int, auto_apply: bool = False) -> Dict[str, Any]:
        """Process an existing GitHub issue."""
        try:
            # Get issue data
            issue = self.github_service.get_issue(issue_number)
            issue_data = {
                "number": issue.number,
                "title": issue.title,
                "body": issue.body,
                "user": {
                    "login": issue.user.login,
                    "id": issue.user.id,
                    "avatar_url": issue.user.avatar_url,
                    "type": issue.user.type
                },
                "created_at": issue.created_at.isoformat(),
                "updated_at": issue.updated_at.isoformat(),
                "state": issue.state,
                "labels": [label.name for label in issue.labels],
                "assignees": [assignee.login for assignee in issue.assignees]
            }
            
            return self.process_new_issue(issue_data, auto_apply)
            
        except Exception as e:
            self.logger.error(f"Error processing existing issue #{issue_number}: {e}")
            return {
                "success": False,
                "error": str(e),
                "issue_number": issue_number
            }
    
    def _apply_analysis_results(self, issue_data: Dict[str, Any], analysis: IssueAnalysis) -> None:
        """Apply the AI analysis results to the GitHub issue."""
        issue_number = issue_data.get('number')
        
        # Add labels
        if analysis.suggested_labels:
            self.github_service.add_labels_to_issue(issue_number, analysis.suggested_labels)
            self.logger.info(f"Added labels to issue #{issue_number}: {analysis.suggested_labels}")
        
        # Assign issue
        if analysis.suggested_assignee:
            self.github_service.assign_issue(issue_number, analysis.suggested_assignee)
            self.logger.info(f"Assigned issue #{issue_number} to {analysis.suggested_assignee}")
    
    def _store_issue_in_vector_db(self, issue_data: Dict[str, Any], analysis: IssueAnalysis) -> None:
        """Store issue data in vector database for future reference."""
        try:
            # Create a simple embedding (in a real implementation, you'd use an embedding model)
            # For now, we'll use a placeholder
            issue_text = f"{issue_data.get('title', '')} {issue_data.get('body', '')}"
            # This is a placeholder - in practice you'd use an embedding model
            embeddings = [0.1] * 1536  # Placeholder embedding
            
            self.vector_service.store_issue_context(
                str(issue_data.get('number')),
                issue_data,
                embeddings
            )
            self.logger.info(f"Stored issue #{issue_data.get('number')} in vector database")
        except Exception as e:
            self.logger.warning(f"Failed to store issue in vector database: {e}")
    
    def get_issue_recommendations(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get recommendations for an issue without applying them."""
        try:
            repo_context = self.github_service.get_repository_context()
            analysis = self.ai_service.analyze_issue(issue_data, repo_context)
            
            # Get similar issues if vector service is available
            similar_issues = []
            if self.vector_service.is_available():
                # Placeholder embeddings - in practice use an embedding model
                query_embeddings = [0.1] * 1536
                similar_issues = self.vector_service.search_similar_issues(query_embeddings)
            
            return {
                "success": True,
                "analysis": analysis.dict(),
                "similar_issues": similar_issues,
                "repo_context": {
                    "labels": repo_context.get('labels', []),
                    "contributors": repo_context.get('contributors', []),
                    "topics": repo_context.get('topics', [])
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting recommendations: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def batch_process_issues(self, issue_numbers: list, auto_apply: bool = False) -> Dict[str, Any]:
        """Process multiple issues in batch."""
        results = []
        successful = 0
        failed = 0
        
        for issue_number in issue_numbers:
            result = self.process_existing_issue(issue_number, auto_apply)
            results.append(result)
            
            if result.get('success'):
                successful += 1
            else:
                failed += 1
        
        return {
            "total_processed": len(issue_numbers),
            "successful": successful,
            "failed": failed,
            "results": results
        }
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        try:
            all_issues = self.github_service.get_all_issues()
            open_issues = [issue for issue in all_issues if issue.state == 'open']
            closed_issues = [issue for issue in all_issues if issue.state == 'closed']
            
            return {
                "total_issues": len(all_issues),
                "open_issues": len(open_issues),
                "closed_issues": len(closed_issues),
                "vector_service_available": self.vector_service.is_available(),
                "repository": {
                    "name": self.github_service.repo.name if self.github_service.repo else None,
                    "full_name": self.github_service.repo.full_name if self.github_service.repo else None
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting stats: {e}")
            return {
                "error": str(e)
            } 