"""
User service - user management operations
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.user import User, UserPreferences
from app.models.ml_model import UserMLModel
from app.schemas.user import UserCreate, UserUpdate, UserPreferencesCreate, UserPreferencesUpdate
from app.services.auth import AuthService


class UserService:
    """Handle user CRUD operations"""

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user"""
        # Hash password
        password_hash = AuthService.get_password_hash(user_data.password)

        # Create user
        user = User(
            email=user_data.email,
            password_hash=password_hash,
            display_name=user_data.display_name,
            has_adhd=user_data.has_adhd,
            has_autism_spectrum=user_data.has_autism_spectrum,
            has_anxiety=user_data.has_anxiety,
            has_depression=user_data.has_depression,
            other_conditions=user_data.other_conditions,
            age_range=user_data.age_range,
            timezone=user_data.timezone
        )
        db.add(user)
        db.flush()

        # Create default preferences
        preferences = UserPreferences(user_id=user.id)
        # Auto-enable features based on neurodiversity flags
        if user.has_adhd:
            preferences.time_blindness_support = True
            preferences.task_breakdown_auto = True
            preferences.hyperfocus_reminders = True
        if user.has_autism_spectrum:
            preferences.sensory_load_tracking = True
            preferences.routine_deviation_alerts = True
            preferences.reduce_motion = True
        db.add(preferences)

        # Create empty ML model state
        ml_model = UserMLModel(user_id=user.id)
        db.add(ml_model)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def update_user(db: Session, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
        """Update user profile"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_preferences(
        db: Session, user_id: UUID, prefs_data: UserPreferencesUpdate
    ) -> Optional[UserPreferences]:
        """Update user preferences"""
        user = UserService.get_user_by_id(db, user_id)
        if not user or not user.preferences:
            return None

        update_data = prefs_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user.preferences, key, value)

        db.commit()
        db.refresh(user.preferences)
        return user.preferences

    @staticmethod
    def delete_user(db: Session, user_id: UUID) -> bool:
        """Delete user and all associated data (GDPR compliance)"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return False

        db.delete(user)
        db.commit()
        return True

    @staticmethod
    def export_user_data(db: Session, user_id: UUID) -> dict:
        """Export all user data for GDPR/CCPA compliance"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return {}

        # Compile all user data
        data = {
            "user_profile": {
                "email": user.email,
                "display_name": user.display_name,
                "created_at": str(user.created_at),
                "has_adhd": user.has_adhd,
                "has_autism_spectrum": user.has_autism_spectrum,
                "has_anxiety": user.has_anxiety,
                "has_depression": user.has_depression,
                "other_conditions": user.other_conditions,
                "timezone": user.timezone,
            },
            "preferences": {},
            "checkins": [],
            "intervention_sessions": [],
            "achievements": [],
            "weekly_summaries": [],
        }

        # Add preferences
        if user.preferences:
            data["preferences"] = {
                "theme": user.preferences.theme,
                "font_size": user.preferences.font_size,
                "animation_speed": user.preferences.animation_speed,
                "sound_enabled": user.preferences.sound_enabled,
                "morning_checkin_time": user.preferences.morning_checkin_time,
                "evening_reflection_time": user.preferences.evening_reflection_time,
            }

        # Add checkins
        for checkin in user.checkins:
            data["checkins"].append({
                "created_at": str(checkin.created_at),
                "mood_score": checkin.mood_score,
                "energy_level": checkin.energy_level,
                "emotion_tags": checkin.emotion_tags,
                "journal_text": checkin.journal_text,
            })

        # Add intervention sessions
        for session in user.intervention_sessions:
            data["intervention_sessions"].append({
                "created_at": str(session.created_at),
                "intervention_id": str(session.intervention_id),
                "was_completed": session.was_completed,
                "effectiveness_rating": session.effectiveness_rating,
            })

        # Add achievements
        for achievement in user.achievements:
            data["achievements"].append({
                "type": achievement.achievement_type,
                "achieved_at": str(achievement.achieved_at),
            })

        # Add weekly summaries
        for summary in user.weekly_summaries:
            data["weekly_summaries"].append({
                "week_start": str(summary.week_start_date),
                "total_checkins": summary.total_checkins,
                "average_mood": summary.average_mood_score,
                "streak_length": summary.streak_length,
            })

        return data
