#!/usr/bin/env python3
"""
Quick start script for GitHub Issue AI Agent.
This script helps you set up the application step by step.
"""

import os
import sys
import subprocess
import requests
from pathlib import Path


def print_banner():
    """Print the application banner."""
    print("🤖 GitHub Issue AI Agent - Quick Start")
    print("=" * 50)
    print()


def check_python_version():
    """Check if Python version is compatible."""
    print("🔍 Checking Python version...")
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required.")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n📦 Checking dependencies...")
    
    try:
        import anthropic
        print("✅ Anthropic library found")
    except ImportError:
        print("❌ Anthropic library not found")
        return False
    
    try:
        import fastapi
        print("✅ FastAPI library found")
    except ImportError:
        print("❌ FastAPI library not found")
        return False
    
    try:
        import github
        print("✅ PyGithub library found")
    except ImportError:
        print("❌ PyGithub library not found")
        return False
    
    return True


def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def setup_environment():
    """Set up environment file."""
    print("\n⚙️  Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ env.example file not found")
        return False
    
    try:
        # Copy env.example to .env
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        print("✅ Created .env file from env.example")
        print("⚠️  Please edit .env with your actual credentials")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def test_github_connection():
    """Test GitHub API connection."""
    print("\n🔗 Testing GitHub connection...")
    
    try:
        from config import settings
        from services.github_service import GitHubService
        
        github_service = GitHubService()
        github_service.get_repository(settings.default_repo_owner, settings.default_repo_name)
        print("✅ GitHub connection successful")
        return True
    except Exception as e:
        print(f"❌ GitHub connection failed: {e}")
        print("   Please check your GITHUB_ACCESS_TOKEN and repository settings")
        return False


def test_anthropic_connection():
    """Test Anthropic API connection."""
    print("\n🧠 Testing Anthropic connection...")
    
    try:
        from config import settings
        from services.ai_service import AIService
        
        ai_service = AIService()
        print("✅ Anthropic connection successful")
        return True
    except Exception as e:
        print(f"❌ Anthropic connection failed: {e}")
        print("   Please check your ANTHROPIC_API_KEY")
        return False


def start_application():
    """Start the application."""
    print("\n🚀 Starting application...")
    print("   The application will be available at: http://localhost:8000")
    print("   API documentation: http://localhost:8000/docs")
    print("   Press Ctrl+C to stop")
    print()
    
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped")


def main():
    """Main function."""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("\n📦 Installing dependencies...")
        if not install_dependencies():
            sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("\n❌ Please create a .env file manually")
        sys.exit(1)
    
    print("\n" + "="*50)
    print("🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env file with your credentials:")
    print("   - ANTHROPIC_API_KEY")
    print("   - GITHUB_ACCESS_TOKEN")
    print("   - GITHUB_WEBHOOK_SECRET")
    print("   - DEFAULT_REPO_OWNER")
    print("   - DEFAULT_REPO_NAME")
    print("\n2. Test connections:")
    print("   python quick_start.py --test")
    print("\n3. Start the application:")
    print("   python quick_start.py --start")
    print("\n4. Set up webhook:")
    print("   python scripts/setup_webhook.py setup")
    print("="*50)


def test_connections():
    """Test all connections."""
    print_banner()
    print("🧪 Testing connections...")
    
    success = True
    
    if not test_github_connection():
        success = False
    
    if not test_anthropic_connection():
        success = False
    
    if success:
        print("\n✅ All connections successful!")
        print("   You can now start the application")
    else:
        print("\n❌ Some connections failed")
        print("   Please check your credentials in .env")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            test_connections()
        elif sys.argv[1] == "--start":
            start_application()
        else:
            print("Usage: python quick_start.py [--test|--start]")
    else:
        main() 