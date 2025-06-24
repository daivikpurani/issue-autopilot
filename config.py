import os
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Anthropic Claude API
    anthropic_api_key: str
    
    # GitHub Configuration
    github_access_token: str
    github_webhook_secret: str
    
    # Pinecone Vector Database (Optional)
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    pinecone_index_name: str = "github-issues-context"
    
    # Application Configuration
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True
    
    # Repository Configuration
    default_repo_owner: str
    default_repo_name: str
    
    # AI Configuration
    max_tokens: int = 4000
    temperature: float = 0.1
    model_name: str = "claude-3-sonnet-20240229"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings() 