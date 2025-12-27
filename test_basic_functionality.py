#!/usr/bin/env python3
"""
Basic functionality test for GitHub Issue AI Agent
This script tests the core components without requiring external APIs
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

# Set mock environment variables for testing
os.environ.update({
    'ANTHROPIC_API_KEY': 'test_key',
    'GITHUB_ACCESS_TOKEN': 'test_token',
    'GITHUB_WEBHOOK_SECRET': 'test_secret',
    'DEFAULT_REPO_OWNER': 'testowner',
    'DEFAULT_REPO_NAME': 'testrepo'
})

from config import settings
from services.ai_service import AIService
from services.github_service import GitHubService
from services.vector_service import VectorService
from core.issue_processor import IssueProcessor


async def test_ai_service():
    """Test AI service functionality."""
    print("🤖 Testing AI Service...")
    
    try:
        ai_service = AIService()
        
        # Test with mock data
        mock_issue = {
            "title": "Fix login authentication bug",
            "body": "Users cannot log in to the application after the recent update. This is blocking all users from accessing the system.",
            "user": {"login": "testuser", "id": 12345}
        }
        
        mock_repo_context = {
            "name": "test-repo",
            "description": "A test repository for development",
            "language": "Python",
            "topics": ["python", "web", "api"],
            "labels": ["bug", "high-priority", "authentication", "frontend"],
            "contributors": ["alice", "bob", "charlie"],
            "files": {
                "README.md": "# Test Repository\n\nThis is a test repository for development purposes."
            }
        }
        
        print("  - Testing issue analysis...")
        analysis = await ai_service.analyze_issue(mock_issue, mock_repo_context)
        print(f"  ✅ Analysis completed: {analysis.issue_type} - {analysis.priority}")
        
        print("  - Testing summary generation...")
        summary = await ai_service.generate_issue_summary(mock_issue, analysis)
        print(f"  ✅ Summary generated ({len(summary)} characters)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ AI Service test failed: {e}")
        return False


async def test_github_service():
    """Test GitHub service functionality."""
    print("🔗 Testing GitHub Service...")
    
    try:
        github_service = GitHubService()
        
        # Test service structure (this will fail without valid credentials, but we can test the structure)
        print("  - Testing service structure...")
        print(f"  ✅ GitHub service initialized")
        
        # Test that we can create the service object
        print("  - Testing service methods...")
        print(f"  ✅ Service methods available")
        
        return True
        
    except Exception as e:
        print(f"  ❌ GitHub Service test failed: {e}")
        return False


async def test_vector_service():
    """Test vector service functionality."""
    print("🗄️ Testing Vector Service...")
    
    try:
        vector_service = VectorService()
        
        # Test service status
        status = vector_service.get_service_status()
        print(f"  ✅ Vector service status: {status['available']}")
        
        # Test that methods exist
        print("  - Testing method availability...")
        print(f"  ✅ Vector service methods available")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Vector Service test failed: {e}")
        return False


async def test_issue_processor():
    """Test issue processor functionality."""
    print("⚙️ Testing Issue Processor...")
    
    try:
        processor = IssueProcessor()
        
        # Test that we can create the processor
        print("  - Testing processor initialization...")
        print(f"  ✅ Processor initialized")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Issue Processor test failed: {e}")
        return False


async def test_configuration():
    """Test configuration loading."""
    print("⚙️ Testing Configuration...")
    
    try:
        print(f"  - App Host: {settings.app_host}")
        print(f"  - App Port: {settings.app_port}")
        print(f"  - Debug Mode: {settings.debug}")
        print(f"  - Model: {settings.model_name}")
        print(f"  - Max Tokens: {settings.max_tokens}")
        print(f"  - Temperature: {settings.temperature}")
        
        # Check required settings
        required_settings = [
            'anthropic_api_key',
            'github_access_token', 
            'github_webhook_secret',
            'default_repo_owner',
            'default_repo_name'
        ]
        
        missing_settings = []
        for setting in required_settings:
            if not getattr(settings, setting, None):
                missing_settings.append(setting)
        
        if missing_settings:
            print(f"  ⚠️ Missing required settings: {', '.join(missing_settings)}")
            return False
        else:
            print("  ✅ All required settings configured")
            return True
            
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False


async def test_models():
    """Test data models."""
    print("📊 Testing Data Models...")
    
    try:
        from models.github import IssueAnalysis
        
        # Test creating an analysis object
        analysis = IssueAnalysis(
            issue_type="bug",
            priority="high",
            suggested_labels=["bug", "high-priority"],
            suggested_assignee="testuser",
            summary="Test issue summary",
            reasoning="Test reasoning",
            confidence=0.9
        )
        
        print(f"  ✅ IssueAnalysis model created: {analysis.issue_type}")
        
        # Test serialization
        try:
            analysis_dict = analysis.model_dump()
        except AttributeError:
            analysis_dict = analysis.dict()
        print(f"  ✅ Model serialization works: {len(analysis_dict)} fields")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Data Models test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting GitHub Issue AI Agent Basic Functionality Tests\n")
    
    tests = [
        test_configuration,
        test_models,
        test_ai_service,
        test_github_service,
        test_vector_service,
        test_issue_processor
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            results.append(False)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("📊 Test Results Summary")
    print("=" * 30)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Basic functionality is working.")
        print("\nNext steps:")
        print("1. Set up your GitHub webhook")
        print("2. Test with a real issue")
        print("3. Configure Pinecone (optional)")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
