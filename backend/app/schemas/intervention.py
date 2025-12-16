"""
Intervention schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class InterventionResponse(BaseModel):
    id: UUID
    name: str
    short_description: str
    detailed_instructions: str
    duration_seconds: int
    effort_level: str
    energy_required: str
    therapeutic_approach: str
    sub_category: Optional[str]
    target_emotions: List[str]
    is_active: bool
    is_premium: bool
    media_type: Optional[str]
    media_url: Optional[str]
    adhd_friendly: bool
    asd_friendly: bool
    sensory_intensity: str
    requires_verbal: bool
    requires_movement: bool
    contraindications: List[str]
    age_appropriate: List[str]
    evidence_source: Optional[str]
    evidence_strength: Optional[str]
    global_effectiveness_score: float
    total_completions: int
    average_rating: float

    class Config:
        from_attributes = True


class InterventionSessionCreate(BaseModel):
    intervention_id: UUID
    checkin_id: Optional[UUID] = None
    started_at: datetime
    context_emotion: Optional[str] = None
    context_energy_level: Optional[int] = None
    context_time_of_day: Optional[str] = None


class InterventionSessionComplete(BaseModel):
    completed_at: datetime
    was_completed: bool = True
    effectiveness_rating: Optional[int] = Field(None, ge=1, le=5)
    feedback_tags: List[str] = []
    feedback_text: Optional[str] = None


class InterventionSessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    intervention_id: UUID
    checkin_id: Optional[UUID]
    created_at: datetime
    started_at: datetime
    completed_at: Optional[datetime]
    duration_actual_seconds: Optional[int]
    was_completed: bool
    was_skipped: bool
    effectiveness_rating: Optional[int]
    feedback_tags: List[str]
    feedback_text: Optional[str]
    context_emotion: Optional[str]
    context_energy_level: Optional[int]
    context_time_of_day: Optional[str]
    predicted_effectiveness: Optional[float]
    actual_effectiveness: Optional[float]

    class Config:
        from_attributes = True


class RecommendationRequest(BaseModel):
    current_emotion: str
    energy_level: int = Field(..., ge=1, le=10)
    time_available_minutes: int = Field(..., ge=1)
    context: Optional[str] = None


class RecommendationResponse(BaseModel):
    intervention_id: UUID
    name: str
    short_description: str
    duration_seconds: int
    effort_level: str
    why_recommended: str
    predicted_effectiveness: float


class InterventionFilterRequest(BaseModel):
    therapeutic_approach: Optional[str] = None
    max_duration_seconds: Optional[int] = None
    energy_level: Optional[str] = None
    target_emotion: Optional[str] = None
    adhd_friendly: Optional[bool] = None
    asd_friendly: Optional[bool] = None
    is_premium: Optional[bool] = None
