import hmac
import hashlib
import json
import logging
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException, Header
from fastapi.responses import JSONResponse

from core.issue_processor import IssueProcessor
from config import settings


class WebhookHandler:
    """Handler for GitHub webhooks."""
    
    def __init__(self):
        self.processor = IssueProcessor()
        self.logger = logging.getLogger(__name__)
    
    async def handle_webhook(self, request: Request, x_github_event: str = Header(None)) -> JSONResponse:
        """Handle incoming GitHub webhook."""
        try:
            # Verify webhook signature
            if not await self._verify_signature(request):
                raise HTTPException(status_code=401, detail="Invalid signature")
            
            # Get webhook payload
            payload = await request.json()
            
            # Handle different event types
            if x_github_event == "issues":
                return await self._handle_issues_webhook(payload)
            elif x_github_event == "ping":
                return JSONResponse(content={"message": "Webhook received", "status": "pong"}, status_code=200)
            else:
                self.logger.info(f"Unhandled webhook event: {x_github_event}")
                return JSONResponse(content={"message": "Event ignored", "event": x_github_event}, status_code=200)
                
        except Exception as e:
            self.logger.error(f"Error handling webhook: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _verify_signature(self, request: Request) -> bool:
        """Verify GitHub webhook signature."""
        try:
            # Get the signature from headers
            signature = request.headers.get("x-hub-signature-256")
            if not signature:
                self.logger.warning("No signature found in webhook")
                return False
            
            # Get the raw body
            body = await request.body()
            
            # Calculate expected signature
            expected_signature = "sha256=" + hmac.new(
                settings.github_webhook_secret.encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            self.logger.error(f"Error verifying signature: {e}")
            return False
    
    async def _handle_issues_webhook(self, payload: Dict[str, Any]) -> JSONResponse:
        """Handle issues webhook events."""
        action = payload.get("action")
        issue_data = payload.get("issue", {})
        
        self.logger.info(f"Received issues webhook: {action} for issue #{issue_data.get('number')}")
        
        # Only process new issues
        if action == "opened":
            try:
                # Process the new issue
                result = await self.processor.process_new_issue(issue_data, auto_apply=False)
                
                if result.get("success"):
                    return JSONResponse(
                        content={
                            "message": "Issue processed successfully",
                            "issue_number": result.get("issue_number"),
                            "analysis": result.get("analysis"),
                            "agent_action": "analysis_completed"
                        },
                        status_code=200
                    )
                else:
                    return JSONResponse(
                        content={
                            "message": "Failed to process issue",
                            "error": result.get("error"),
                            "agent_action": "analysis_failed"
                        },
                        status_code=500
                    )
            except Exception as e:
                self.logger.error(f"Error processing issue: {e}")
                return JSONResponse(
                    content={
                        "message": "Error processing issue",
                        "error": str(e),
                        "agent_action": "error"
                    },
                    status_code=500
                )
        else:
            # Log other actions but don't process them
            self.logger.info(f"Ignoring issue action: {action}")
            return JSONResponse(
                content={
                    "message": f"Issue action '{action}' ignored",
                    "agent_action": "ignored"
                },
                status_code=200
            )
    
    def get_webhook_url(self) -> str:
        """Get the webhook URL for GitHub configuration."""
        return f"http://{settings.app_host}:{settings.app_port}/api/v1/webhook"
    
    def get_webhook_secret(self) -> str:
        """Get the webhook secret for GitHub configuration."""
        return settings.github_webhook_secret 