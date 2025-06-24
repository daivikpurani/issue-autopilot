#!/usr/bin/env python3
"""
Script to set up GitHub webhook for the repository.
"""

import requests
import json
import sys
from config import settings


def setup_webhook():
    """Set up GitHub webhook for the repository."""
    
    # Webhook configuration
    webhook_url = f"http://{settings.app_host}:{settings.app_port}/api/v1/webhook"
    webhook_secret = settings.github_webhook_secret
    
    webhook_data = {
        "name": "web",
        "active": True,
        "events": ["issues"],
        "config": {
            "url": webhook_url,
            "content_type": "application/json",
            "secret": webhook_secret
        }
    }
    
    # GitHub API endpoint
    api_url = f"https://api.github.com/repos/{settings.default_repo_owner}/{settings.default_repo_name}/hooks"
    
    headers = {
        "Authorization": f"token {settings.github_access_token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Setting up webhook for {settings.default_repo_owner}/{settings.default_repo_name}")
        print(f"Webhook URL: {webhook_url}")
        
        # Check if webhook already exists
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            existing_hooks = response.json()
            for hook in existing_hooks:
                if hook["config"]["url"] == webhook_url:
                    print("Webhook already exists!")
                    return
        
        # Create new webhook
        response = requests.post(api_url, headers=headers, json=webhook_data)
        
        if response.status_code == 201:
            print("✅ Webhook created successfully!")
            hook_data = response.json()
            print(f"Webhook ID: {hook_data['id']}")
            print(f"Events: {', '.join(hook_data['events'])}")
        else:
            print(f"❌ Failed to create webhook: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error setting up webhook: {e}")


def test_webhook():
    """Test the webhook by sending a ping event."""
    
    webhook_url = f"http://{settings.app_host}:{settings.app_port}/api/v1/webhook"
    
    # Create a test payload
    test_payload = {
        "zen": "Speak like a human.",
        "hook_id": 123456,
        "hook": {
            "type": "Repository",
            "id": 123456,
            "name": "web",
            "active": True,
            "events": ["issues"],
            "config": {
                "url": webhook_url,
                "content_type": "json"
            }
        },
        "repository": {
            "id": 123456,
            "name": settings.default_repo_name,
            "full_name": f"{settings.default_repo_owner}/{settings.default_repo_name}"
        },
        "sender": {
            "login": "test-user",
            "id": 123456
        }
    }
    
    headers = {
        "X-GitHub-Event": "ping",
        "X-Hub-Signature-256": "sha256=test-signature",
        "Content-Type": "application/json"
    }
    
    try:
        print("Testing webhook...")
        response = requests.post(webhook_url, headers=headers, json=test_payload)
        
        if response.status_code == 200:
            print("✅ Webhook test successful!")
        else:
            print(f"❌ Webhook test failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python setup_webhook.py [setup|test]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "setup":
        setup_webhook()
    elif command == "test":
        test_webhook()
    else:
        print("Unknown command. Use 'setup' or 'test'")
        sys.exit(1)


if __name__ == "__main__":
    main() 