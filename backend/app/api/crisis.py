"""
Crisis Support API routes
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.services.crisis import CrisisDetectionService
from app.services.audit import AuditService
from app.models.user import User
from app.models.crisis import CrisisEvent
from pydantic import BaseModel


router = APIRouter(prefix="/crisis", tags=["Crisis Support"])


class SafetyPlanRequest(BaseModel):
    warning_signs: list[str] = []
    coping_strategies: list[str] = []
    support_people: list[dict] = []
    professional_contacts: list[dict] = []
    safe_environment_steps: list[str] = []
    reasons_to_live: list[str] = []


@router.get("/resources")
def get_crisis_resources(current_user: User = Depends(get_current_user)):
    """Get crisis resources and hotline information"""
    return CrisisDetectionService.get_crisis_resources()


@router.post("/report")
def report_crisis(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """User self-reports being in crisis"""
    # Create crisis event
    crisis_event = CrisisEvent(
        user_id=current_user.id,
        trigger_source="user_reported",
        risk_score=1.0,
        risk_level="critical",
        immediate_response_shown=True,
        hotline_info_displayed=True
    )
    db.add(crisis_event)
    db.commit()

    # Log the event
    AuditService.log_action(
        db=db,
        action_type="CRISIS_SELF_REPORTED",
        user_id=current_user.id,
        resource_type="crisis_event",
        resource_id=crisis_event.id,
        ip_address=request.client.host if request.client else None
    )

    return {
        "message": "We're here for you. Please reach out to one of these resources immediately.",
        "resources": CrisisDetectionService.get_crisis_resources(),
        "crisis_event_id": crisis_event.id
    }


@router.post("/safe-now")
def mark_safe(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """User confirms they are safe"""
    # Find most recent unresolved crisis event
    recent_crisis = db.query(CrisisEvent).filter(
        CrisisEvent.user_id == current_user.id,
        CrisisEvent.resolved == False
    ).order_by(CrisisEvent.created_at.desc()).first()

    if recent_crisis:
        from datetime import datetime
        recent_crisis.resolved = True
        recent_crisis.resolved_at = datetime.utcnow()
        recent_crisis.resolution_notes = "User marked self as safe"
        db.commit()

    AuditService.log_action(
        db=db,
        action_type="USER_MARKED_SAFE",
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None
    )

    return {
        "message": "We're glad you're safe.",
        "options": [
            "Try a calming exercise",
            "Review your safety plan",
            "Contact someone you trust",
            "Return to app"
        ]
    }


@router.get("/safety-plan")
def get_safety_plan(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's safety plan (stored in preferences or separate table)"""
    # For Phase 1, return a template
    return {
        "warning_signs": [],
        "coping_strategies": [
            "Deep breathing",
            "Call a friend",
            "Go for a walk",
            "Listen to calming music"
        ],
        "support_people": [],
        "professional_contacts": [
            {"name": "988 Suicide & Crisis Lifeline", "number": "988"},
            {"name": "Crisis Text Line", "number": "Text HOME to 741741"}
        ],
        "safe_environment_steps": [],
        "reasons_to_live": []
    }


@router.put("/safety-plan")
def update_safety_plan(
    request: Request,
    plan_data: SafetyPlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user's safety plan"""
    # For Phase 1, just acknowledge the update
    # In production, would store this encrypted

    AuditService.log_action(
        db=db,
        action_type="SAFETY_PLAN_UPDATED",
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None
    )

    return {
        "message": "Safety plan updated successfully",
        "plan": plan_data.model_dump()
    }
