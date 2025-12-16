"""
Insights Generation Service - Generates personalized insights from ML patterns
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User
from app.models.checkin import MoodCheckin
from app.models.intervention import InterventionSession
from app.services.ml_training import MLTrainingService
from app.services.mood_prediction import MoodPredictionService


class InsightsService:
    """Generate personalized insights from user data"""

    @staticmethod
    def generate_weekly_insights(db: Session, user_id: UUID) -> Dict:
        """
        Generate comprehensive weekly insights for user.
        Combines mood trends, patterns, and intervention effectiveness.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}

        since = datetime.now(timezone.utc) - timedelta(days=7)
        checkins = db.query(MoodCheckin).filter(
            MoodCheckin.user_id == user_id,
            MoodCheckin.created_at >= since
        ).order_by(MoodCheckin.created_at.asc()).all()

        sessions = db.query(InterventionSession).filter(
            InterventionSession.user_id == user_id,
            InterventionSession.created_at >= since
        ).all()

        insights = {
            "period": "weekly",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "checkin_summary": {},
            "mood_insights": [],
            "intervention_insights": [],
            "personalized_tips": [],
            "achievements": [],
            "focus_areas": []
        }

        if len(checkins) == 0:
            insights["checkin_summary"] = {"total": 0, "message": "No check-ins this week"}
            insights["personalized_tips"].append("Try to check in at least once daily to build insights")
            return insights

        # Checkin summary
        avg_mood = sum(c.mood_score for c in checkins) / len(checkins)
        avg_energy = sum(c.energy_level for c in checkins) / len(checkins)

        insights["checkin_summary"] = {
            "total": len(checkins),
            "average_mood": round(avg_mood, 1),
            "average_energy": round(avg_energy, 1),
            "highest_mood": max(c.mood_score for c in checkins),
            "lowest_mood": min(c.mood_score for c in checkins),
            "consistency": InsightsService._calculate_consistency(checkins)
        }

        # Mood insights
        if avg_mood >= 7:
            insights["mood_insights"].append("Great week! Your average mood was quite positive.")
        elif avg_mood <= 4:
            insights["mood_insights"].append("This was a challenging week. Remember that difficult periods pass.")
        else:
            insights["mood_insights"].append("Your mood was moderate this week.")

        # Track mood volatility
        mood_changes = []
        for i in range(1, len(checkins)):
            mood_changes.append(abs(checkins[i].mood_score - checkins[i-1].mood_score))

        if mood_changes:
            avg_change = sum(mood_changes) / len(mood_changes)
            if avg_change > 2.5:
                insights["mood_insights"].append("Your mood showed significant variability this week.")
            elif avg_change < 1.0:
                insights["mood_insights"].append("Your mood was quite stable this week.")

        # Emotion frequency analysis
        emotion_counts = {}
        for checkin in checkins:
            for emotion in checkin.emotion_tags:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        if emotion_counts:
            top_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            insights["mood_insights"].append(
                f"Your most common emotions: {', '.join([e[0] for e in top_emotions])}"
            )

            # Check for concerning patterns
            negative_emotions = ["anxiety", "sadness", "overwhelm", "fear", "anger"]
            negative_count = sum(emotion_counts.get(e, 0) for e in negative_emotions)
            total_emotions = sum(emotion_counts.values())
            if total_emotions > 0 and negative_count / total_emotions > 0.6:
                insights["focus_areas"].append("Managing difficult emotions")

        # Intervention insights
        if sessions:
            completed = [s for s in sessions if s.was_completed]
            rated = [s for s in completed if s.effectiveness_rating]

            insights["intervention_insights"].append(
                f"You completed {len(completed)} interventions this week"
            )

            if rated:
                avg_effectiveness = sum(s.effectiveness_rating for s in rated) / len(rated)
                insights["intervention_insights"].append(
                    f"Average effectiveness rating: {avg_effectiveness:.1f}/5"
                )

                # Find best intervention
                best_session = max(rated, key=lambda s: s.effectiveness_rating)
                if best_session.effectiveness_rating >= 4:
                    insights["intervention_insights"].append(
                        f"Your most effective intervention this week worked really well"
                    )

        # Generate personalized tips based on user profile and patterns
        tips = InsightsService._generate_personalized_tips(user, checkins, sessions)
        insights["personalized_tips"] = tips

        # Achievements
        achievements = InsightsService._check_achievements(checkins, sessions)
        insights["achievements"] = achievements

        return insights

    @staticmethod
    def _calculate_consistency(checkins: List[MoodCheckin]) -> str:
        """Calculate check-in consistency over the week"""
        if len(checkins) >= 14:
            return "excellent"
        elif len(checkins) >= 7:
            return "good"
        elif len(checkins) >= 3:
            return "moderate"
        else:
            return "needs_improvement"

    @staticmethod
    def _generate_personalized_tips(
        user: User,
        checkins: List[MoodCheckin],
        sessions: List[InterventionSession]
    ) -> List[str]:
        """Generate personalized tips based on user profile and patterns"""
        tips = []

        # ADHD-specific tips
        if user.has_adhd:
            low_exec_function = [c for c in checkins if c.executive_function_score and c.executive_function_score <= 4]
            if len(low_exec_function) >= 2:
                tips.append("Consider breaking tasks into smaller chunks when executive function feels low")

            if len(checkins) < 7:
                tips.append("Try setting a daily reminder to help remember check-ins")

        # ASD-specific tips
        if user.has_autism_spectrum:
            high_sensory = [c for c in checkins if c.sensory_load_score and c.sensory_load_score >= 7]
            if len(high_sensory) >= 2:
                tips.append("You've had several high sensory load days - consider planning some low-stimulation time")

            high_masking = [c for c in checkins if c.masking_level and c.masking_level >= 7]
            if len(high_masking) >= 3:
                tips.append("High masking can be exhausting - remember to unmask in safe spaces")

        # Anxiety-specific tips
        if user.has_anxiety:
            high_anxiety = [c for c in checkins if c.anxiety_level and c.anxiety_level >= 7]
            if len(high_anxiety) >= 2:
                tips.append("Breathing exercises can help when anxiety is high")

        # Depression-specific tips
        if user.has_depression:
            low_energy = [c for c in checkins if c.energy_level <= 3]
            if len(low_energy) >= 3:
                tips.append("When energy is low, even small movements can help - try a 2-minute walk")

        # General tips based on patterns
        if len(checkins) >= 7:
            tips.append("Great consistency! Regular check-ins help build self-awareness")

        if sessions and len([s for s in sessions if s.was_completed]) > 5:
            tips.append("You're actively using interventions - this is excellent self-care")
        elif len(sessions) == 0:
            tips.append("Try exploring the intervention library when you need support")

        return tips[:5]  # Max 5 tips

    @staticmethod
    def _check_achievements(
        checkins: List[MoodCheckin],
        sessions: List[InterventionSession]
    ) -> List[Dict]:
        """Check for achievements earned this week"""
        achievements = []

        # Check-in streak
        if len(checkins) >= 7:
            achievements.append({
                "name": "Week Warrior",
                "description": "Checked in every day this week",
                "icon": "🏆"
            })

        # Intervention master
        completed = len([s for s in sessions if s.was_completed])
        if completed >= 10:
            achievements.append({
                "name": "Self-Care Champion",
                "description": f"Completed {completed} interventions this week",
                "icon": "⭐"
            })
        elif completed >= 5:
            achievements.append({
                "name": "Intervention Explorer",
                "description": f"Completed {completed} interventions this week",
                "icon": "🌟"
            })

        # Mood stability
        if len(checkins) >= 5:
            moods = [c.mood_score for c in checkins]
            variance = sum((m - sum(moods)/len(moods))**2 for m in moods) / len(moods)
            if variance < 1.5:
                achievements.append({
                    "name": "Steady Sailor",
                    "description": "Maintained stable mood throughout the week",
                    "icon": "⚓"
                })

        return achievements

    @staticmethod
    def get_daily_insight(db: Session, user_id: UUID) -> Dict:
        """
        Generate a single daily insight/tip for the user.
        Personalized based on their patterns and current state.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"insight": "Take care of yourself today", "type": "general"}

        # Get recent check-ins
        since = datetime.now(timezone.utc) - timedelta(days=3)
        recent_checkins = db.query(MoodCheckin).filter(
            MoodCheckin.user_id == user_id,
            MoodCheckin.created_at >= since
        ).order_by(MoodCheckin.created_at.desc()).all()

        # Get learned patterns
        model = MLTrainingService.get_or_create_user_model(db, user_id)
        circadian = model.circadian_patterns or {}
        triggers = model.trigger_patterns or {}

        current_hour = datetime.now(timezone.utc).hour
        current_day = datetime.now(timezone.utc).strftime("%A")

        insights = []

        # Time-based insight
        if "best_hours" in circadian and current_hour in circadian["best_hours"]:
            insights.append({
                "insight": f"This is typically your best time of day - great time for challenging tasks!",
                "type": "circadian",
                "priority": 1
            })
        elif "worst_hours" in circadian and current_hour in circadian["worst_hours"]:
            insights.append({
                "insight": "This is often a harder time for you - be extra gentle with yourself",
                "type": "circadian",
                "priority": 1
            })

        # Day-based insight
        if "best_days" in circadian and current_day in circadian["best_days"]:
            insights.append({
                "insight": f"{current_day}s tend to be good days for you - enjoy it!",
                "type": "weekly_pattern",
                "priority": 2
            })

        # Recent mood trend insight
        if len(recent_checkins) >= 2:
            mood_trend = recent_checkins[0].mood_score - recent_checkins[-1].mood_score
            if mood_trend > 2:
                insights.append({
                    "insight": "Your mood has been improving - keep up the good work!",
                    "type": "trend",
                    "priority": 2
                })
            elif mood_trend < -2:
                insights.append({
                    "insight": "Your mood has dipped recently - consider trying a gentle intervention",
                    "type": "trend",
                    "priority": 1
                })

        # Neurodiversity-specific insights
        if user.has_adhd and recent_checkins:
            latest = recent_checkins[0]
            if latest.executive_function_score and latest.executive_function_score <= 3:
                insights.append({
                    "insight": "Executive function seems low - try breaking tasks into tiny steps",
                    "type": "adhd_support",
                    "priority": 1
                })

        if user.has_autism_spectrum and recent_checkins:
            latest = recent_checkins[0]
            if latest.sensory_load_score and latest.sensory_load_score >= 8:
                insights.append({
                    "insight": "High sensory load detected - consider some quiet time or sensory breaks",
                    "type": "asd_support",
                    "priority": 1
                })

        # Pick the highest priority insight
        if insights:
            insights.sort(key=lambda x: x["priority"])
            return insights[0]

        # Default insight
        return {
            "insight": "Remember: every small step toward wellness counts",
            "type": "general",
            "priority": 3
        }

    @staticmethod
    def get_intervention_effectiveness_report(db: Session, user_id: UUID) -> Dict:
        """
        Generate report on which interventions work best for the user.
        """
        sessions = db.query(InterventionSession).filter(
            InterventionSession.user_id == user_id,
            InterventionSession.was_completed == True,
            InterventionSession.effectiveness_rating.isnot(None)
        ).all()

        if len(sessions) < 5:
            return {
                "report_available": False,
                "reason": "Need at least 5 rated interventions"
            }

        # Group by intervention
        intervention_stats = {}
        for session in sessions:
            int_id = str(session.intervention_id)
            if int_id not in intervention_stats:
                intervention_stats[int_id] = {
                    "ratings": [],
                    "emotions": [],
                    "times": []
                }
            intervention_stats[int_id]["ratings"].append(session.effectiveness_rating)
            if session.context_emotion:
                intervention_stats[int_id]["emotions"].append(session.context_emotion)
            if session.context_time_of_day:
                intervention_stats[int_id]["times"].append(session.context_time_of_day)

        # Calculate effectiveness
        effectiveness_report = []
        for int_id, stats in intervention_stats.items():
            avg_rating = sum(stats["ratings"]) / len(stats["ratings"])
            most_common_emotion = max(set(stats["emotions"]), key=stats["emotions"].count) if stats["emotions"] else "any"

            effectiveness_report.append({
                "intervention_id": int_id,
                "average_rating": round(avg_rating, 2),
                "total_uses": len(stats["ratings"]),
                "best_for_emotion": most_common_emotion,
                "consistency": round(
                    1 - (sum(abs(r - avg_rating) for r in stats["ratings"]) / len(stats["ratings"]) / 5), 2
                )
            })

        # Sort by effectiveness
        effectiveness_report.sort(key=lambda x: x["average_rating"], reverse=True)

        return {
            "report_available": True,
            "total_interventions_tried": len(effectiveness_report),
            "total_sessions": len(sessions),
            "top_interventions": effectiveness_report[:5],
            "least_effective": effectiveness_report[-3:] if len(effectiveness_report) > 3 else [],
            "recommendation": InsightsService._generate_effectiveness_recommendation(effectiveness_report)
        }

    @staticmethod
    def _generate_effectiveness_recommendation(report: List[Dict]) -> str:
        """Generate recommendation based on effectiveness report"""
        if not report:
            return "Try more interventions to discover what works for you"

        top = report[0]
        if top["average_rating"] >= 4.5:
            return f"Your top intervention is highly effective - consider using it more often"
        elif top["average_rating"] >= 3.5:
            return "You have some effective interventions - keep exploring to find more"
        else:
            return "Consider trying different interventions to find better fits"

    @staticmethod
    def generate_comprehensive_report(db: Session, user_id: UUID) -> Dict:
        """
        Generate a comprehensive ML insights report combining all analyses.
        """
        # Gather all insights
        mood_patterns = MoodPredictionService.detect_mood_patterns(db, user_id)
        crisis_risk = MoodPredictionService.predict_crisis_risk(db, user_id)
        optimal_times = MoodPredictionService.get_optimal_intervention_times(db, user_id)
        weekly = InsightsService.generate_weekly_insights(db, user_id)
        effectiveness = InsightsService.get_intervention_effectiveness_report(db, user_id)

        # Get model info
        model = MLTrainingService.get_or_create_user_model(db, user_id)

        return {
            "report_generated_at": datetime.now(timezone.utc).isoformat(),
            "model_version": model.model_version,
            "total_interactions_learned": model.total_interactions,
            "last_model_update": model.last_model_update.isoformat() if model.last_model_update else None,
            "sections": {
                "weekly_summary": weekly,
                "mood_patterns": mood_patterns,
                "crisis_risk_assessment": crisis_risk,
                "optimal_intervention_times": optimal_times,
                "intervention_effectiveness": effectiveness
            },
            "key_insights": InsightsService._extract_key_insights(
                mood_patterns, crisis_risk, weekly, effectiveness
            )
        }

    @staticmethod
    def _extract_key_insights(mood_patterns: Dict, crisis_risk: Dict, weekly: Dict, effectiveness: Dict) -> List[str]:
        """Extract the most important insights from all analyses"""
        key_insights = []

        # From mood patterns
        if mood_patterns.get("patterns_detected"):
            for pattern in mood_patterns.get("notable_patterns", [])[:2]:
                key_insights.append(pattern)

        # From crisis risk
        if crisis_risk.get("risk_level") == "moderate":
            key_insights.append("Consider prioritizing self-care - some risk factors detected")
        elif crisis_risk.get("risk_level") == "high":
            key_insights.append("IMPORTANT: Please consider reaching out for support")

        # From weekly insights
        for insight in weekly.get("mood_insights", [])[:1]:
            key_insights.append(insight)

        # From effectiveness
        if effectiveness.get("report_available"):
            key_insights.append(effectiveness.get("recommendation", ""))

        return key_insights[:5]
