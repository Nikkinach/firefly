"""
Machine Learning API endpoints - Insights, predictions, and personalization
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.ml_training import MLTrainingService
from app.services.mood_prediction import MoodPredictionService
from app.services.insights import InsightsService
from app.schemas.ml import (
    MLModelInfo,
    MoodPrediction,
    MoodForecastResponse,
    PatternDetection,
    CrisisRiskAssessment,
    OptimalInterventionTimes,
    DailyInsight,
    WeeklyInsights,
    InterventionEffectivenessReport,
    ComprehensiveReport,
    TrainModelResponse,
    PersonalizedScore,
    UpdateBeliefRequest
)

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


@router.get("/model/info", response_model=MLModelInfo)
def get_ml_model_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get information about user's ML model"""
    model = MLTrainingService.get_or_create_user_model(db, current_user.id)

    patterns_available = []
    if model.circadian_patterns:
        patterns_available.append("circadian_patterns")
    if model.trigger_patterns:
        patterns_available.append("trigger_patterns")
    if model.coping_effectiveness_map:
        patterns_available.append("coping_effectiveness")
    if model.intervention_prior_beliefs:
        patterns_available.append("intervention_beliefs")

    return MLModelInfo(
        user_id=current_user.id,
        model_version=model.model_version,
        total_interactions=model.total_interactions,
        last_model_update=model.last_model_update,
        patterns_available=patterns_available
    )


@router.post("/model/train", response_model=TrainModelResponse)
def train_user_model(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Trigger full model training for current user.
    Learns circadian patterns, triggers, and coping effectiveness.
    """
    result = MLTrainingService.train_user_model(db, current_user.id)
    return result


@router.post("/model/update-belief")
def update_intervention_belief(
    request: UpdateBeliefRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update ML belief about an intervention's effectiveness.
    Called after user rates an intervention session.
    """
    context = {
        "emotion": request.context_emotion or "unknown",
        "energy_level": request.context_energy_level or 5,
        "time_of_day": request.context_time_of_day or "unknown"
    }

    MLTrainingService.update_intervention_belief(
        db,
        current_user.id,
        request.intervention_id,
        request.effectiveness_rating,
        context
    )

    return {"status": "belief_updated", "intervention_id": str(request.intervention_id)}


@router.get("/predict/mood", response_model=MoodPrediction)
def predict_mood(
    hours_ahead: int = Query(default=24, ge=1, le=168),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Predict user's mood for the next N hours.
    Uses exponential smoothing and circadian patterns.
    """
    prediction = MoodPredictionService.predict_next_mood(db, current_user.id, hours_ahead)
    return prediction


@router.get("/predict/forecast")
def get_mood_forecast(
    days: int = Query(default=7, ge=1, le=14),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get mood forecast for the next N days.
    Returns morning, afternoon, and evening predictions.
    """
    from datetime import datetime
    forecasts = MoodPredictionService.get_mood_forecast(db, current_user.id, days)
    return {
        "forecasts": forecasts,
        "generated_at": datetime.utcnow().isoformat()
    }


@router.get("/patterns/mood", response_model=PatternDetection)
def detect_mood_patterns(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Detect patterns in user's mood data.
    Identifies weekly cycles, time-of-day effects, and volatility.
    """
    patterns = MoodPredictionService.detect_mood_patterns(db, current_user.id)
    return patterns


@router.get("/patterns/circadian")
def get_circadian_patterns(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's learned circadian patterns"""
    model = MLTrainingService.get_or_create_user_model(db, current_user.id)
    return model.circadian_patterns or {"message": "No circadian patterns learned yet"}


@router.get("/patterns/triggers")
def get_trigger_patterns(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's learned trigger patterns"""
    model = MLTrainingService.get_or_create_user_model(db, current_user.id)
    return model.trigger_patterns or {"message": "No trigger patterns learned yet"}


@router.get("/risk/crisis", response_model=CrisisRiskAssessment)
def assess_crisis_risk(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Assess crisis risk based on recent patterns.
    NOT a clinical assessment - for informational purposes only.
    """
    assessment = MoodPredictionService.predict_crisis_risk(db, current_user.id)
    return assessment


@router.get("/optimal-times", response_model=OptimalInterventionTimes)
def get_optimal_intervention_times(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get optimal times for interventions based on learned patterns.
    Identifies times when mood is lower but energy is available.
    """
    optimal = MoodPredictionService.get_optimal_intervention_times(db, current_user.id)
    return optimal


@router.get("/insights/daily", response_model=DailyInsight)
def get_daily_insight(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a personalized daily insight based on patterns and current state.
    """
    insight = InsightsService.get_daily_insight(db, current_user.id)
    return insight


@router.get("/insights/weekly")
def get_weekly_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate comprehensive weekly insights.
    Includes mood trends, achievements, and personalized tips.
    """
    insights = InsightsService.generate_weekly_insights(db, current_user.id)
    return insights


@router.get("/insights/effectiveness", response_model=InterventionEffectivenessReport)
def get_intervention_effectiveness(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get report on which interventions are most effective for the user.
    """
    report = InsightsService.get_intervention_effectiveness_report(db, current_user.id)
    return report


@router.get("/insights/comprehensive", response_model=ComprehensiveReport)
def get_comprehensive_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate comprehensive ML insights report.
    Combines all analyses into a single report.
    """
    report = InsightsService.generate_comprehensive_report(db, current_user.id)
    return report


@router.get("/score/intervention")
def get_personalized_intervention_score(
    intervention_id: UUID,
    emotion: str = Query(..., description="Current emotion"),
    energy_level: int = Query(default=5, ge=1, le=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get personalized effectiveness score for an intervention.
    Uses Thompson Sampling and learned patterns.
    """
    from datetime import datetime
    context = {
        "emotion": emotion,
        "energy_level": energy_level,
        "time_of_day": datetime.utcnow().strftime("%p").lower(),
        "hour": datetime.utcnow().hour
    }

    score, explanation = MLTrainingService.get_personalized_score(
        db, current_user.id, intervention_id, emotion, context
    )

    return PersonalizedScore(
        intervention_id=intervention_id,
        score=round(score, 3),
        explanation=explanation
    )


@router.get("/coping-map")
def get_coping_effectiveness_map(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get learned coping effectiveness map.
    Shows which interventions work best for which emotions.
    """
    model = MLTrainingService.get_or_create_user_model(db, current_user.id)
    coping_map = model.coping_effectiveness_map or {}

    if not coping_map or coping_map == {}:
        return {"message": "No coping effectiveness data learned yet. Complete more interventions!"}

    return coping_map
