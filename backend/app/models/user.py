"""
User and UserPreferences models
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime(timezone=True), nullable=True)

    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    subscription_tier = Column(String(50), default="free")

    # Neurodiversity flags
    has_adhd = Column(Boolean, default=False)
    has_autism_spectrum = Column(Boolean, default=False)
    has_anxiety = Column(Boolean, default=False)
    has_depression = Column(Boolean, default=False)
    other_conditions = Column(ARRAY(Text), default=[])

    # Privacy settings
    data_sharing_consent = Column(Boolean, default=False)
    research_participation = Column(Boolean, default=False)
    therapist_sharing_enabled = Column(Boolean, default=False)

    # Account security
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)

    # Age and timezone
    age_range = Column(String(20), nullable=True)
    timezone = Column(String(50), default="UTC")

    # Relationships
    preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    checkins = relationship("MoodCheckin", back_populates="user", cascade="all, delete-orphan")
    intervention_sessions = relationship("InterventionSession", back_populates="user", cascade="all, delete-orphan")
    ml_model = relationship("UserMLModel", back_populates="user", uselist=False, cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    weekly_summaries = relationship("WeeklySummary", back_populates="user", cascade="all, delete-orphan")
    crisis_events = relationship("CrisisEvent", back_populates="user", cascade="all, delete-orphan")


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Visual preferences
    theme = Column(String(50), default="calm_light")
    font_family = Column(String(50), default="Inter")
    font_size = Column(Integer, default=16)
    animation_speed = Column(String(20), default="normal")
    high_contrast = Column(Boolean, default=False)

    # Sensory preferences
    sound_enabled = Column(Boolean, default=True)
    haptic_feedback = Column(Boolean, default=True)
    notification_sound = Column(String(50), default="gentle_chime")
    reduce_motion = Column(Boolean, default=False)

    # Communication preferences
    preferred_language = Column(String(10), default="en")
    communication_style = Column(String(50), default="warm")

    # Notification preferences
    morning_checkin_enabled = Column(Boolean, default=True)
    morning_checkin_time = Column(String(10), default="08:00")
    evening_reflection_enabled = Column(Boolean, default=True)
    evening_reflection_time = Column(String(10), default="20:00")
    max_notifications_per_day = Column(Integer, default=3)
    quiet_hours_start = Column(String(10), default="22:00")
    quiet_hours_end = Column(String(10), default="07:00")

    # ADHD-specific
    time_blindness_support = Column(Boolean, default=False)
    task_breakdown_auto = Column(Boolean, default=False)
    hyperfocus_reminders = Column(Boolean, default=False)
    dopamine_reward_style = Column(String(50), default="standard")

    # Autism-specific
    sensory_load_tracking = Column(Boolean, default=False)
    routine_deviation_alerts = Column(Boolean, default=False)
    emotion_scaffolding_level = Column(Integer, default=1)

    # Relationship
    user = relationship("User", back_populates="preferences")
