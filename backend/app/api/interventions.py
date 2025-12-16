"""
Interventions API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.api.deps import get_db, get_current_user
from app.schemas.intervention import (
    InterventionResponse, InterventionSessionCreate,
    InterventionSessionComplete, InterventionSessionResponse,
    RecommendationRequest
)
from app.services.intervention import InterventionService
from app.services.recommendation import RecommendationService
from app.models.user import User

router = APIRouter(prefix="/interventions", tags=["Interventions"])


@router.get("/", response_model=List[InterventionResponse])
def get_interventions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    therapeutic_approach: Optional[str] = None,
    max_duration_seconds: Optional[int] = None,
    target_emotion: Optional[str] = None,
    adhd_friendly: Optional[bool] = None,
    asd_friendly: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get intervention library with optional filters"""
    # Filter premium if user is not premium
    is_premium = None if current_user.is_premium else False

    interventions = InterventionService.get_all_interventions(
        db=db,
        skip=skip,
        limit=limit,
        therapeutic_approach=therapeutic_approach,
        max_duration=max_duration_seconds,
        target_emotion=target_emotion,
        adhd_friendly=adhd_friendly,
        asd_friendly=asd_friendly,
        is_premium=is_premium
    )
    return interventions


@router.post("/recommendations")
def get_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get personalized intervention recommendations"""
    recommendations = RecommendationService.get_recommendations(
        db=db,
        user_id=current_user.id,
        current_emotion=request.current_emotion,
        energy_level=request.energy_level,
        time_available_minutes=request.time_available_minutes,
        context=request.context
    )
    return {"recommendations": recommendations}


@router.get("/{intervention_id}", response_model=InterventionResponse)
def get_intervention(
    intervention_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific intervention by ID"""
    intervention = InterventionService.get_intervention_by_id(db, intervention_id)
    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention not found"
        )
    return intervention


@router.post("/sessions", response_model=InterventionSessionResponse, status_code=status.HTTP_201_CREATED)
def start_intervention_session(
    session_data: InterventionSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start an intervention session"""
    # Verify intervention exists
    intervention = InterventionService.get_intervention_by_id(db, session_data.intervention_id)
    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention not found"
        )

    session = InterventionService.start_session(db, current_user.id, session_data)
    return session


@router.post("/sessions/{session_id}/complete", response_model=InterventionSessionResponse)
def complete_intervention_session(
    session_id: UUID,
    completion_data: InterventionSessionComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Complete an intervention session with feedback"""
    session = InterventionService.complete_session(db, session_id, current_user.id, completion_data)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return session


@router.post("/sessions/{session_id}/skip", response_model=InterventionSessionResponse)
def skip_intervention_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Skip an intervention session"""
    session = InterventionService.skip_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return session


@router.get("/sessions/history", response_model=List[InterventionSessionResponse])
def get_session_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's intervention session history"""
    sessions = InterventionService.get_user_sessions(db, current_user.id, skip, limit)
    return sessions


@router.get("/effective")
def get_effective_interventions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get interventions that have been effective for user"""
    effective = InterventionService.get_user_effective_interventions(db, current_user.id)
    return {"effective_interventions": effective}
