"""
Database Models for ML Features
Stores analysis results, predictions, user profiles, and A/B test data
"""

import uuid
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base


class JournalAnalysis(Base):
    """Stores NLP analysis results for journal entries"""
    __tablename__ = "journal_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    checkin_id = Column(UUID(as_uuid=True), ForeignKey("mood_checkins.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Sentiment
    sentiment_score = Column(Float)  # 0.0 to 1.0
    sentiment_label = Column(String)  # positive, negative, neutral
    sentiment_confidence = Column(Float)

    # Emotions
    primary_emotion = Column(String)
    primary_emotion_score = Column(Float)
    all_emotions = Column(JSON)  # Dict of all emotion scores

    # Crisis Detection
    crisis_detected = Column(Boolean, default=False)
    crisis_score = Column(Float)  # 0.0 to 1.0
    risk_level = Column(String)  # none, low, moderate, high, critical
    matched_keywords = Column(JSON)  # List of detected crisis keywords
    requires_immediate_attention = Column(Boolean, default=False)

    # Themes
    themes = Column(JSON)  # Extracted themes and keywords

    # Metadata
    text_length = Column(Integer)
    word_count = Column(Integer)
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    # journal_entry = relationship("JournalEntry", back_populates="analyses")


class MoodPrediction(Base):
    """Stores mood predictions for future days"""
    __tablename__ = "mood_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    prediction_date = Column(DateTime(timezone=True), nullable=False)
    predicted_mood = Column(Float, nullable=False)  # Predicted mood score
    confidence_lower = Column(Float)  # Lower confidence interval
    confidence_upper = Column(Float)  # Upper confidence interval

    model_type = Column(String)  # lstm, transformer
    model_version = Column(String)

    # Actual outcome (filled in later)
    actual_mood = Column(Float)
    prediction_error = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SeasonalPattern(Base):
    """Stores detected seasonal patterns"""
    __tablename__ = "seasonal_patterns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    pattern_type = Column(String)  # weekly, monthly, yearly
    pattern_data = Column(JSON)  # Detailed pattern information

    # Weekly patterns
    best_day = Column(String)
    worst_day = Column(String)
    weekly_p_value = Column(Float)

    # Monthly patterns
    best_month = Column(String, nullable=True)
    worst_month = Column(String, nullable=True)

    # Cycle detection
    dominant_cycles = Column(JSON)  # FFT-detected cycles

    data_span_days = Column(Integer)
    confidence_score = Column(Float)

    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CorrelationAnalysis(Base):
    """Stores correlation analysis results"""
    __tablename__ = "correlation_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    analysis_type = Column(String)  # weather, sleep, exercise, etc.
    correlation_data = Column(JSON)  # Detailed correlation results

    # Summary metrics
    primary_correlation = Column(Float)  # Strongest correlation value
    primary_factor = Column(String)  # Factor with strongest correlation
    p_value = Column(Float)
    is_significant = Column(Boolean)

    n_data_points = Column(Integer)
    date_range_start = Column(DateTime(timezone=True))
    date_range_end = Column(DateTime(timezone=True))

    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserProfile(Base):
    """Anonymized user profiles for collaborative filtering"""
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(String, unique=True, index=True)  # Anonymized hash
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    # Feature vector (anonymized behavioral patterns)
    features = Column(JSON, nullable=False)

    # Clustering
    cluster_id = Column(Integer, nullable=True)
    cluster_updated_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    n_data_points = Column(Integer)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class InterventionEffectiveness(Base):
    """Records intervention effectiveness for users"""
    __tablename__ = "intervention_effectiveness"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(String, ForeignKey("user_profiles.profile_id"), nullable=False)
    intervention_id = Column(String, nullable=False)

    effectiveness_score = Column(Float, nullable=False)  # 0.0 to 1.0
    n_uses = Column(Integer, default=1)

    # Metrics
    mood_before = Column(Float)
    mood_after = Column(Float)
    mood_improvement = Column(Float)

    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ABTest(Base):
    """A/B test configurations"""
    __tablename__ = "ab_tests"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)

    variants = Column(JSON, nullable=False)  # List of variant configurations
    target_metric = Column(String, nullable=False)

    status = Column(String, default='active')  # active, paused, completed
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)

    # Results summary
    winner = Column(String, nullable=True)
    statistical_significance = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ABTestAssignment(Base):
    """User assignments to A/B test variants"""
    __tablename__ = "ab_test_assignments"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(String, ForeignKey("ab_tests.test_id"), nullable=False)
    profile_id = Column(String, ForeignKey("user_profiles.profile_id"), nullable=False)

    variant_id = Column(String, nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())


class ABTestResult(Base):
    """Individual results from A/B tests"""
    __tablename__ = "ab_test_results"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(String, ForeignKey("ab_tests.test_id"), nullable=False)
    assignment_id = Column(Integer, ForeignKey("ab_test_assignments.id"), nullable=False)

    metric_value = Column(Float, nullable=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class MLModelVersion(Base):
    """Track ML model versions and performance"""
    __tablename__ = "ml_model_versions"

    id = Column(Integer, primary_key=True, index=True)
    model_type = Column(String, nullable=False)  # lstm, transformer, etc.
    version = Column(String, nullable=False)

    # Model metadata
    architecture = Column(JSON)  # Model architecture details
    hyperparameters = Column(JSON)
    training_data_size = Column(Integer)

    # Performance metrics
    training_loss = Column(Float)
    validation_loss = Column(Float)
    test_metrics = Column(JSON)

    # Model storage
    model_path = Column(String)  # Path to saved model file
    is_active = Column(Boolean, default=True)

    trained_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
