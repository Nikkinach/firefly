"""
Weekly Summary model
"""
import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Integer, Float, DateTime, Date, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class WeeklySummary(Base):
    __tablename__ = "weekly_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    week_start_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Aggregated stats
    total_checkins = Column(Integer, default=0)
    average_mood_score = Column(Float, nullable=True)
    mood_trend = Column(String(20), nullable=True)  # improving, stable, declining
    average_energy_level = Column(Float, nullable=True)

    # Top insights
    most_common_emotions = Column(ARRAY(Text), default=[])
    most_effective_interventions = Column(ARRAY(Text), default=[])
    recommended_focus_areas = Column(ARRAY(Text), default=[])

    # Patterns discovered
    best_time_for_checkins = Column(String(20), nullable=True)
    trigger_patterns_identified = Column(JSONB, nullable=True)
    coping_strategies_that_worked = Column(JSONB, nullable=True)

    # Goals progress
    streak_length = Column(Integer, default=0)
    interventions_completed = Column(Integer, default=0)
    skills_practiced = Column(ARRAY(Text), default=[])

    # AI-generated narrative
    summary_narrative = Column(Text, nullable=True)

    # Gamification
    achievements_unlocked = Column(ARRAY(Text), default=[])
    firefly_count = Column(Integer, default=0)

    # Relationship
    user = relationship("User", back_populates="weekly_summaries")
