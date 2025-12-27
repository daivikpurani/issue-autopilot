#!/usr/bin/env python3
"""
Demo script for GitHub Issue AI Agent
This shows the agent working with mock data
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

# Set mock environment variables for demo
os.environ.update({
    'ANTHROPIC_API_KEY': 'demo_key',
    'GITHUB_ACCESS_TOKEN': 'demo_token',
    'GITHUB_WEBHOOK_SECRET': 'demo_secret',
    'DEFAULT_REPO_OWNER': 'demoowner',
    'DEFAULT_REPO_NAME': 'demorepo'
})

from services.ai_service import AIService
from services.vector_service import VectorService


async def demo_ai_analysis():
    """Demonstrate AI analysis capabilities."""
    print("🤖 **IssueBot AI Agent Demo**\n")
    
    # Create AI service
    ai_service = AIService()
    
    # Mock repository context
    repo_context = {
        "name": "awesome-project",
        "description": "A modern web application built with Python and React",
        "language": "Python",
        "topics": ["python", "react", "web", "api", "machine-learning"],
        "labels": ["bug", "feature", "enhancement", "documentation", "high-priority", "low-priority", "frontend", "backend", "api", "security"],
        "contributors": ["alice", "bob", "charlie", "diana", "eve"],
        "files": {
            "README.md": "# Awesome Project\n\nA modern web application with AI capabilities.",
            "CONTRIBUTING.md": "# Contributing\n\nPlease read our contribution guidelines before submitting PRs."
        }
    }
    
    # Sample issues to analyze
    sample_issues = [
        {
            "title": "Fix critical authentication bug in login system",
            "body": "Users are experiencing 500 errors when trying to log in. This is blocking all users from accessing the application. The error occurs in the auth middleware.",
            "user": {"login": "security-team", "id": 123}
        },
        {
            "title": "Add dark mode theme to user interface",
            "body": "Users have requested a dark mode option for better accessibility and user experience. This should include theme switching and persistent user preferences.",
            "user": {"login": "ux-designer", "id": 456}
        },
        {
            "title": "Update API documentation for v2 endpoints",
            "body": "The API documentation is outdated and doesn't cover the new v2 endpoints. Need to add examples and proper error handling documentation.",
            "user": {"login": "tech-writer", "id": 789}
        }
    ]
    
    print("📋 **Repository Context**")
    print(f"Project: {repo_context['name']}")
    print(f"Description: {repo_context['description']}")
    print(f"Language: {repo_context['language']}")
    print(f"Topics: {', '.join(repo_context['topics'])}")
    print(f"Available Labels: {', '.join(repo_context['labels'])}")
    print(f"Contributors: {', '.join(repo_context['contributors'])}\n")
    
    print("🔍 **AI Analysis Examples**\n")
    
    for i, issue in enumerate(sample_issues, 1):
        print(f"--- **Issue #{i}** ---")
        print(f"Title: {issue['title']}")
        print(f"Body: {issue['body'][:100]}...")
        print(f"Author: {issue['user']['login']}")
        
        try:
            # Analyze with AI
            analysis = await ai_service.analyze_issue(issue, repo_context)
            
            print(f"\n🤖 **AI Analysis Results:**")
            print(f"• Type: {analysis.issue_type}")
            print(f"• Priority: {analysis.priority}")
            print(f"• Suggested Labels: {', '.join(analysis.suggested_labels)}")
            print(f"• Suggested Assignee: {analysis.suggested_assignee or 'None'}")
            print(f"• Confidence: {analysis.confidence:.1%}")
            print(f"• Summary: {analysis.summary}")
            print(f"• Reasoning: {analysis.reasoning}")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            # Show fallback analysis
            print(f"\n🤖 **Fallback Analysis:**")
            print(f"• Type: {analysis.issue_type}")
            print(f"• Priority: {analysis.priority}")
            print(f"• Summary: {analysis.summary}")
        
        print("\n" + "="*60 + "\n")
    
    # Show agent capabilities
    print("🚀 **Agent Capabilities**")
    print("✅ Intelligent issue classification")
    print("✅ Priority assessment")
    print("✅ Smart label suggestions")
    print("✅ Contributor assignment recommendations")
    print("✅ Context-aware analysis")
    print("✅ Reasoning and explanations")
    print("✅ Confidence scoring")
    print("✅ Fallback handling")
    
    print("\n🎯 **Next Steps**")
    print("1. Configure real API keys in .env file")
    print("2. Set up GitHub webhook")
    print("3. Test with real repository")
    print("4. Enable Pinecone for vector storage")
    print("5. Deploy to production")


async def demo_vector_service():
    """Demonstrate vector service capabilities."""
    print("\n🗄️ **Vector Service Demo**")
    
    vector_service = VectorService()
    status = vector_service.get_service_status()
    
    print(f"Service Available: {status['available']}")
    print(f"Service Type: {status['service_type']}")
    
    if status['available']:
        print("✅ Vector service is ready for similarity search")
        print("✅ Issue context will be stored for future reference")
        print("✅ Similar issues can be found automatically")
    else:
        print("⚠️ Vector service not configured")
        print("💡 To enable: Set PINECONE_API_KEY and PINECONE_ENVIRONMENT")


async def main():
    """Run the demo."""
    print("🚀 Starting GitHub Issue AI Agent Demo\n")
    
    try:
        await demo_ai_analysis()
        await demo_vector_service()
        
        print("\n🎉 Demo completed successfully!")
        print("\nThe AI agent is ready to process real GitHub issues!")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("This might be due to missing dependencies or configuration issues.")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run demo
    asyncio.run(main())
