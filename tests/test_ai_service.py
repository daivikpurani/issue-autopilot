import pytest
from unittest.mock import Mock, patch
from services.ai_service import AIService
from models.github import IssueAnalysis


class TestAIService:
    """Test cases for AIService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with patch('services.ai_service.settings') as mock_settings:
            mock_settings.anthropic_api_key = "test_key"
            mock_settings.model_name = "claude-3-sonnet-20240229"
            mock_settings.max_tokens = 4000
            mock_settings.temperature = 0.1
            self.ai_service = AIService()
    
    def test_analyze_issue_success(self):
        """Test successful issue analysis."""
        # Mock issue data
        issue_data = {
            "title": "Fix login bug",
            "body": "Users cannot log in to the application",
            "user": {"login": "testuser"}
        }
        
        repo_context = {
            "name": "test-repo",
            "labels": ["bug", "enhancement"],
            "contributors": ["user1", "user2"]
        }
        
        # Mock Claude response
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = '''
        {
            "issue_type": "bug",
            "priority": "high",
            "suggested_labels": ["bug"],
            "suggested_assignee": "user1",
            "summary": "Login functionality is broken",
            "reasoning": "This is clearly a bug affecting user login",
            "confidence": 0.9
        }
        '''
        
        with patch.object(self.ai_service.anthropic.messages, 'create', return_value=mock_response):
            result = self.ai_service.analyze_issue(issue_data, repo_context)
            
            assert isinstance(result, IssueAnalysis)
            assert result.issue_type == "bug"
            assert result.priority == "high"
            assert "bug" in result.suggested_labels
            assert result.suggested_assignee == "user1"
            assert result.confidence == 0.9
    
    def test_analyze_issue_fallback_parsing(self):
        """Test fallback parsing when JSON is malformed."""
        issue_data = {
            "title": "Add new feature",
            "body": "We need a new feature",
            "user": {"login": "testuser"}
        }
        
        repo_context = {
            "name": "test-repo",
            "labels": ["feature"],
            "contributors": ["user1"]
        }
        
        # Mock Claude response with malformed JSON
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "This is a feature request with high priority"
        
        with patch.object(self.ai_service.anthropic.messages, 'create', return_value=mock_response):
            result = self.ai_service.analyze_issue(issue_data, repo_context)
            
            assert isinstance(result, IssueAnalysis)
            assert result.issue_type == "feature"
            assert result.priority == "high"
            assert result.confidence == 0.5
    
    def test_generate_issue_summary(self):
        """Test issue summary generation."""
        issue_data = {
            "title": "Test issue",
            "body": "Test body",
            "user": {"login": "testuser"}
        }
        
        analysis = IssueAnalysis(
            issue_type="bug",
            priority="high",
            suggested_labels=["bug"],
            suggested_assignee="user1",
            summary="This is a test summary",
            reasoning="Test reasoning",
            confidence=0.8
        )
        
        summary = self.ai_service.generate_issue_summary(issue_data, analysis)
        
        assert "AI Analysis Summary" in summary
        assert "Bug" in summary
        assert "High" in summary
        assert "80%" in summary
        assert "user1" in summary
    
    def test_create_system_prompt(self):
        """Test system prompt creation."""
        repo_context = {
            "name": "test-repo",
            "description": "Test repository",
            "language": "Python",
            "topics": ["ai", "github"],
            "labels": ["bug", "feature"],
            "contributors": ["user1", "user2"],
            "files": {"README.md": "Test content"}
        }
        
        prompt = self.ai_service._create_system_prompt(repo_context)
        
        assert "test-repo" in prompt
        assert "Python" in prompt
        assert "bug" in prompt
        assert "feature" in prompt
        assert "user1" in prompt
        assert "user2" in prompt
        assert "README.md" in prompt
    
    def test_create_user_prompt(self):
        """Test user prompt creation."""
        issue_data = {
            "title": "Test title",
            "body": "Test body",
            "user": {"login": "testuser"},
            "created_at": "2023-01-01T00:00:00Z"
        }
        
        prompt = self.ai_service._create_user_prompt(issue_data)
        
        assert "Test title" in prompt
        assert "Test body" in prompt
        assert "testuser" in prompt
        assert "2023-01-01T00:00:00Z" in prompt
    
    def test_format_documentation(self):
        """Test documentation formatting."""
        files = {
            "README.md": "This is a test README",
            "CONTRIBUTING.md": "This is contributing guidelines"
        }
        
        formatted = self.ai_service._format_documentation(files)
        
        assert "README.md" in formatted
        assert "CONTRIBUTING.md" in formatted
        assert "This is a test README" in formatted
        assert "This is contributing guidelines" in formatted
    
    def test_format_documentation_empty(self):
        """Test documentation formatting with empty files."""
        formatted = self.ai_service._format_documentation({})
        
        assert "No documentation available" in formatted 