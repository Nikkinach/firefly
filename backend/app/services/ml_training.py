"""
ML Training Service - Personalized learning for each user
Uses Thompson Sampling for intervention recommendations
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from uuid import UUID
import json
import math
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.user import User
from app.models.ml_model import UserMLModel
from app.models.checkin import MoodCheckin
from app.models.intervention import Intervention, InterventionSession


class MLTrainingService:
    """Personalized ML model training and management"""

    @staticmethod
    def get_or_create_user_model(db: Session, user_id: UUID) -> UserMLModel:
        """Get or create ML model for user"""
        model = db.query(UserMLModel).filter(UserMLModel.user_id == user_id).first()
        if not model:
            model = UserMLModel(
                user_id=user_id,
                bandit_model_state={},
                intervention_prior_beliefs={},
                circadian_patterns={},
                trigger_patterns={},
                coping_effectiveness_map={},
                task_completion_patterns={},
                sensory_sensitivity_profile={},
                regulation_strategy_preferences={},
                total_interactions=0,
                model_version=1
            )
            db.add(model)
            db.commit()
            db.refresh(model)
        return model

    @staticmethod
    def update_intervention_belief(
        db: Session,
        user_id: UUID,
        intervention_id: UUID,
        effectiveness_rating: int,
        context: Dict
    ) -> None:
        """
        Update Thompson Sampling beliefs for intervention effectiveness.
        Uses Beta distribution: Beta(alpha, beta) where:
        - alpha = successes + 1
        - beta = failures + 1
        """
        model = MLTrainingService.get_or_create_user_model(db, user_id)

        # Get current beliefs
        beliefs = model.intervention_prior_beliefs or {}
        intervention_key = str(intervention_id)

        # Initialize if new intervention
        if intervention_key not in beliefs:
            beliefs[intervention_key] = {
                "alpha": 1.0,  # Prior success
                "beta": 1.0,   # Prior failure
                "count": 0,
                "contexts": {}
            }

        # Convert rating (1-5) to success probability
        # 4-5 = success, 1-2 = failure, 3 = partial
        if effectiveness_rating >= 4:
            success = 1.0
        elif effectiveness_rating <= 2:
            success = 0.0
        else:
            success = 0.5

        # Update Beta distribution
        beliefs[intervention_key]["alpha"] += success
        beliefs[intervention_key]["beta"] += (1 - success)
        beliefs[intervention_key]["count"] += 1

        # Store context-specific performance
        context_key = MLTrainingService._get_context_key(context)
        if context_key not in beliefs[intervention_key]["contexts"]:
            beliefs[intervention_key]["contexts"][context_key] = {"alpha": 1.0, "beta": 1.0, "count": 0}

        beliefs[intervention_key]["contexts"][context_key]["alpha"] += success
        beliefs[intervention_key]["contexts"][context_key]["beta"] += (1 - success)
        beliefs[intervention_key]["contexts"][context_key]["count"] += 1

        # Update model
        model.intervention_prior_beliefs = beliefs
        model.total_interactions += 1
        model.last_model_update = datetime.utcnow()
        db.commit()

    @staticmethod
    def _get_context_key(context: Dict) -> str:
        """Generate a key for context-specific learning"""
        emotion = context.get("emotion", "unknown")
        energy = context.get("energy_level", 5)
        time_of_day = context.get("time_of_day", "unknown")

        # Bucket energy into low/medium/high
        if energy <= 3:
            energy_bucket = "low"
        elif energy <= 7:
            energy_bucket = "medium"
        else:
            energy_bucket = "high"

        return f"{emotion}_{energy_bucket}_{time_of_day}"

    @staticmethod
    def sample_intervention_effectiveness(
        db: Session,
        user_id: UUID,
        intervention_id: UUID,
        context: Dict
    ) -> float:
        """
        Thompson Sampling: Sample from posterior distribution to estimate effectiveness.
        Returns a value between 0 and 1.
        """
        model = MLTrainingService.get_or_create_user_model(db, user_id)
        beliefs = model.intervention_prior_beliefs or {}
        intervention_key = str(intervention_id)

        if intervention_key not in beliefs:
            # No data yet, use prior (uniform)
            return MLTrainingService._sample_beta(1.0, 1.0)

        belief = beliefs[intervention_key]

        # Check for context-specific belief
        context_key = MLTrainingService._get_context_key(context)
        if context_key in belief["contexts"] and belief["contexts"][context_key]["count"] >= 3:
            # Use context-specific belief if we have enough data
            ctx_belief = belief["contexts"][context_key]
            return MLTrainingService._sample_beta(ctx_belief["alpha"], ctx_belief["beta"])

        # Use general belief
        return MLTrainingService._sample_beta(belief["alpha"], belief["beta"])

    @staticmethod
    def _sample_beta(alpha: float, beta: float) -> float:
        """Sample from Beta distribution using simple approximation"""
        import random
        # Simple beta sampling using transformation
        x = random.gammavariate(alpha, 1)
        y = random.gammavariate(beta, 1)
        return x / (x + y)

    @staticmethod
    def learn_circadian_patterns(db: Session, user_id: UUID) -> Dict:
        """
        Analyze user's check-ins to learn their circadian mood patterns.
        Returns patterns by hour of day and day of week.
        """
        model = MLTrainingService.get_or_create_user_model(db, user_id)

        # Get last 60 days of check-ins
        since = datetime.utcnow() - timedelta(days=60)
        checkins = db.query(MoodCheckin).filter(
            MoodCheckin.user_id == user_id,
            MoodCheckin.created_at >= since
        ).all()

        if len(checkins) < 10:
            return {}

        # Aggregate by hour of day
        hourly_patterns = defaultdict(lambda: {"mood_sum": 0, "energy_sum": 0, "count": 0})
        daily_patterns = defaultdict(lambda: {"mood_sum": 0, "energy_sum": 0, "count": 0})

        for checkin in checkins:
            hour = checkin.created_at.hour
            day = checkin.created_at.strftime("%A")

            hourly_patterns[hour]["mood_sum"] += checkin.mood_score
            hourly_patterns[hour]["energy_sum"] += checkin.energy_level
            hourly_patterns[hour]["count"] += 1

            daily_patterns[day]["mood_sum"] += checkin.mood_score
            daily_patterns[day]["energy_sum"] += checkin.energy_level
            daily_patterns[day]["count"] += 1

        # Calculate averages
        patterns = {
            "hourly": {},
            "daily": {},
            "best_hours": [],
            "worst_hours": [],
            "best_days": [],
            "updated_at": datetime.utcnow().isoformat()
        }

        for hour, data in hourly_patterns.items():
            if data["count"] >= 3:  # Need at least 3 samples
                patterns["hourly"][hour] = {
                    "avg_mood": round(data["mood_sum"] / data["count"], 2),
                    "avg_energy": round(data["energy_sum"] / data["count"], 2),
                    "sample_count": data["count"]
                }

        for day, data in daily_patterns.items():
            if data["count"] >= 3:
                patterns["daily"][day] = {
                    "avg_mood": round(data["mood_sum"] / data["count"], 2),
                    "avg_energy": round(data["energy_sum"] / data["count"], 2),
                    "sample_count": data["count"]
                }

        # Find best/worst times
        if patterns["hourly"]:
            sorted_hours = sorted(
                patterns["hourly"].items(),
                key=lambda x: x[1]["avg_mood"],
                reverse=True
            )
            patterns["best_hours"] = [int(h[0]) for h in sorted_hours[:3]]
            patterns["worst_hours"] = [int(h[0]) for h in sorted_hours[-3:]]

        if patterns["daily"]:
            sorted_days = sorted(
                patterns["daily"].items(),
                key=lambda x: x[1]["avg_mood"],
                reverse=True
            )
            patterns["best_days"] = [d[0] for d in sorted_days[:2]]

        # Save to model
        model.circadian_patterns = patterns
        model.last_model_update = datetime.utcnow()
        db.commit()

        return patterns

    @staticmethod
    def learn_trigger_patterns(db: Session, user_id: UUID) -> Dict:
        """
        Identify patterns that correlate with low mood or high anxiety.
        Looks at context (location, activity, social) and emotions.
        """
        model = MLTrainingService.get_or_create_user_model(db, user_id)

        since = datetime.utcnow() - timedelta(days=90)
        checkins = db.query(MoodCheckin).filter(
            MoodCheckin.user_id == user_id,
            MoodCheckin.created_at >= since
        ).all()

        if len(checkins) < 15:
            return {}

        # Track context correlations with low mood/high anxiety
        location_impact = defaultdict(lambda: {"positive": 0, "negative": 0, "count": 0})
        activity_impact = defaultdict(lambda: {"positive": 0, "negative": 0, "count": 0})
        social_impact = defaultdict(lambda: {"positive": 0, "negative": 0, "count": 0})
        emotion_sequences = []

        for checkin in checkins:
            is_negative = checkin.mood_score <= 4 or (checkin.anxiety_level and checkin.anxiety_level >= 7)
            is_positive = checkin.mood_score >= 7

            if checkin.context_location:
                location_impact[checkin.context_location]["count"] += 1
                if is_negative:
                    location_impact[checkin.context_location]["negative"] += 1
                if is_positive:
                    location_impact[checkin.context_location]["positive"] += 1

            if checkin.context_activity:
                activity_impact[checkin.context_activity]["count"] += 1
                if is_negative:
                    activity_impact[checkin.context_activity]["negative"] += 1
                if is_positive:
                    activity_impact[checkin.context_activity]["positive"] += 1

            if checkin.context_social:
                social_impact[checkin.context_social]["count"] += 1
                if is_negative:
                    social_impact[checkin.context_social]["negative"] += 1
                if is_positive:
                    social_impact[checkin.context_social]["positive"] += 1

            # Track emotion sequence
            if checkin.emotion_tags:
                emotion_sequences.append({
                    "emotions": checkin.emotion_tags,
                    "mood": checkin.mood_score,
                    "timestamp": checkin.created_at
                })

        # Identify triggers (high negative correlation)
        triggers = {"locations": [], "activities": [], "social": [], "protective_factors": []}

        for loc, data in location_impact.items():
            if data["count"] >= 3:
                neg_rate = data["negative"] / data["count"]
                if neg_rate >= 0.6:
                    triggers["locations"].append({"context": loc, "risk_score": round(neg_rate, 2)})
                elif data["positive"] / data["count"] >= 0.6:
                    triggers["protective_factors"].append({"type": "location", "context": loc})

        for act, data in activity_impact.items():
            if data["count"] >= 3:
                neg_rate = data["negative"] / data["count"]
                if neg_rate >= 0.6:
                    triggers["activities"].append({"context": act, "risk_score": round(neg_rate, 2)})
                elif data["positive"] / data["count"] >= 0.6:
                    triggers["protective_factors"].append({"type": "activity", "context": act})

        for soc, data in social_impact.items():
            if data["count"] >= 3:
                neg_rate = data["negative"] / data["count"]
                if neg_rate >= 0.6:
                    triggers["social"].append({"context": soc, "risk_score": round(neg_rate, 2)})
                elif data["positive"] / data["count"] >= 0.6:
                    triggers["protective_factors"].append({"type": "social", "context": soc})

        triggers["updated_at"] = datetime.utcnow().isoformat()

        # Save to model
        model.trigger_patterns = triggers
        model.last_model_update = datetime.utcnow()
        db.commit()

        return triggers

    @staticmethod
    def learn_coping_effectiveness(db: Session, user_id: UUID) -> Dict:
        """
        Learn which interventions are most effective for specific emotions.
        Maps emotion -> intervention -> effectiveness score.
        """
        model = MLTrainingService.get_or_create_user_model(db, user_id)

        # Get all completed intervention sessions with ratings
        sessions = db.query(InterventionSession).filter(
            InterventionSession.user_id == user_id,
            InterventionSession.was_completed == True,
            InterventionSession.effectiveness_rating.isnot(None)
        ).all()

        if len(sessions) < 5:
            return {}

        # Map emotion -> intervention -> ratings
        effectiveness_map = defaultdict(lambda: defaultdict(list))

        for session in sessions:
            if session.context_emotion:
                effectiveness_map[session.context_emotion][str(session.intervention_id)].append(
                    session.effectiveness_rating
                )

        # Calculate average effectiveness
        coping_map = {}
        for emotion, interventions in effectiveness_map.items():
            coping_map[emotion] = {}
            for intervention_id, ratings in interventions.items():
                if len(ratings) >= 2:  # Need at least 2 uses
                    avg_rating = sum(ratings) / len(ratings)
                    coping_map[emotion][intervention_id] = {
                        "avg_effectiveness": round(avg_rating, 2),
                        "usage_count": len(ratings),
                        "reliability": min(len(ratings) / 10, 1.0)  # Confidence grows with usage
                    }

        coping_map["updated_at"] = datetime.utcnow().isoformat()

        # Save to model
        model.coping_effectiveness_map = coping_map
        model.last_model_update = datetime.utcnow()
        db.commit()

        return coping_map

    @staticmethod
    def train_user_model(db: Session, user_id: UUID) -> Dict:
        """
        Run full model training for a user.
        Called periodically or after significant new data.
        """
        results = {
            "user_id": str(user_id),
            "trained_at": datetime.utcnow().isoformat(),
            "patterns_learned": []
        }

        # Learn all patterns
        circadian = MLTrainingService.learn_circadian_patterns(db, user_id)
        if circadian:
            results["patterns_learned"].append("circadian_patterns")
            results["circadian_summary"] = {
                "best_hours": circadian.get("best_hours", []),
                "worst_hours": circadian.get("worst_hours", []),
                "best_days": circadian.get("best_days", [])
            }

        triggers = MLTrainingService.learn_trigger_patterns(db, user_id)
        if triggers:
            results["patterns_learned"].append("trigger_patterns")
            results["triggers_found"] = len(triggers.get("locations", [])) + len(triggers.get("activities", []))

        coping = MLTrainingService.learn_coping_effectiveness(db, user_id)
        if coping:
            results["patterns_learned"].append("coping_effectiveness")
            results["emotions_mapped"] = len([k for k in coping.keys() if k != "updated_at"])

        # Update model version
        model = MLTrainingService.get_or_create_user_model(db, user_id)
        model.model_version += 1
        model.last_model_update = datetime.utcnow()
        db.commit()

        results["model_version"] = model.model_version
        results["total_interactions"] = model.total_interactions

        return results

    @staticmethod
    def get_personalized_score(
        db: Session,
        user_id: UUID,
        intervention_id: UUID,
        emotion: str,
        context: Dict
    ) -> Tuple[float, str]:
        """
        Get personalized effectiveness score for an intervention.
        Combines Thompson Sampling with learned patterns.
        Returns (score, explanation).
        """
        model = MLTrainingService.get_or_create_user_model(db, user_id)

        # Base score from Thompson Sampling
        sampled_score = MLTrainingService.sample_intervention_effectiveness(
            db, user_id, intervention_id, context
        )

        explanation = "Based on your personal usage patterns"

        # Boost from coping effectiveness map
        coping_map = model.coping_effectiveness_map or {}
        if emotion in coping_map and str(intervention_id) in coping_map[emotion]:
            coping_data = coping_map[emotion][str(intervention_id)]
            # Weight by reliability
            coping_score = coping_data["avg_effectiveness"] / 5.0  # Normalize to 0-1
            reliability = coping_data["reliability"]
            sampled_score = (sampled_score * (1 - reliability) + coping_score * reliability)

            if coping_data["avg_effectiveness"] >= 4.0:
                explanation = f"You've rated this {coping_data['avg_effectiveness']:.1f}/5 for {emotion}"
            elif coping_data["usage_count"] >= 5:
                explanation = f"Based on {coping_data['usage_count']} times you've used this"

        # Consider time of day patterns
        circadian = model.circadian_patterns or {}
        current_hour = context.get("hour", datetime.utcnow().hour)
        if "worst_hours" in circadian and current_hour in circadian["worst_hours"]:
            # During typically hard times, boost easy interventions
            if context.get("effort_level") in ["minimal", "low"]:
                sampled_score *= 1.1
                explanation += " | Good for this time of day"

        return min(sampled_score, 1.0), explanation
