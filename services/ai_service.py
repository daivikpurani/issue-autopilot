import json
import logging
from typing import Dict, Any, List, Optional
from anthropic import Anthropic

from config import settings
from models.github import IssueAnalysis


class AIService:
    """Service for AI-powered issue analysis using Anthropic Claude."""
    
    def __init__(self):
        self.anthropic = Anthropic(api_key=settings.anthropic_api_key)
        self.logger = logging.getLogger(__name__)
    
    async def analyze_issue(self, issue_data: Dict[str, Any], repo_context: Dict[str, Any]) -> IssueAnalysis:
        """Analyze a GitHub issue using Claude."""
        
        try:
            # Prepare the prompt
            system_prompt = self._create_system_prompt(repo_context)
            user_prompt = self._create_user_prompt(issue_data)
            
            # Get Claude's response
            response = await self.anthropic.completions.create(
                model=settings.model_name,
                max_tokens_to_sample=settings.max_tokens,
                temperature=settings.temperature,
                prompt=f"{system_prompt}\n\n{user_prompt}",
                stop_sequences=["\n\nHuman:", "\n\nAssistant:"]
            )
            
            # Parse the response
            try:
                analysis_data = json.loads(response.completion)
                return IssueAnalysis(**analysis_data)
            except (json.JSONDecodeError, KeyError) as e:
                self.logger.warning(f"Failed to parse JSON response: {e}")
                # Fallback parsing if JSON is malformed
                return self._parse_fallback_response(response.completion, issue_data)
                
        except Exception as e:
            self.logger.error(f"Error in AI analysis: {e}")
            # Return a basic analysis on error
            return self._create_basic_analysis(issue_data)
    
    def _create_system_prompt(self, repo_context: Dict[str, Any]) -> str:
        """Create the system prompt for Claude."""
        return f"""You are an intelligent AI agent named "IssueBot" that analyzes GitHub issues and provides expert recommendations. You have deep knowledge of software development and repository management.

Repository Context:
- Name: {repo_context.get('name', 'Unknown')}
- Description: {repo_context.get('description', 'No description')}
- Language: {repo_context.get('language', 'Unknown')}
- Topics: {', '.join(repo_context.get('topics', []))}
- Available Labels: {', '.join(repo_context.get('labels', []))}
- Contributors: {', '.join(repo_context.get('contributors', []))}

Available Documentation:
{self._format_documentation(repo_context.get('files', {}))}

Your task is to analyze GitHub issues like a senior developer would. You should:

1. **Classify the issue type** (bug, feature, documentation, enhancement, question, etc.)
2. **Assess priority** (low, medium, high, critical) based on impact and urgency
3. **Suggest appropriate labels** from the available list or propose new ones if needed
4. **Recommend an assignee** based on contributor expertise and file ownership
5. **Provide a concise summary** that captures the essence of the issue
6. **Explain your reasoning** for each decision with clear logic
7. **Give a confidence score** (0-1) based on how certain you are

Think step by step:
- First, understand what the issue is about
- Consider the repository context and available resources
- Make informed decisions based on software development best practices
- Explain your thinking process clearly

Respond with a valid JSON object containing:
{{
    "issue_type": "string",
    "priority": "string", 
    "suggested_labels": ["string"],
    "suggested_assignee": "string or null",
    "summary": "string",
    "reasoning": "string",
    "confidence": float
}}

Be thorough but concise. Your analysis should help developers quickly understand and act on the issue."""
    
    def _create_user_prompt(self, issue_data: Dict[str, Any]) -> str:
        """Create the user prompt with issue details."""
        return f"""Please analyze this GitHub issue with your developer expertise:

Title: {issue_data.get('title', 'No title')}
Body: {issue_data.get('body', 'No body')}
Author: {issue_data.get('user', {}).get('login', 'Unknown')}
Created: {issue_data.get('created_at', 'Unknown')}

Provide your analysis in JSON format as specified in the system prompt. Think like a senior developer reviewing this issue."""
    
    def _format_documentation(self, files: Dict[str, str]) -> str:
        """Format documentation files for the prompt."""
        if not files:
            return "No documentation available."
        
        formatted = []
        for file_path, content in files.items():
            # Truncate content to avoid token limits
            truncated_content = content[:800] + "..." if len(content) > 800 else content
            formatted.append(f"File: {file_path}\nContent: {truncated_content}")
        
        return "\n\n".join(formatted)
    
    def _parse_fallback_response(self, response_text: str, issue_data: Dict[str, Any]) -> IssueAnalysis:
        """Fallback parsing if JSON response is malformed."""
        self.logger.info("Using fallback parsing for AI response")
        
        # Try to extract information from the text response
        issue_type = "unknown"
        priority = "medium"
        labels = []
        assignee = None
        summary = response_text[:200] if response_text else "No analysis available"
        reasoning = "Analysis completed but response format was unexpected"
        confidence = 0.5
        
        # Simple keyword extraction
        text_lower = response_text.lower()
        
        # Issue type detection
        if "bug" in text_lower or "error" in text_lower or "fix" in text_lower:
            issue_type = "bug"
        elif "feature" in text_lower or "enhancement" in text_lower or "improvement" in text_lower:
            issue_type = "feature"
        elif "documentation" in text_lower or "docs" in text_lower or "readme" in text_lower:
            issue_type = "documentation"
        elif "question" in text_lower or "help" in text_lower or "support" in text_lower:
            issue_type = "question"
        
        # Priority detection
        if "critical" in text_lower or "urgent" in text_lower or "blocker" in text_lower:
            priority = "critical"
        elif "high" in text_lower or "important" in text_lower:
            priority = "high"
        elif "low" in text_lower or "minor" in text_lower:
            priority = "low"
        
        return IssueAnalysis(
            issue_type=issue_type,
            priority=priority,
            suggested_labels=labels,
            suggested_assignee=assignee,
            summary=summary,
            reasoning=reasoning,
            confidence=confidence
        )
    
    def _create_basic_analysis(self, issue_data: Dict[str, Any]) -> IssueAnalysis:
        """Create a basic analysis when AI service fails."""
        return IssueAnalysis(
            issue_type="unknown",
            priority="medium",
            suggested_labels=[],
            suggested_assignee=None,
            summary=f"Issue: {issue_data.get('title', 'No title')}",
            reasoning="AI analysis service unavailable, using basic classification",
            confidence=0.1
        )
    
    async def generate_issue_summary(self, issue_data: Dict[str, Any], analysis: IssueAnalysis) -> str:
        """Generate a human-readable summary for the issue."""
        summary_template = f"""🤖 **IssueBot Analysis Report**

**Issue Type:** {analysis.issue_type.title()}
**Priority:** {analysis.priority.title()}
**Confidence:** {analysis.confidence:.1%}

**Summary:** {analysis.summary}

**Suggested Labels:** {', '.join(analysis.suggested_labels) if analysis.suggested_labels else 'None'}
**Suggested Assignee:** {analysis.suggested_assignee if analysis.suggested_assignee else 'None'}

**Reasoning:** {analysis.reasoning}

---
*This analysis was performed by IssueBot, an AI development assistant. Please review and adjust as needed.*"""
        
        return summary_template
    
    async def suggest_assignee(self, issue_data: Dict[str, Any], repo_context: Dict[str, Any]) -> Optional[str]:
        """Suggest an assignee based on issue content and repository context."""
        try:
            analysis = await self.analyze_issue(issue_data, repo_context)
            return analysis.suggested_assignee
        except Exception as e:
            self.logger.error(f"Error suggesting assignee: {e}")
            return None 