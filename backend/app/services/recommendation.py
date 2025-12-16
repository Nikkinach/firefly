"""
Recommendation Engine - ML-powered personalized recommendations
Uses Thompson Sampling and learned patterns for optimization
"""
from typing import List, Dict
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.intervention import Intervention
from app.models.user import User
from app.services.intervention import InterventionService
from app.services.ml_training import MLTrainingService


class RecommendationService:
    """Generate personalized intervention recommendations using ML"""

    # Emotion to intervention mapping (base knowledge)
    EMOTION_INTERVENTION_MAP = {
        "anxiety": ["DBT", "Mindfulness", "Physical"],
        "stress": ["Mindfulness", "Physical", "DBT"],
        "sadness": ["ACT", "CBT", "Physical"],
        "anger": ["DBT", "Physical", "Mindfulness"],
        "overwhelm": ["DBT", "Sensory", "Mindfulness"],
        "fear": ["CBT", "DBT", "Mindfulness"],
        "neutral": ["Mindfulness", "ACT", "Physical"],
        "calm": ["ACT", "Mindfulness", "CBT"],
        "joy": ["Mindfulness", "ACT", "Physical"],
    }

    @staticmethod
    def get_recommendations(
        db: Session,
        user_id: UUID,
        current_emotion: str,
        energy_level: int,
        time_available_minutes: int,
        context: str = None
    ) -> List[Dict]:
        """
        Get top 3 personalized intervention recommendations.
        Uses Thompson Sampling for exploration/exploitation balance.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []

        # Get user's ML model for personalized scoring
        ml_model = MLTrainingService.get_or_create_user_model(db, user_id)

        # Get user's effective interventions from history
        effective_interventions = InterventionService.get_user_effective_interventions(db, user_id)
        effective_ids = {item["intervention_id"] for item in effective_interventions}

        # Determine preferred therapeutic approaches based on emotion
        preferred_approaches = RecommendationService.EMOTION_INTERVENTION_MAP.get(
            current_emotion.lower(), ["Mindfulness", "DBT", "ACT"]
        )

        # Filter interventions based on constraints
        max_duration_seconds = time_available_minutes * 60

        # Determine energy requirement based on energy level
        if energy_level <= 3:
            allowed_effort = ["minimal", "low"]
        elif energy_level <= 6:
            allowed_effort = ["minimal", "low", "medium"]
        else:
            allowed_effort = ["minimal", "low", "medium", "high"]

        # Query interventions
        base_query = db.query(Intervention).filter(
            Intervention.is_active == True,
            Intervention.duration_seconds <= max_duration_seconds,
            Intervention.effort_level.in_(allowed_effort)
        )

        # Apply neurodiversity filters
        if user.has_adhd:
            base_query = base_query.filter(Intervention.adhd_friendly == True)
        if user.has_autism_spectrum:
            base_query = base_query.filter(Intervention.asd_friendly == True)

        # Filter by premium status
        if not user.is_premium:
            base_query = base_query.filter(Intervention.is_premium == False)

        all_interventions = base_query.all()

        # Build context for ML scoring
        ml_context = {
            "emotion": current_emotion,
            "energy_level": energy_level,
            "time_of_day": datetime.utcnow().strftime("%p").lower(),
            "hour": datetime.utcnow().hour
        }

        # Score and rank interventions using ML
        scored_interventions = []
        for intervention in all_interventions:
            # Get ML-based personalized score
            ml_score, ml_explanation = MLTrainingService.get_personalized_score(
                db, user_id, intervention.id, current_emotion, ml_context
            )

            # Combine ML score with rule-based score
            rule_score = RecommendationService._calculate_base_score(
                intervention,
                current_emotion,
                preferred_approaches,
                effective_ids,
                energy_level
            )

            # Weight: 60% ML, 40% rules (ML gets more weight as data accumulates)
            ml_weight = min(0.6, 0.3 + (ml_model.total_interactions / 100) * 0.3)
            rule_weight = 1 - ml_weight
            final_score = (ml_score * ml_weight) + (rule_score * rule_weight)

            # Generate explanation
            why_recommended = RecommendationService._generate_ml_explanation(
                intervention,
                current_emotion,
                effective_ids,
                ml_explanation,
                ml_model.total_interactions
            )

            scored_interventions.append({
                "intervention": intervention,
                "score": final_score,
                "ml_score": ml_score,
                "rule_score": rule_score,
                "why_recommended": why_recommended
            })

        # Sort by score (descending)
        scored_interventions.sort(key=lambda x: x["score"], reverse=True)

        # Return top 3 with diversity (exploration)
        top_recommendations = RecommendationService._ensure_diversity_with_exploration(
            scored_interventions[:15],
            ml_model.total_interactions
        )[:3]

        # Format response
        results = []
        for item in top_recommendations:
            intervention = item["intervention"]
            results.append({
                "intervention_id": intervention.id,
                "name": intervention.name,
                "short_description": intervention.short_description,
                "duration_seconds": intervention.duration_seconds,
                "effort_level": intervention.effort_level,
                "why_recommended": item["why_recommended"],
                "predicted_effectiveness": round(item["score"], 2),
                "personalization_score": round(item["ml_score"], 2)
            })

        return results

    @staticmethod
    def _calculate_base_score(
        intervention: Intervention,
        current_emotion: str,
        preferred_approaches: List[str],
        effective_ids: set,
        energy_level: int
    ) -> float:
        """Calculate base recommendation score (rule-based)"""
        score = 0.5  # Base score

        # Boost if therapeutic approach matches emotion needs
        if intervention.therapeutic_approach in preferred_approaches:
            position = preferred_approaches.index(intervention.therapeutic_approach)
            score += 0.3 - (position * 0.1)  # Higher boost for first preferred

        # Boost if emotion is in target emotions
        if current_emotion.lower() in [e.lower() for e in intervention.target_emotions]:
            score += 0.2

        # Boost if proven effective for user
        if intervention.id in effective_ids:
            score += 0.25

        # Consider global effectiveness
        score += intervention.global_effectiveness_score * 0.15

        # Energy match bonus
        effort_map = {"minimal": 1, "low": 3, "medium": 6, "high": 9}
        effort_score = effort_map.get(intervention.effort_level, 5)
        energy_match = 1 - abs(energy_level - effort_score) / 10
        score += energy_match * 0.1

        return min(score, 1.0)

    @staticmethod
    def _generate_ml_explanation(
        intervention: Intervention,
        current_emotion: str,
        effective_ids: set,
        ml_explanation: str,
        total_interactions: int
    ) -> str:
        """Generate human-readable explanation with ML insights"""
        # If we have enough ML data, use ML explanation
        if total_interactions >= 10 and ml_explanation != "Based on your personal usage patterns":
            return ml_explanation

        # Fall back to rule-based explanation
        reasons = []

        if intervention.id in effective_ids:
            reasons.append("This has worked well for you before")

        if current_emotion.lower() in [e.lower() for e in intervention.target_emotions]:
            reasons.append(f"Specifically designed for {current_emotion}")

        if not reasons:
            approach_reasons = {
                "DBT": "DBT skills help with emotional regulation",
                "ACT": "ACT promotes psychological flexibility",
                "CBT": "CBT helps restructure thought patterns",
                "Mindfulness": "Mindfulness brings present-moment awareness",
                "Physical": "Physical interventions release tension",
                "Sensory": "Sensory techniques help with regulation"
            }
            reasons.append(approach_reasons.get(
                intervention.therapeutic_approach,
                f"Based on {intervention.therapeutic_approach} principles"
            ))

        return reasons[0] if reasons else "Recommended based on your profile"

    @staticmethod
    def _ensure_diversity_with_exploration(
        scored_interventions: List[Dict],
        total_interactions: int
    ) -> List[Dict]:
        """
        Ensure variety in recommendations with exploration bonus.
        Less explored interventions get a small boost to encourage trying new things.
        """
        if len(scored_interventions) <= 3:
            return scored_interventions

        selected = []
        approaches_used = set()

        # Exploration rate decreases as we learn more
        exploration_rate = max(0.1, 0.3 - (total_interactions / 200))

        for item in scored_interventions:
            approach = item["intervention"].therapeutic_approach

            # Add small exploration bonus for diversity
            if approach not in approaches_used:
                item["score"] *= (1 + exploration_rate)

            if approach not in approaches_used or len(selected) < 3:
                selected.append(item)
                approaches_used.add(approach)

            if len(selected) >= 3:
                break

        # Re-sort after exploration bonus
        selected.sort(key=lambda x: x["score"], reverse=True)

        return selected

    @staticmethod
    def _generate_explanation(
        intervention: Intervention,
        current_emotion: str,
        effective_ids: set
    ) -> str:
        """Generate human-readable explanation for recommendation"""
        reasons = []

        if intervention.id in effective_ids:
            reasons.append("This has worked well for you before")

        if current_emotion.lower() in [e.lower() for e in intervention.target_emotions]:
            reasons.append(f"Specifically designed for {current_emotion}")

        if not reasons:
            approach_reasons = {
                "DBT": "DBT skills help with emotional regulation",
                "ACT": "ACT promotes psychological flexibility",
                "CBT": "CBT helps restructure thought patterns",
                "Mindfulness": "Mindfulness brings present-moment awareness",
                "Physical": "Physical interventions release tension",
                "Sensory": "Sensory techniques help with regulation"
            }
            reasons.append(approach_reasons.get(
                intervention.therapeutic_approach,
                f"Based on {intervention.therapeutic_approach} principles"
            ))

        return reasons[0] if reasons else "Recommended based on your profile"

    @staticmethod
    def _ensure_diversity(scored_interventions: List[Dict]) -> List[Dict]:
        """Ensure variety in recommendations (different approaches)"""
        if len(scored_interventions) <= 3:
            return scored_interventions

        selected = []
        approaches_used = set()

        for item in scored_interventions:
            approach = item["intervention"].therapeutic_approach
            if approach not in approaches_used or len(selected) < 3:
                selected.append(item)
                approaches_used.add(approach)
            if len(selected) >= 3:
                break

        return selected
