"""
Crisis Event model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.core.database import Base


class CrisisEvent(Base):
    __tablename__ = "crisis_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    # Trigger source
    trigger_source = Column(String(50), nullable=False)  # journal_nlp, checkin, user_reported
    associated_checkin_id = Column(UUID(as_uuid=True), nullable=True)

    # Risk assessment
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)  # low, moderate, high, critical
    crisis_keywords_detected = Column(ARRAY(Text), default=[])

    # Response
    immediate_response_shown = Column(Boolean, default=True)
    hotline_info_displayed = Column(Boolean, default=False)
    safety_plan_accessed = Column(Boolean, default=False)
    emergency_contact_notified = Column(Boolean, default=False)

    # Resolution
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)

    # Follow-up
    follow_up_scheduled = Column(Boolean, default=False)
    follow_up_completed = Column(Boolean, default=False)

    # Relationship
    user = relationship("User", back_populates="crisis_events")
