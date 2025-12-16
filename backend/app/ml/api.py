"""
API Endpoints for ML Features
Provides endpoints for NLP analysis, predictions, and recommendations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from app.database import get_db
from app.auth import get_current_user
from app.ml.nlp_service import get_nlp_service
from app.ml.prediction_service import get_prediction_service
from app.ml.collaborative_filtering import get_collaborative_filtering_service
from app.ml.models import (
    JournalAnalysis,
    MoodPrediction,
    SeasonalPattern,
    CorrelationAnalysis,
    UserProfile,
    InterventionEffectiveness,
    ABTest
)

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


# ============================================================================
# Request/Response Models
# ============================================================================

class AnalyzeJournalRequest(BaseModel):
    text: str = Field(..., min_length=10)
    journal_entry_id: Optional[int] = None


class AnalyzeJournalResponse(BaseModel):
    sentiment: dict
    emotions: dict
    crisis_detection: dict
    themes: dict
    analyzed_at: str


class TrainModelRequest(BaseModel):
    model_type: str = Field(..., pattern="^(lstm|transformer)$")
    sequence_length: int = Field(14, ge=7, le=60)
    epochs: int = Field(50, ge=10, le=200)


class PredictMoodRequest(BaseModel):
    days_ahead: int = Field(7, ge=1, le=30)
    include_confidence: bool = True


class MoodPredictionResponse(BaseModel):
    date: str
    predicted_mood: float
    confidence_lower: Optional[float]
    confidence_upper: Optional[float]


class InterventionRequest(BaseModel):
    id: str
    name: str
    description: str
    category: str


class RecommendInterventionsRequest(BaseModel):
    available_interventions: List[InterventionRequest]
    n_recommendations: int = Field(5, ge=1, le=20)


class RecordEffectivenessRequest(BaseModel):
    intervention_id: str
    effectiveness_score: float = Field(..., ge=0.0, le=1.0)
    mood_before: Optional[float]
    mood_after: Optional[float]


class CreateABTestRequest(BaseModel):
    test_name: str
    variants: List[dict]
    target_metric: str
    duration_days: int = Field(30, ge=7, le=90)


class RecordABResultRequest(BaseModel):
    test_id: str
    metric_value: float


# ============================================================================
# NLP Endpoints
# ============================================================================

@router.post("/analyze-journal", response_model=AnalyzeJournalResponse)
async def analyze_journal_entry(
    request: AnalyzeJournalRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze a journal entry using NLP
    Performs sentiment analysis, emotion classification, crisis detection, and theme extraction
    """
    try:
        nlp_service = get_nlp_service()
        analysis = await nlp_service.analyze_journal_entry(request.text)

        # Store analysis in database
        if request.journal_entry_id:
            db_analysis = JournalAnalysis(
                journal_entry_id=request.journal_entry_id,
                user_id=current_user["id"],
                sentiment_score=analysis['sentiment']['score'],
                sentiment_label=analysis['sentiment']['label'],
                sentiment_confidence=analysis['sentiment']['confidence'],
                primary_emotion=analysis['emotions']['primary_emotion'],
                primary_emotion_score=analysis['emotions']['primary_score'],
                all_emotions=analysis['emotions']['all_emotions'],
                crisis_detected=analysis['crisis_detection']['crisis_detected'],
                crisis_score=analysis['crisis_detection']['crisis_score'],
                risk_level=analysis['crisis_detection']['risk_level'],
                matched_keywords=analysis['crisis_detection']['matched_keywords'],
                requires_immediate_attention=analysis['crisis_detection']['requires_immediate_attention'],
                themes=analysis['themes'],
                text_length=analysis['text_length'],
                word_count=analysis['word_count']
            )
            db.add(db_analysis)
            db.commit()

        return analysis

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/journal-analyses")
async def get_journal_analyses(
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent journal analyses for the current user"""
    analyses = db.query(JournalAnalysis)\
        .filter(JournalAnalysis.user_id == current_user["id"])\
        .order_by(JournalAnalysis.created_at.desc())\
        .limit(limit)\
        .all()

    return analyses


@router.get("/crisis-alerts")
async def get_crisis_alerts(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get entries that require immediate attention"""
    alerts = db.query(JournalAnalysis)\
        .filter(
            JournalAnalysis.user_id == current_user["id"],
            JournalAnalysis.requires_immediate_attention == True
        )\
        .order_by(JournalAnalysis.analyzed_at.desc())\
        .limit(10)\
        .all()

    return {"alerts": alerts, "count": len(alerts)}


# ============================================================================
# Prediction Endpoints
# ============================================================================

@router.post("/train-model")
async def train_prediction_model(
    request: TrainModelRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Train mood prediction model on user's historical data
    Requires at least 21 days of mood data
    """
    try:
        # Fetch user's mood data (assuming you have a Mood model)
        # This is a placeholder - adjust based on your actual data model
        mood_data = []  # TODO: Fetch from database

        if len(mood_data) < 21:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Need at least 21 days of mood data to train model"
            )

        prediction_service = get_prediction_service()

        if request.model_type == 'lstm':
            result = await prediction_service.train_lstm_model(
                mood_data,
                sequence_length=request.sequence_length,
                epochs=request.epochs
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only LSTM model is currently supported"
            )

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('error', 'Training failed')
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Training failed: {str(e)}"
        )


@router.post("/predict-mood", response_model=List[MoodPredictionResponse])
async def predict_mood(
    request: PredictMoodRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Predict mood for upcoming days
    Model must be trained first
    """
    try:
        # Fetch recent mood data
        recent_data = []  # TODO: Fetch from database

        prediction_service = get_prediction_service()
        result = await prediction_service.predict_mood(
            recent_data,
            days_ahead=request.days_ahead,
            include_confidence=request.include_confidence
        )

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Prediction failed')
            )

        # Store predictions in database
        for pred in result['predictions']:
            db_prediction = MoodPrediction(
                user_id=current_user["id"],
                prediction_date=datetime.fromisoformat(pred['date']),
                predicted_mood=pred['predicted_mood'],
                confidence_lower=pred.get('confidence_lower'),
                confidence_upper=pred.get('confidence_upper'),
                model_type=result['model_type']
            )
            db.add(db_prediction)

        db.commit()

        return result['predictions']

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.get("/predictions")
async def get_predictions(
    limit: int = 30,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get stored mood predictions"""
    predictions = db.query(MoodPrediction)\
        .filter(MoodPrediction.user_id == current_user["id"])\
        .order_by(MoodPrediction.prediction_date.desc())\
        .limit(limit)\
        .all()

    return predictions


@router.get("/seasonal-patterns")
async def detect_seasonal_patterns(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Detect seasonal patterns in mood data
    Requires at least 90 days of data
    """
    try:
        # Fetch mood data
        mood_data = []  # TODO: Fetch from database

        prediction_service = get_prediction_service()
        result = await prediction_service.detect_seasonal_patterns(mood_data)

        if result['patterns_detected']:
            # Store in database
            db_pattern = SeasonalPattern(
                user_id=current_user["id"],
                pattern_type='comprehensive',
                pattern_data=result,
                best_day=result.get('weekly_pattern', {}).get('best_day'),
                worst_day=result.get('weekly_pattern', {}).get('worst_day'),
                weekly_p_value=result.get('weekly_pattern', {}).get('p_value'),
                best_month=result.get('yearly_pattern', {}).get('best_month'),
                worst_month=result.get('yearly_pattern', {}).get('worst_month'),
                dominant_cycles=result.get('dominant_cycles'),
                data_span_days=result.get('data_span_days')
            )
            db.add(db_pattern)
            db.commit()

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pattern detection failed: {str(e)}"
        )


@router.get("/weather-correlation")
async def analyze_weather_correlation(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze correlation between mood and weather
    Requires weather tracking data
    """
    try:
        # Fetch mood and weather data
        mood_data = []  # TODO: Fetch from database
        weather_data = []  # TODO: Fetch from database

        prediction_service = get_prediction_service()
        result = await prediction_service.analyze_weather_correlation(
            mood_data,
            weather_data
        )

        if result['sufficient_data']:
            # Store in database
            db_correlation = CorrelationAnalysis(
                user_id=current_user["id"],
                analysis_type='weather',
                correlation_data=result['correlations'],
                n_data_points=result['n_days']
            )
            db.add(db_correlation)
            db.commit()

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Weather correlation analysis failed: {str(e)}"
        )


@router.get("/sleep-correlation")
async def analyze_sleep_patterns(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze relationship between sleep and mood
    Requires sleep tracking data
    """
    try:
        # Fetch mood and sleep data
        mood_data = []  # TODO: Fetch from database
        sleep_data = []  # TODO: Fetch from database

        prediction_service = get_prediction_service()
        result = await prediction_service.analyze_sleep_patterns(
            mood_data,
            sleep_data
        )

        if result['sufficient_data']:
            # Store in database
            db_correlation = CorrelationAnalysis(
                user_id=current_user["id"],
                analysis_type='sleep',
                correlation_data=result
            )
            db.add(db_correlation)
            db.commit()

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sleep pattern analysis failed: {str(e)}"
        )


# ============================================================================
# Collaborative Filtering Endpoints
# ============================================================================

@router.post("/create-profile")
async def create_user_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create anonymized user profile for collaborative filtering
    Used for personalized recommendations
    """
    try:
        # Fetch user's mood data
        mood_data = []  # TODO: Fetch from database

        cf_service = get_collaborative_filtering_service()
        result = await cf_service.create_user_profile(
            str(current_user["id"]),
            mood_data,
            anonymize=True
        )

        if result['success']:
            # Store in database
            db_profile = UserProfile(
                profile_id=result['profile_id'],
                user_id=current_user["id"],
                features=result['features'],
                n_data_points=len(mood_data)
            )
            db.add(db_profile)
            db.commit()

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile creation failed: {str(e)}"
        )


@router.post("/recommend-interventions")
async def recommend_interventions(
    request: RecommendInterventionsRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized intervention recommendations
    Based on similar users' success with interventions
    """
    try:
        cf_service = get_collaborative_filtering_service()

        # Convert request interventions to list of dicts
        interventions = [i.dict() for i in request.available_interventions]

        result = await cf_service.recommend_interventions(
            str(current_user["id"]),
            interventions,
            n_recommendations=request.n_recommendations
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation failed: {str(e)}"
        )


@router.post("/record-effectiveness")
async def record_intervention_effectiveness(
    request: RecordEffectivenessRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record how effective an intervention was
    Helps improve recommendations for similar users
    """
    try:
        cf_service = get_collaborative_filtering_service()
        result = await cf_service.record_intervention_effectiveness(
            str(current_user["id"]),
            request.intervention_id,
            request.effectiveness_score
        )

        if result['success']:
            # Get user's profile_id
            profile = db.query(UserProfile)\
                .filter(UserProfile.user_id == current_user["id"])\
                .first()

            if profile:
                # Store in database
                db_effectiveness = InterventionEffectiveness(
                    profile_id=profile.profile_id,
                    intervention_id=request.intervention_id,
                    effectiveness_score=request.effectiveness_score,
                    mood_before=request.mood_before,
                    mood_after=request.mood_after,
                    mood_improvement=(request.mood_after - request.mood_before)
                    if request.mood_before and request.mood_after else None
                )
                db.add(db_effectiveness)
                db.commit()

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recording effectiveness failed: {str(e)}"
        )


@router.get("/similar-users")
async def find_similar_users(
    top_k: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """
    Find anonymized profiles of similar users
    Used for understanding patterns in similar populations
    """
    try:
        cf_service = get_collaborative_filtering_service()
        result = await cf_service.find_similar_users(
            str(current_user["id"]),
            top_k=top_k
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Finding similar users failed: {str(e)}"
        )


# ============================================================================
# A/B Testing Endpoints
# ============================================================================

@router.post("/ab-test/create")
async def create_ab_test(
    request: CreateABTestRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create A/B test for new interventions
    Requires admin privileges (add authorization as needed)
    """
    try:
        cf_service = get_collaborative_filtering_service()
        result = await cf_service.create_ab_test(
            request.test_name,
            request.variants,
            request.target_metric,
            request.duration_days
        )

        if result['success']:
            # Store in database
            config = result['config']
            db_test = ABTest(
                test_id=config['test_id'],
                name=config['name'],
                variants=config['variants'],
                target_metric=config['target_metric'],
                status=config['status'],
                start_date=datetime.fromisoformat(config['start_date']),
                end_date=datetime.fromisoformat(config['end_date'])
            )
            db.add(db_test)
            db.commit()

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"A/B test creation failed: {str(e)}"
        )


@router.get("/ab-test/{test_id}/assign")
async def assign_to_ab_test(
    test_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Assign current user to A/B test variant
    Returns assigned variant
    """
    try:
        cf_service = get_collaborative_filtering_service()
        result = await cf_service.assign_user_to_variant(
            test_id,
            str(current_user["id"]),
            method='balanced'
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Variant assignment failed: {str(e)}"
        )


@router.post("/ab-test/record-result")
async def record_ab_test_result(
    request: RecordABResultRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Record A/B test result for current user
    """
    try:
        cf_service = get_collaborative_filtering_service()
        result = await cf_service.record_ab_test_result(
            request.test_id,
            str(current_user["id"]),
            request.metric_value
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recording result failed: {str(e)}"
        )


@router.get("/ab-test/{test_id}/analyze")
async def analyze_ab_test(test_id: str):
    """
    Analyze A/B test results
    Returns statistical analysis and recommendations
    """
    try:
        cf_service = get_collaborative_filtering_service()
        result = await cf_service.analyze_ab_test(test_id)

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"A/B test analysis failed: {str(e)}"
        )


@router.get("/ab-tests")
async def list_ab_tests(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all A/B tests"""
    query = db.query(ABTest)

    if status_filter:
        query = query.filter(ABTest.status == status_filter)

    tests = query.order_by(ABTest.created_at.desc()).all()

    return {"tests": tests, "count": len(tests)}


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def ml_health_check():
    """Check ML services health"""
    try:
        nlp_service = get_nlp_service()
        prediction_service = get_prediction_service()
        cf_service = get_collaborative_filtering_service()

        return {
            "status": "healthy",
            "services": {
                "nlp": "ready",
                "prediction": "ready",
                "collaborative_filtering": "ready"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
