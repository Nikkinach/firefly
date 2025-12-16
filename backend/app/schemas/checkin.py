"""
Mood Check-in schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class CheckinCreate(BaseModel):
    mood_score: int = Field(..., ge=1, le=10)
    energy_level: int = Field(..., ge=1, le=10)
    anxiety_level: Optional[int] = Field(None, ge=1, le=10)
    stress_level: Optional[int] = Field(None, ge=1, le=10)
    emotion_tags: List[str] = []
    context_location: Optional[str] = None
    context_activity: Optional[str] = None
    context_social: Optional[str] = None
    journal_text: Optional[str] = None
    body_scan_data: Optional[Dict[str, Any]] = None
    sensory_load_score: Optional[int] = Field(None, ge=1, le=10)
    executive_function_score: Optional[int] = Field(None, ge=1, le=10)
    masking_level: Optional[int] = Field(None, ge=1, le=10)


class CheckinResponse(BaseModel):
    id: UUID
    user_id: UUID
    created_at: datetime
    mood_score: int
    energy_level: int
    anxiety_level: Optional[int]
    stress_level: Optional[int]
    emotion_tags: List[str]
    context_location: Optional[str]
    context_activity: Optional[str]
    context_social: Optional[str]
    journal_text: Optional[str]
    body_scan_data: Optional[Dict[str, Any]]
    sensory_load_score: Optional[int]
    executive_function_score: Optional[int]
    masking_level: Optional[int]
    ai_emotion_primary: Optional[str]
    ai_emotion_secondary: Optional[str]
    ai_confidence_score: Optional[float]
    crisis_risk_score: float
    crisis_flagged: bool

    class Config:
        from_attributes = True


class CheckinListResponse(BaseModel):
    checkins: List[CheckinResponse]
    total: int
    page: int
    page_size: int


class CheckinWithRecommendations(BaseModel):
    checkin: CheckinResponse
    recommendations: List["RecommendationResponse"]
    crisis_alert: bool = False


# Forward reference for circular import
from app.schemas.intervention import RecommendationResponse
CheckinWithRecommendations.model_rebuild()
