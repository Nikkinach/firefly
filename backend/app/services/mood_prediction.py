"""
Mood Prediction Service - Predicts future mood based on historical patterns
Uses exponential smoothing and pattern recognition
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from uuid import UUID
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.checkin import MoodCheckin
from app.models.ml_model import UserMLModel
from app.services.ml_training import MLTrainingService


class MoodPredictionService:
    """Predict mood and provide insights based on historical patterns"""

    @staticmethod
    def predict_next_mood(
        db: Session,
        user_id: UUID,
        prediction_hours: int = 24
    ) -> Dict:
        """
        Predict user's mood for the next N hours.
        Uses combination of:
        - Recent trend (exponential smoothing)
        - Circadian patterns
        - Day of week patterns
        """
        # Get recent check-ins
        since = datetime.now(timezone.utc) - timedelta(days=14)
        checkins = db.query(MoodCheckin).filter(
            MoodCheckin.user_id == user_id,
            MoodCheckin.created_at >= since
        ).order_by(MoodCheckin.created_at.desc()).all()

        if len(checkins) < 5:
            return {
                "prediction_available": False,
                "reason": "Need at least 5 check-ins in the past 2 weeks"
            }

        # Get user's learned patterns
        model = MLTrainingService.get_or_create_user_model(db, user_id)
        circadian = model.circadian_patterns or {}

        # Exponential smoothing for trend
        alpha = 0.3  # Smoothing factor
        smoothed_mood = checkins[-1].mood_score
        smoothed_energy = checkins[-1].energy_level

        for i in range(len(checkins) - 2, -1, -1):
            smoothed_mood = alpha * checkins[i].mood_score + (1 - alpha) * smoothed_mood
            smoothed_energy = alpha * checkins[i].energy_level + (1 - alpha) * smoothed_energy

        # Calculate trend direction
        recent_avg = sum(c.mood_score for c in checkins[:3]) / 3
        older_avg = sum(c.mood_score for c in checkins[3:min(7, len(checkins))]) / max(1, min(4, len(checkins) - 3))
        trend_direction = "stable"
        if recent_avg - older_avg > 0.5:
            trend_direction = "improving"
        elif recent_avg - older_avg < -0.5:
            trend_direction = "declining"

        # Predict for specific time
        target_time = datetime.now(timezone.utc) + timedelta(hours=prediction_hours)
        target_hour = target_time.hour
        target_day = target_time.strftime("%A")

        # Adjust prediction based on circadian patterns
        predicted_mood = smoothed_mood
        predicted_energy = smoothed_energy
        confidence = 0.5

        if "hourly" in circadian and str(target_hour) in circadian["hourly"]:
            hour_data = circadian["hourly"][str(target_hour)]
            # Blend smoothed value with historical pattern
            weight = min(hour_data["sample_count"] / 20, 0.7)  # Max 70% weight to historical
            predicted_mood = (1 - weight) * smoothed_mood + weight * hour_data["avg_mood"]
            predicted_energy = (1 - weight) * smoothed_energy + weight * hour_data["avg_energy"]
            confidence += 0.2

        if "daily" in circadian and target_day in circadian["daily"]:
            day_data = circadian["daily"][target_day]
            weight = min(day_data["sample_count"] / 15, 0.3)
            predicted_mood = predicted_mood * (1 - weight) + day_data["avg_mood"] * weight
            confidence += 0.1

        # Bound predictions
        predicted_mood = max(1, min(10, round(predicted_mood, 1)))
        predicted_energy = max(1, min(10, round(predicted_energy, 1)))
        confidence = min(confidence, 0.95)

        # Generate insights
        insights = []
        if "worst_hours" in circadian and target_hour in circadian["worst_hours"]:
            insights.append(f"This is typically a challenging time for you (around {target_hour}:00)")
        if "best_hours" in circadian and target_hour in circadian["best_hours"]:
            insights.append(f"This is typically your best time (around {target_hour}:00)")
        if trend_direction == "improving":
            insights.append("Your mood has been trending upward recently")
        elif trend_direction == "declining":
            insights.append("Your mood has been trending downward - consider proactive self-care")

        return {
            "prediction_available": True,
            "predicted_mood": predicted_mood,
            "predicted_energy": predicted_energy,
            "prediction_time": target_time.isoformat(),
            "confidence": round(confidence, 2),
            "trend_direction": trend_direction,
            "insights": insights,
            "based_on_checkins": len(checkins)
        }

    @staticmethod
    def get_mood_forecast(db: Session, user_id: UUID, days: int = 7) -> List[Dict]:
        """
        Generate mood forecast for the next N days.
        Predicts morning, afternoon, and evening mood for each day.
        """
        forecasts = []
        model = MLTrainingService.get_or_create_user_model(db, user_id)
        circadian = model.circadian_patterns or {}

        # Get baseline from recent check-ins
        since = datetime.now(timezone.utc) - timedelta(days=14)
        checkins = db.query(MoodCheckin).filter(
            MoodCheckin.user_id == user_id,
            MoodCheckin.created_at >= since
        ).all()

        if len(checkins) < 10:
            return []

        # Calculate baseline
        baseline_mood = sum(c.mood_score for c in checkins) / len(checkins)

        for day_offset in range(days):
            target_date = datetime.now(timezone.utc) + timedelta(days=day_offset)
            day_name = target_date.strftime("%A")

            # Get day-specific adjustment
            day_adjustment = 0
            if "daily" in circadian and day_name in circadian["daily"]:
                day_avg = circadian["daily"][day_name]["avg_mood"]
                day_adjustment = day_avg - baseline_mood

            # Morning (8am), Afternoon (2pm), Evening (8pm)
            times = [("morning", 8), ("afternoon", 14), ("evening", 20)]
            day_forecast = {
                "date": target_date.strftime("%Y-%m-%d"),
                "day": day_name,
                "periods": {}
            }

            for period_name, hour in times:
                hour_mood = baseline_mood + day_adjustment

                # Apply hourly pattern
                if "hourly" in circadian and str(hour) in circadian["hourly"]:
                    hour_avg = circadian["hourly"][str(hour)]["avg_mood"]
                    hour_mood = (hour_mood + hour_avg) / 2

                day_forecast["periods"][period_name] = {
                    "time": f"{hour:02d}:00",
                    "predicted_mood": round(max(1, min(10, hour_mood)), 1)
                }

            forecasts.append(day_forecast)

        return forecasts

    @staticmethod
    def detect_mood_patterns(db: Session, user_id: UUID) -> Dict:
        """
        Detect significant patterns in user's mood data.
        Identifies:
        - Weekly patterns
        - Monthly patterns (if enough data)
        - Seasonal patterns
        - Sudden changes
        """
        since = datetime.now(timezone.utc) - timedelta(days=90)
        checkins = db.query(MoodCheckin).filter(
            MoodCheckin.user_id == user_id,
            MoodCheckin.created_at >= since
        ).order_by(MoodCheckin.created_at.asc()).all()

        if len(checkins) < 20:
            return {"patterns_detected": False, "reason": "Need more data"}

        patterns = {
            "patterns_detected": True,
            "weekly_cycle": None,
            "time_of_day_effect": None,
            "volatility": None,
            "recent_stability": None,
            "notable_patterns": []
        }

        # Analyze weekly cycle
        day_moods = defaultdict(list)
        for checkin in checkins:
            day = checkin.created_at.strftime("%A")
            day_moods[day].append(checkin.mood_score)

        day_averages = {}
        for day, moods in day_moods.items():
            if len(moods) >= 3:
                day_averages[day] = sum(moods) / len(moods)

        if day_averages:
            best_day = max(day_averages, key=day_averages.get)
            worst_day = min(day_averages, key=day_averages.get)
            spread = day_averages[best_day] - day_averages[worst_day]

            if spread >= 1.5:
                patterns["weekly_cycle"] = {
                    "best_day": best_day,
                    "worst_day": worst_day,
                    "spread": round(spread, 2),
                    "strength": "strong" if spread >= 2.5 else "moderate"
                }
                patterns["notable_patterns"].append(
                    f"Your mood tends to be higher on {best_day}s (avg {day_averages[best_day]:.1f}) "
                    f"and lower on {worst_day}s (avg {day_averages[worst_day]:.1f})"
                )

        # Analyze time of day effect
        time_buckets = {"morning": [], "afternoon": [], "evening": [], "night": []}
        for checkin in checkins:
            hour = checkin.created_at.hour
            if 5 <= hour < 12:
                time_buckets["morning"].append(checkin.mood_score)
            elif 12 <= hour < 17:
                time_buckets["afternoon"].append(checkin.mood_score)
            elif 17 <= hour < 21:
                time_buckets["evening"].append(checkin.mood_score)
            else:
                time_buckets["night"].append(checkin.mood_score)

        time_averages = {}
        for time_period, moods in time_buckets.items():
            if len(moods) >= 5:
                time_averages[time_period] = sum(moods) / len(moods)

        if time_averages:
            best_time = max(time_averages, key=time_averages.get)
            worst_time = min(time_averages, key=time_averages.get)
            spread = time_averages[best_time] - time_averages[worst_time]

            if spread >= 1.0:
                patterns["time_of_day_effect"] = {
                    "best_time": best_time,
                    "worst_time": worst_time,
                    "spread": round(spread, 2)
                }
                patterns["notable_patterns"].append(
                    f"You typically feel better in the {best_time} and lower in the {worst_time}"
                )

        # Calculate mood volatility
        mood_diffs = []
        for i in range(1, len(checkins)):
            diff = abs(checkins[i].mood_score - checkins[i-1].mood_score)
            mood_diffs.append(diff)

        avg_volatility = sum(mood_diffs) / len(mood_diffs) if mood_diffs else 0
        patterns["volatility"] = {
            "average_change": round(avg_volatility, 2),
            "level": "high" if avg_volatility > 2.5 else "moderate" if avg_volatility > 1.5 else "stable"
        }

        if avg_volatility > 2.5:
            patterns["notable_patterns"].append(
                "Your mood shows high variability - consider tracking triggers"
            )

        # Recent stability (last 7 days vs previous)
        recent = [c for c in checkins if c.created_at >= datetime.now(timezone.utc) - timedelta(days=7)]
        older = [c for c in checkins if c.created_at < datetime.now(timezone.utc) - timedelta(days=7)]

        if len(recent) >= 3 and len(older) >= 5:
            recent_avg = sum(c.mood_score for c in recent) / len(recent)
            older_avg = sum(c.mood_score for c in older) / len(older)
            change = recent_avg - older_avg

            patterns["recent_stability"] = {
                "recent_average": round(recent_avg, 2),
                "historical_average": round(older_avg, 2),
                "change": round(change, 2),
                "direction": "improving" if change > 0.5 else "declining" if change < -0.5 else "stable"
            }

            if abs(change) >= 1.0:
                direction = "improved" if change > 0 else "declined"
                patterns["notable_patterns"].append(
                    f"Your mood has {direction} significantly in the past week"
                )

        return patterns

    @staticmethod
    def predict_crisis_risk(db: Session, user_id: UUID) -> Dict:
        """
        Predict likelihood of crisis based on patterns.
        Looks at declining mood trends, high anxiety patterns, and historical crisis events.
        """
        # Get recent check-ins
        since = datetime.now(timezone.utc) - timedelta(days=14)
        checkins = db.query(MoodCheckin).filter(
            MoodCheckin.user_id == user_id,
            MoodCheckin.created_at >= since
        ).order_by(MoodCheckin.created_at.desc()).all()

        if len(checkins) < 3:
            return {
                "risk_assessment_available": False,
                "reason": "Insufficient data"
            }

        risk_factors = []
        risk_score = 0.0

        # Check for declining mood trend
        if len(checkins) >= 5:
            recent_avg = sum(c.mood_score for c in checkins[:3]) / 3
            older_avg = sum(c.mood_score for c in checkins[3:min(7, len(checkins))]) / max(1, min(4, len(checkins) - 3))

            if recent_avg - older_avg < -2.0:
                risk_factors.append("Significant mood decline detected")
                risk_score += 0.3

        # Check for persistent low mood
        low_mood_count = sum(1 for c in checkins[:7] if c.mood_score <= 3)
        if low_mood_count >= 3:
            risk_factors.append(f"Persistent low mood ({low_mood_count} of last 7 check-ins)")
            risk_score += 0.25

        # Check for high anxiety
        high_anxiety_count = sum(1 for c in checkins[:7] if c.anxiety_level and c.anxiety_level >= 8)
        if high_anxiety_count >= 2:
            risk_factors.append(f"Elevated anxiety levels")
            risk_score += 0.2

        # Check for crisis flags in history
        crisis_flagged = sum(1 for c in checkins if c.crisis_flagged)
        if crisis_flagged >= 1:
            risk_factors.append("Recent crisis-level check-in detected")
            risk_score += 0.35

        # Check for isolation patterns
        isolation_count = sum(1 for c in checkins[:7] if c.context_social == "alone")
        if isolation_count >= 5:
            risk_factors.append("Social isolation pattern")
            risk_score += 0.15

        risk_level = "low"
        if risk_score >= 0.6:
            risk_level = "high"
        elif risk_score >= 0.3:
            risk_level = "moderate"

        recommendations = []
        if risk_level == "high":
            recommendations = [
                "Consider reaching out to a mental health professional",
                "Use crisis resources if needed",
                "Reach out to a trusted friend or family member",
                "Practice grounding techniques"
            ]
        elif risk_level == "moderate":
            recommendations = [
                "Prioritize self-care activities",
                "Consider talking to someone you trust",
                "Try gentle interventions from your toolkit"
            ]

        return {
            "risk_assessment_available": True,
            "risk_level": risk_level,
            "risk_score": round(min(risk_score, 1.0), 2),
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "assessed_at": datetime.now(timezone.utc).isoformat()
        }

    @staticmethod
    def get_optimal_intervention_times(db: Session, user_id: UUID) -> Dict:
        """
        Identify optimal times for interventions based on patterns.
        """
        model = MLTrainingService.get_or_create_user_model(db, user_id)
        circadian = model.circadian_patterns or {}

        if not circadian or "hourly" not in circadian:
            return {"optimal_times_available": False}

        # Find times when mood is low but energy is okay
        optimal_times = []
        for hour_str, data in circadian.get("hourly", {}).items():
            hour = int(hour_str)
            mood = data["avg_mood"]
            energy = data["avg_energy"]

            # Good time for intervention: lower mood but decent energy
            if mood <= 6 and energy >= 4:
                optimal_times.append({
                    "hour": hour,
                    "mood": mood,
                    "energy": energy,
                    "reason": "Lower mood with available energy"
                })

        # Sort by mood (lower first)
        optimal_times.sort(key=lambda x: x["mood"])

        return {
            "optimal_times_available": True,
            "recommended_times": optimal_times[:3],
            "insight": "These are times when interventions may be most beneficial"
        }
