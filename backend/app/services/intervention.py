"""
Intervention service
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from app.models.intervention import Intervention, InterventionSession
from app.schemas.intervention import InterventionSessionCreate, InterventionSessionComplete
from app.services.ml_training import MLTrainingService


class InterventionService:
    """Handle intervention operations"""

    @staticmethod
    def get_all_interventions(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        therapeutic_approach: Optional[str] = None,
        max_duration: Optional[int] = None,
        target_emotion: Optional[str] = None,
        adhd_friendly: Optional[bool] = None,
        asd_friendly: Optional[bool] = None,
        is_premium: Optional[bool] = None
    ) -> List[Intervention]:
        """Get interventions with optional filters"""
        query = db.query(Intervention).filter(Intervention.is_active == True)

        if therapeutic_approach:
            query = query.filter(Intervention.therapeutic_approach == therapeutic_approach)
        if max_duration:
            query = query.filter(Intervention.duration_seconds <= max_duration)
        if target_emotion:
            query = query.filter(Intervention.target_emotions.contains([target_emotion]))
        if adhd_friendly is not None:
            query = query.filter(Intervention.adhd_friendly == adhd_friendly)
        if asd_friendly is not None:
            query = query.filter(Intervention.asd_friendly == asd_friendly)
        if is_premium is not None:
            query = query.filter(Intervention.is_premium == is_premium)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_intervention_by_id(db: Session, intervention_id: UUID) -> Optional[Intervention]:
        """Get intervention by ID"""
        return db.query(Intervention).filter(Intervention.id == intervention_id).first()

    @staticmethod
    def start_session(
        db: Session,
        user_id: UUID,
        session_data: InterventionSessionCreate
    ) -> InterventionSession:
        """Start an intervention session"""
        session = InterventionSession(
            user_id=user_id,
            intervention_id=session_data.intervention_id,
            checkin_id=session_data.checkin_id,
            started_at=session_data.started_at,
            context_emotion=session_data.context_emotion,
            context_energy_level=session_data.context_energy_level,
            context_time_of_day=session_data.context_time_of_day
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def complete_session(
        db: Session,
        session_id: UUID,
        user_id: UUID,
        completion_data: InterventionSessionComplete
    ) -> Optional[InterventionSession]:
        """Complete an intervention session with feedback"""
        session = db.query(InterventionSession).filter(
            InterventionSession.id == session_id,
            InterventionSession.user_id == user_id
        ).first()

        if not session:
            return None

        session.completed_at = completion_data.completed_at
        session.was_completed = completion_data.was_completed
        session.effectiveness_rating = completion_data.effectiveness_rating
        session.feedback_tags = completion_data.feedback_tags
        session.feedback_text = completion_data.feedback_text

        # Calculate actual duration
        if session.started_at and session.completed_at:
            duration = (session.completed_at - session.started_at).total_seconds()
            session.duration_actual_seconds = int(duration)

        # Update intervention global stats
        intervention = db.query(Intervention).filter(
            Intervention.id == session.intervention_id
        ).first()
        if intervention and session.was_completed:
            intervention.total_completions += 1
            if session.effectiveness_rating:
                # Update running average
                total = intervention.average_rating * (intervention.total_completions - 1)
                intervention.average_rating = (total + session.effectiveness_rating) / intervention.total_completions

        db.commit()
        db.refresh(session)

        # Trigger ML learning if rating was provided
        if session.effectiveness_rating and session.was_completed:
            context = {
                "emotion": session.context_emotion or "unknown",
                "energy_level": session.context_energy_level or 5,
                "time_of_day": session.context_time_of_day or "unknown"
            }
            MLTrainingService.update_intervention_belief(
                db, user_id, session.intervention_id, session.effectiveness_rating, context
            )

            # Check if we should trigger full model training
            InterventionService._check_model_training_trigger(db, user_id)

        return session

    @staticmethod
    def _check_model_training_trigger(db: Session, user_id: UUID) -> None:
        """
        Check if we should trigger full model training.
        Training happens after every 10 interactions or every 5 new rated sessions.
        """
        model = MLTrainingService.get_or_create_user_model(db, user_id)

        # Train after every 10 total interactions
        if model.total_interactions > 0 and model.total_interactions % 10 == 0:
            MLTrainingService.train_user_model(db, user_id)

    @staticmethod
    def skip_session(db: Session, session_id: UUID, user_id: UUID) -> Optional[InterventionSession]:
        """Mark session as skipped"""
        session = db.query(InterventionSession).filter(
            InterventionSession.id == session_id,
            InterventionSession.user_id == user_id
        ).first()

        if not session:
            return None

        session.was_skipped = True
        session.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_user_sessions(
        db: Session,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[InterventionSession]:
        """Get user's intervention session history"""
        return db.query(InterventionSession).filter(
            InterventionSession.user_id == user_id
        ).order_by(desc(InterventionSession.created_at)).offset(skip).limit(limit).all()

    @staticmethod
    def get_user_effective_interventions(db: Session, user_id: UUID) -> List[dict]:
        """Get interventions that work well for user"""
        sessions = db.query(InterventionSession).filter(
            InterventionSession.user_id == user_id,
            InterventionSession.was_completed == True,
            InterventionSession.effectiveness_rating != None
        ).all()

        # Group by intervention and calculate average effectiveness
        intervention_scores = {}
        for session in sessions:
            if session.intervention_id not in intervention_scores:
                intervention_scores[session.intervention_id] = {
                    "total": 0,
                    "count": 0
                }
            intervention_scores[session.intervention_id]["total"] += session.effectiveness_rating
            intervention_scores[session.intervention_id]["count"] += 1

        # Calculate averages and sort
        results = []
        for intervention_id, data in intervention_scores.items():
            avg_score = data["total"] / data["count"]
            if avg_score >= 3.0:  # Only include helpful interventions
                results.append({
                    "intervention_id": intervention_id,
                    "average_effectiveness": avg_score,
                    "times_used": data["count"]
                })

        results.sort(key=lambda x: x["average_effectiveness"], reverse=True)
        return results[:10]  # Top 10
