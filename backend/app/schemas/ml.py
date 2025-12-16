"""
ML and Insights schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class MLModelInfo(BaseModel):
    user_id: UUID
    model_version: int
    total_interactions: int
    last_model_update: Optional[datetime]
    patterns_available: List[str]


class InterventionBelief(BaseModel):
    intervention_id: UUID
    alpha: float
    beta: float
    count: int
    expected_effectiveness: float


class CircadianPattern(BaseModel):
    hourly: Dict[str, Dict[str, float]]
    daily: Dict[str, Dict[str, float]]
    best_hours: List[int]
    worst_hours: List[int]
    best_days: List[str]


class TriggerPattern(BaseModel):
    locations: List[Dict[str, Any]]
    activities: List[Dict[str, Any]]
    social: List[Dict[str, Any]]
    protective_factors: List[Dict[str, Any]]


class MoodPrediction(BaseModel):
    prediction_available: bool
    predicted_mood: Optional[float] = None
    predicted_energy: Optional[float] = None
    prediction_time: Optional[str] = None
    confidence: Optional[float] = None
    trend_direction: Optional[str] = None
    insights: List[str] = []
    based_on_checkins: Optional[int] = None
    reason: Optional[str] = None


class DayForecast(BaseModel):
    date: str
    day: str
    periods: Dict[str, Dict[str, Any]]


class MoodForecastResponse(BaseModel):
    forecasts: List[DayForecast]
    generated_at: str


class PatternDetection(BaseModel):
    patterns_detected: bool
    weekly_cycle: Optional[Dict[str, Any]] = None
    time_of_day_effect: Optional[Dict[str, Any]] = None
    volatility: Optional[Dict[str, Any]] = None
    recent_stability: Optional[Dict[str, Any]] = None
    notable_patterns: List[str] = []
    reason: Optional[str] = None


class CrisisRiskAssessment(BaseModel):
    risk_assessment_available: bool
    risk_level: Optional[str] = None
    risk_score: Optional[float] = None
    risk_factors: List[str] = []
    recommendations: List[str] = []
    assessed_at: Optional[str] = None
    reason: Optional[str] = None


class OptimalInterventionTimes(BaseModel):
    optimal_times_available: bool
    recommended_times: List[Dict[str, Any]] = []
    insight: Optional[str] = None


class DailyInsight(BaseModel):
    insight: str
    type: str
    priority: Optional[int] = None


class Achievement(BaseModel):
    name: str
    description: str
    icon: str


class WeeklyInsights(BaseModel):
    period: str
    generated_at: str
    checkin_summary: Dict[str, Any]
    mood_insights: List[str]
    intervention_insights: List[str]
    personalized_tips: List[str]
    achievements: List[Achievement]
    focus_areas: List[str]


class InterventionEffectivenessItem(BaseModel):
    intervention_id: str
    average_rating: float
    total_uses: int
    best_for_emotion: str
    consistency: float


class InterventionEffectivenessReport(BaseModel):
    report_available: bool
    total_interventions_tried: Optional[int] = None
    total_sessions: Optional[int] = None
    top_interventions: List[InterventionEffectivenessItem] = []
    least_effective: List[InterventionEffectivenessItem] = []
    recommendation: Optional[str] = None
    reason: Optional[str] = None


class ComprehensiveReport(BaseModel):
    report_generated_at: str
    model_version: int
    total_interactions_learned: int
    last_model_update: Optional[str]
    sections: Dict[str, Any]
    key_insights: List[str]


class TrainModelResponse(BaseModel):
    user_id: str
    trained_at: str
    patterns_learned: List[str]
    model_version: int
    total_interactions: int
    circadian_summary: Optional[Dict[str, Any]] = None
    triggers_found: Optional[int] = None
    emotions_mapped: Optional[int] = None


class PersonalizedScore(BaseModel):
    intervention_id: UUID
    score: float
    explanation: str


class UpdateBeliefRequest(BaseModel):
    intervention_id: UUID
    effectiveness_rating: int = Field(..., ge=1, le=5)
    context_emotion: Optional[str] = None
    context_energy_level: Optional[int] = Field(None, ge=1, le=10)
    context_time_of_day: Optional[str] = None
