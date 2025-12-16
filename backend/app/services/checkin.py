"""
Mood Check-in service
"""
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.checkin import MoodCheckin
from app.schemas.checkin import CheckinCreate
from app.services.crisis import CrisisDetectionService
from app.services.ml_training import MLTrainingService


class CheckinService:
    """Handle mood check-in operations"""

    @staticmethod
    def create_checkin(db: Session, user_id: UUID, checkin_data: CheckinCreate) -> MoodCheckin:
        """Create a new mood check-in"""
        checkin = MoodCheckin(
            user_id=user_id,
            mood_score=checkin_data.mood_score,
            energy_level=checkin_data.energy_level,
            anxiety_level=checkin_data.anxiety_level,
            stress_level=checkin_data.stress_level,
            emotion_tags=checkin_data.emotion_tags,
            context_location=checkin_data.context_location,
            context_activity=checkin_data.context_activity,
            context_social=checkin_data.context_social,
            journal_text=checkin_data.journal_text,
            body_scan_data=checkin_data.body_scan_data,
            sensory_load_score=checkin_data.sensory_load_score,
            executive_function_score=checkin_data.executive_function_score,
            masking_level=checkin_data.masking_level
        )

        # Perform crisis detection if journal text exists
        if checkin_data.journal_text:
            crisis_result = CrisisDetectionService.analyze_text(checkin_data.journal_text)
            checkin.crisis_risk_score = crisis_result["risk_score"]
            checkin.crisis_flagged = crisis_result["crisis_flagged"]
            if crisis_result.get("ai_emotion_primary"):
                checkin.ai_emotion_primary = crisis_result["ai_emotion_primary"]

        # Simple emotion detection from tags if no journal
        if not checkin.ai_emotion_primary and checkin_data.emotion_tags:
            checkin.ai_emotion_primary = checkin_data.emotion_tags[0] if checkin_data.emotion_tags else None

        db.add(checkin)
        db.commit()
        db.refresh(checkin)

        # Trigger ML pattern learning after certain milestones
        CheckinService._trigger_ml_learning(db, user_id)

        return checkin

    @staticmethod
    def _trigger_ml_learning(db: Session, user_id: UUID) -> None:
        """
        Trigger ML pattern learning after check-in milestones.
        Learns circadian patterns, triggers, etc.
        """
        # Count total check-ins
        total_checkins = db.query(MoodCheckin).filter(
            MoodCheckin.user_id == user_id
        ).count()

        # Train patterns after every 10 check-ins
        if total_checkins > 0 and total_checkins % 10 == 0:
            MLTrainingService.train_user_model(db, user_id)

        # Also ensure ML model exists
        elif total_checkins == 1:
            # First check-in, initialize the model
            MLTrainingService.get_or_create_user_model(db, user_id)

    @staticmethod
    def get_user_checkins(
        db: Session,
        user_id: UUID,
        skip: int = 0,
        limit: int = 30,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[MoodCheckin]:
        """Get user's check-in history"""
        query = db.query(MoodCheckin).filter(MoodCheckin.user_id == user_id)

        if start_date:
            query = query.filter(MoodCheckin.created_at >= start_date)
        if end_date:
            query = query.filter(MoodCheckin.created_at <= end_date)

        return query.order_by(desc(MoodCheckin.created_at)).offset(skip).limit(limit).all()

    @staticmethod
    def get_checkin_count(
        db: Session,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """Get total count of user checkins"""
        query = db.query(MoodCheckin).filter(MoodCheckin.user_id == user_id)
        if start_date:
            query = query.filter(MoodCheckin.created_at >= start_date)
        if end_date:
            query = query.filter(MoodCheckin.created_at <= end_date)
        return query.count()

    @staticmethod
    def get_checkin_by_id(db: Session, checkin_id: UUID, user_id: UUID) -> Optional[MoodCheckin]:
        """Get specific check-in by ID"""
        return db.query(MoodCheckin).filter(
            MoodCheckin.id == checkin_id,
            MoodCheckin.user_id == user_id
        ).first()

    @staticmethod
    def get_streak_length(db: Session, user_id: UUID) -> int:
        """Calculate current check-in streak"""
        today = datetime.now(timezone.utc).date()
        streak = 0
        current_date = today

        while True:
            # Check if there's a checkin for current_date
            # Use timezone-aware datetimes for comparison
            start_of_day = datetime.combine(current_date, datetime.min.time(), tzinfo=timezone.utc)
            end_of_day = start_of_day + timedelta(days=1)

            has_checkin = db.query(MoodCheckin).filter(
                MoodCheckin.user_id == user_id,
                MoodCheckin.created_at >= start_of_day,
                MoodCheckin.created_at < end_of_day
            ).first() is not None

            if has_checkin:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break

        return streak

    @staticmethod
    def get_average_mood(db: Session, user_id: UUID, days: int = 7) -> Optional[float]:
        """Get average mood score over specified days"""
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        checkins = db.query(MoodCheckin).filter(
            MoodCheckin.user_id == user_id,
            MoodCheckin.created_at >= start_date
        ).all()

        if not checkins:
            return None

        return sum(c.mood_score for c in checkins) / len(checkins)

    @staticmethod
    def get_mood_trend(db: Session, user_id: UUID) -> str:
        """Determine mood trend (improving, stable, declining)"""
        # Compare last 7 days to previous 7 days
        now = datetime.now(timezone.utc)
        recent_avg = CheckinService.get_average_mood(db, user_id, days=7)

        # Get previous week average
        two_weeks_ago = now - timedelta(days=14)
        one_week_ago = now - timedelta(days=7)

        previous_checkins = db.query(MoodCheckin).filter(
            MoodCheckin.user_id == user_id,
            MoodCheckin.created_at >= two_weeks_ago,
            MoodCheckin.created_at < one_week_ago
        ).all()

        if not previous_checkins or recent_avg is None:
            return "stable"

        previous_avg = sum(c.mood_score for c in previous_checkins) / len(previous_checkins)

        diff = recent_avg - previous_avg
        if diff > 0.5:
            return "improving"
        elif diff < -0.5:
            return "declining"
        return "stable"
