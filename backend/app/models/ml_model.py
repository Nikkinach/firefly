"""
User ML Model state
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserMLModel(Base):
    __tablename__ = "user_ml_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Recommendation engine state
    bandit_model_state = Column(JSONB, default={})
    intervention_prior_beliefs = Column(JSONB, default={})

    # Pattern recognition
    circadian_patterns = Column(JSONB, default={})
    trigger_patterns = Column(JSONB, default={})
    coping_effectiveness_map = Column(JSONB, default={})

    # ADHD time blindness model
    time_estimation_bias = Column(Integer, default=0)
    task_completion_patterns = Column(JSONB, default={})

    # ASD sensory patterns
    sensory_sensitivity_profile = Column(JSONB, default={})
    regulation_strategy_preferences = Column(JSONB, default={})

    # Model metadata
    total_interactions = Column(Integer, default=0)
    last_model_update = Column(DateTime(timezone=True), nullable=True)
    model_version = Column(Integer, default=1)

    # Relationship
    user = relationship("User", back_populates="ml_model")
