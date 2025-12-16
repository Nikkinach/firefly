"""
Intervention and InterventionSession models
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.core.database import Base


class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Basic info
    name = Column(String(255), nullable=False)
    short_description = Column(Text, nullable=False)
    detailed_instructions = Column(Text, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    effort_level = Column(String(20), nullable=False)  # minimal, low, medium, high
    energy_required = Column(String(20), nullable=False)

    # Categorization
    therapeutic_approach = Column(String(50), nullable=False)  # DBT, ACT, CBT, Mindfulness, Sensory, Physical
    sub_category = Column(String(100), nullable=True)
    target_emotions = Column(ARRAY(Text), default=[])

    # Metadata
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    media_type = Column(String(50), nullable=True)  # text, audio, video, interactive
    media_url = Column(Text, nullable=True)

    # Neurodiversity tags
    adhd_friendly = Column(Boolean, default=True)
    asd_friendly = Column(Boolean, default=True)
    sensory_intensity = Column(String(20), default="moderate")
    requires_verbal = Column(Boolean, default=False)
    requires_movement = Column(Boolean, default=False)

    # Safety
    contraindications = Column(ARRAY(Text), default=[])
    age_appropriate = Column(ARRAY(Text), default=["18+"])

    # Evidence base
    evidence_source = Column(Text, nullable=True)
    evidence_strength = Column(String(20), nullable=True)  # strong, moderate, emerging

    # Global effectiveness
    global_effectiveness_score = Column(Float, default=0.5)
    total_completions = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)

    # Relationships
    sessions = relationship("InterventionSession", back_populates="intervention")


class InterventionSession(Base):
    __tablename__ = "intervention_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    intervention_id = Column(UUID(as_uuid=True), ForeignKey("interventions.id"), nullable=False)
    checkin_id = Column(UUID(as_uuid=True), ForeignKey("mood_checkins.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    # Session data
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_actual_seconds = Column(Integer, nullable=True)
    was_completed = Column(Boolean, default=False)
    was_skipped = Column(Boolean, default=False)

    # User feedback
    effectiveness_rating = Column(Integer, nullable=True)  # 1-5
    feedback_tags = Column(ARRAY(Text), default=[])
    feedback_text = Column(Text, nullable=True)

    # Context at time of recommendation
    context_emotion = Column(String(50), nullable=True)
    context_energy_level = Column(Integer, nullable=True)
    context_time_of_day = Column(String(20), nullable=True)

    # AI learning data
    predicted_effectiveness = Column(Float, nullable=True)
    actual_effectiveness = Column(Float, nullable=True)
    learning_signal = Column(Float, nullable=True)

    # Relationships
    user = relationship("User", back_populates="intervention_sessions")
    intervention = relationship("Intervention", back_populates="sessions")
    checkin = relationship("MoodCheckin", back_populates="intervention_sessions")
