"""
Mood Check-in API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.api.deps import get_db, get_current_user
from app.schemas.checkin import CheckinCreate, CheckinResponse, CheckinListResponse
from app.schemas.intervention import RecommendationResponse
from app.services.checkin import CheckinService
from app.services.recommendation import RecommendationService
from app.services.crisis import CrisisDetectionService
from app.services.audit import AuditService
from app.models.user import User

router = APIRouter(prefix="/checkins", tags=["Check-ins"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_checkin(
    request: Request,
    checkin_data: CheckinCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new mood check-in and get recommendations"""
    checkin = CheckinService.create_checkin(db, current_user.id, checkin_data)

    # Log the check-in
    AuditService.log_data_access(
        db=db,
        user_id=current_user.id,
        resource_type="mood_checkin",
        resource_id=checkin.id,
        action="CREATE",
        ip_address=request.client.host if request.client else "unknown"
    )

    # Get recommendations
    recommendations = RecommendationService.get_recommendations(
        db=db,
        user_id=current_user.id,
        current_emotion=checkin.ai_emotion_primary or "neutral",
        energy_level=checkin.energy_level,
        time_available_minutes=10,  # Default 10 minutes
        context=checkin.context_activity
    )

    # Check for crisis
    crisis_alert = checkin.crisis_flagged
    crisis_resources = None
    if crisis_alert:
        crisis_resources = CrisisDetectionService.get_crisis_resources()

    return {
        "checkin": CheckinResponse.model_validate(checkin),
        "recommendations": recommendations,
        "crisis_alert": crisis_alert,
        "crisis_resources": crisis_resources
    }


@router.get("/", response_model=CheckinListResponse)
def get_checkins(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=100),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's check-in history"""
    skip = (page - 1) * page_size
    checkins = CheckinService.get_user_checkins(
        db, current_user.id, skip, page_size, start_date, end_date
    )
    total = CheckinService.get_checkin_count(db, current_user.id, start_date, end_date)

    return CheckinListResponse(
        checkins=[CheckinResponse.model_validate(c) for c in checkins],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/stats")
def get_checkin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get check-in statistics"""
    streak = CheckinService.get_streak_length(db, current_user.id)
    avg_mood_7d = CheckinService.get_average_mood(db, current_user.id, days=7)
    avg_mood_30d = CheckinService.get_average_mood(db, current_user.id, days=30)
    mood_trend = CheckinService.get_mood_trend(db, current_user.id)
    total_checkins = CheckinService.get_checkin_count(db, current_user.id)

    return {
        "streak_length": streak,
        "average_mood_7_days": round(avg_mood_7d, 2) if avg_mood_7d else None,
        "average_mood_30_days": round(avg_mood_30d, 2) if avg_mood_30d else None,
        "mood_trend": mood_trend,
        "total_checkins": total_checkins
    }


@router.get("/{checkin_id}", response_model=CheckinResponse)
def get_checkin(
    checkin_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific check-in by ID"""
    checkin = CheckinService.get_checkin_by_id(db, checkin_id, current_user.id)
    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Check-in not found"
        )
    return checkin
