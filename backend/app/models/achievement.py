"""
User Achievement model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    achievement_type = Column(String(100), nullable=False)
    achieved_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    achievement_data = Column(JSONB, default={})

    # Relationship
    user = relationship("User", back_populates="achievements")
