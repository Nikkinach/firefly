"""
Mood Check-in model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class MoodCheckin(Base):
    __tablename__ = "mood_checkins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    # Primary mood data
    mood_score = Column(Integer, nullable=False)  # 1-10
    energy_level = Column(Integer, nullable=False)  # 1-10
    anxiety_level = Column(Integer, nullable=True)  # 1-10
    stress_level = Column(Integer, nullable=True)  # 1-10

    # Emotion tags
    emotion_tags = Column(ARRAY(Text), default=[])

    # Context
    context_location = Column(String(50), nullable=True)
    context_activity = Column(String(100), nullable=True)
    context_social = Column(String(50), nullable=True)

    # Journal
    journal_text = Column(Text, nullable=True)
    journal_sentiment_score = Column(Float, nullable=True)
    journal_emotion_classification = Column(JSONB, nullable=True)

    # Voice recording
    voice_recording_url = Column(Text, nullable=True)
    voice_sentiment_analysis = Column(JSONB, nullable=True)

    # Body scan
    body_scan_data = Column(JSONB, nullable=True)

    # Neurodiversity-specific
    sensory_load_score = Column(Integer, nullable=True)
    executive_function_score = Column(Integer, nullable=True)
    masking_level = Column(Integer, nullable=True)

    # AI analysis
    ai_emotion_primary = Column(String(50), nullable=True)
    ai_emotion_secondary = Column(String(50), nullable=True)
    ai_confidence_score = Column(Float, nullable=True)
    crisis_risk_score = Column(Float, default=0.0)
    crisis_flagged = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="checkins")
    intervention_sessions = relationship("InterventionSession", back_populates="checkin")
