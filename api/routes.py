from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from core.issue_processor import IssueProcessor
from api.webhook_handler import WebhookHandler
from config import settings

# Create routers
router = APIRouter()
webhook_handler = WebhookHandler()
processor = IssueProcessor()


# Request/Response models
class IssueData(BaseModel):
    title: str
    body: Optional[str] = None
    user: Dict[str, Any]


class ProcessIssueRequest(BaseModel):
    issue_data: IssueData
    auto_apply: bool = False


class BatchProcessRequest(BaseModel):
    issue_numbers: List[int]
    auto_apply: bool = False


class ProcessResponse(BaseModel):
    success: bool
    issue_number: Optional[int] = None
    analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    actions_applied: bool = False
    summary_comment: Optional[str] = None


class StatsResponse(BaseModel):
    total_issues: int
    open_issues: int
    closed_issues: int
    vector_service_available: bool
    repository: Dict[str, Any]


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "GitHub Issue AI Agent",
        "version": "1.0.0"
    }


# Webhook endpoint
@router.post("/webhook")
async def webhook_endpoint(request):
    """GitHub webhook endpoint."""
    return await webhook_handler.handle_webhook(request)


# Process a single issue
@router.post("/process-issue", response_model=ProcessResponse)
async def process_issue(request: ProcessIssueRequest):
    """Process a single issue with AI analysis."""
    try:
        issue_data = request.issue_data.dict()
        result = processor.process_new_issue(issue_data, request.auto_apply)
        return ProcessResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Process an existing issue by number
@router.post("/process-issue/{issue_number}", response_model=ProcessResponse)
async def process_existing_issue(
    issue_number: int,
    auto_apply: bool = Query(False, description="Automatically apply AI recommendations")
):
    """Process an existing issue by its number."""
    try:
        result = processor.process_existing_issue(issue_number, auto_apply)
        return ProcessResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get recommendations for an issue
@router.post("/recommendations")
async def get_recommendations(request: ProcessIssueRequest):
    """Get AI recommendations for an issue without applying them."""
    try:
        issue_data = request.issue_data.dict()
        result = processor.get_issue_recommendations(issue_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Batch process multiple issues
@router.post("/batch-process")
async def batch_process_issues(request: BatchProcessRequest):
    """Process multiple issues in batch."""
    try:
        result = processor.batch_process_issues(request.issue_numbers, request.auto_apply)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get processing statistics
@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get processing statistics."""
    try:
        stats = processor.get_processing_stats()
        if "error" in stats:
            raise HTTPException(status_code=500, detail=stats["error"])
        return StatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get repository information
@router.get("/repository")
async def get_repository_info():
    """Get repository information and context."""
    try:
        repo_context = processor.github_service.get_repository_context()
        return {
            "success": True,
            "repository": repo_context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get available labels
@router.get("/labels")
async def get_labels():
    """Get all available labels in the repository."""
    try:
        labels = processor.github_service.get_labels()
        return {
            "success": True,
            "labels": [{"name": label.name, "color": label.color, "description": label.description} for label in labels]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get contributors
@router.get("/contributors")
async def get_contributors():
    """Get repository contributors."""
    try:
        contributors = processor.github_service.get_contributors()
        return {
            "success": True,
            "contributors": [{"login": user.login, "id": user.id, "type": user.type} for user in contributors]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Webhook configuration info
@router.get("/webhook-config")
async def get_webhook_config():
    """Get webhook configuration information."""
    return {
        "webhook_url": webhook_handler.get_webhook_url(),
        "webhook_secret": webhook_handler.get_webhook_secret(),
        "events": ["issues"],
        "content_type": "application/json"
    } 