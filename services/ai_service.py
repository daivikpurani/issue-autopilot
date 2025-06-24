import json
from typing import Dict, Any, List, Optional
from anthropic import Anthropic
from langchain.llms import Anthropic as LangChainAnthropic
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import HumanMessage, SystemMessage

from config import settings
from models.github import IssueAnalysis


class AIService:
    """Service for AI-powered issue analysis using Anthropic Claude."""
    
    def __init__(self):
        self.anthropic = Anthropic(api_key=settings.anthropic_api_key)
        self.llm = LangChainAnthropic(
            model=settings.model_name,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            anthropic_api_key=settings.anthropic_api_key
        )
    
    def analyze_issue(self, issue_data: Dict[str, Any], repo_context: Dict[str, Any]) -> IssueAnalysis:
        """Analyze a GitHub issue using Claude."""
        
        # Prepare the prompt
        system_prompt = self._create_system_prompt(repo_context)
        user_prompt = self._create_user_prompt(issue_data)
        
        # Get Claude's response
        response = self.anthropic.messages.create(
            model=settings.model_name,
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
            system=system_prompt,
            messages=[
                HumanMessage(content=user_prompt)
            ]
        )
        
        # Parse the response
        try:
            analysis_data = json.loads(response.content[0].text)
            return IssueAnalysis(**analysis_data)
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback parsing if JSON is malformed
            return self._parse_fallback_response(response.content[0].text, issue_data)
    
    def _create_system_prompt(self, repo_context: Dict[str, Any]) -> str:
        """Create the system prompt for Claude."""
        return f"""You are an AI assistant that analyzes GitHub issues and provides intelligent recommendations for labeling, assignment, and summarization.

Repository Context:
- Name: {repo_context.get('name', 'Unknown')}
- Description: {repo_context.get('description', 'No description')}
- Language: {repo_context.get('language', 'Unknown')}
- Topics: {', '.join(repo_context.get('topics', []))}
- Available Labels: {', '.join(repo_context.get('labels', []))}
- Contributors: {', '.join(repo_context.get('contributors', []))}

Available Documentation:
{self._format_documentation(repo_context.get('files', {}))}

Your task is to analyze GitHub issues and provide:
1. Issue type classification (bug, feature, documentation, enhancement, etc.)
2. Priority assessment (low, medium, high, critical)
3. Appropriate labels from the available list or suggest new ones
4. Suggested assignee based on contributor expertise
5. Concise summary of the issue
6. Reasoning for your decisions
7. Confidence score (0-1)

Respond with a valid JSON object containing:
{{
    "issue_type": "string",
    "priority": "string", 
    "suggested_labels": ["string"],
    "suggested_assignee": "string or null",
    "summary": "string",
    "reasoning": "string",
    "confidence": float
}}"""
    
    def _create_user_prompt(self, issue_data: Dict[str, Any]) -> str:
        """Create the user prompt with issue details."""
        return f"""Please analyze this GitHub issue:

Title: {issue_data.get('title', 'No title')}
Body: {issue_data.get('body', 'No body')}
Author: {issue_data.get('user', {}).get('login', 'Unknown')}
Created: {issue_data.get('created_at', 'Unknown')}

Provide your analysis in JSON format as specified in the system prompt."""
    
    def _format_documentation(self, files: Dict[str, str]) -> str:
        """Format documentation files for the prompt."""
        if not files:
            return "No documentation available."
        
        formatted = []
        for file_path, content in files.items():
            formatted.append(f"File: {file_path}\nContent: {content[:1000]}...")
        
        return "\n\n".join(formatted)
    
    def _parse_fallback_response(self, response_text: str, issue_data: Dict[str, Any]) -> IssueAnalysis:
        """Fallback parsing if JSON response is malformed."""
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
        if "bug" in text_lower:
            issue_type = "bug"
        elif "feature" in text_lower:
            issue_type = "feature"
        elif "documentation" in text_lower:
            issue_type = "documentation"
        elif "enhancement" in text_lower:
            issue_type = "enhancement"
        
        # Priority detection
        if "critical" in text_lower or "urgent" in text_lower:
            priority = "critical"
        elif "high" in text_lower:
            priority = "high"
        elif "low" in text_lower:
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
    
    def generate_issue_summary(self, issue_data: Dict[str, Any], analysis: IssueAnalysis) -> str:
        """Generate a human-readable summary for the issue."""
        summary_template = f"""🤖 **AI Analysis Summary**

**Issue Type:** {analysis.issue_type.title()}
**Priority:** {analysis.priority.title()}
**Confidence:** {analysis.confidence:.1%}

**Summary:** {analysis.summary}

**Suggested Labels:** {', '.join(analysis.suggested_labels) if analysis.suggested_labels else 'None'}
**Suggested Assignee:** {analysis.suggested_assignee if analysis.suggested_assignee else 'None'}

**Reasoning:** {analysis.reasoning}

---
*This analysis was performed by an AI assistant. Please review and adjust as needed.*"""
        
        return summary_template
    
    def suggest_assignee(self, issue_data: Dict[str, Any], repo_context: Dict[str, Any]) -> Optional[str]:
        """Suggest an assignee based on issue content and repository context."""
        # This could be enhanced with more sophisticated logic
        # For now, we'll use the analysis result
        analysis = self.analyze_issue(issue_data, repo_context)
        return analysis.suggested_assignee 