"""
Seed realistic demo data for user Nikki to showcase ML features
Creates 60 days of check-ins and intervention sessions with realistic patterns
DATA ENDS TODAY so all stats show current information
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta, timezone
import random
from uuid import uuid4
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.user import User, UserPreferences
from app.models.checkin import MoodCheckin
from app.models.intervention import Intervention, InterventionSession
from app.models.ml_model import UserMLModel
from app.services.auth import AuthService
from app.services.ml_training import MLTrainingService

# Ensure tables exist
Base.metadata.create_all(bind=engine)


def create_nikki_user(db: Session) -> User:
    """Create or get Nikki user"""
    user = db.query(User).filter(User.email == "nikki@demo.com").first()

    if not user:
        user = User(
            email="nikki@demo.com",
            password_hash=AuthService.get_password_hash("demo123"),
            display_name="Nikki",
            is_active=True,
            is_premium=True,
            subscription_tier="premium",
            has_adhd=True,
            has_autism_spectrum=False,
            has_anxiety=True,
            has_depression=False,
            other_conditions=["perfectionism"],
            data_sharing_consent=True,
            research_participation=True,
            age_range="25-34",
            timezone="America/New_York"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create preferences
        prefs = UserPreferences(
            user_id=user.id,
            theme="calm_light",
            font_size=16,
            morning_checkin_enabled=True,
            morning_checkin_time="08:00",
            evening_reflection_enabled=True,
            evening_reflection_time="20:00",
            time_blindness_support=True,
            task_breakdown_auto=True,
            sensory_load_tracking=False,
            emotion_scaffolding_level=2
        )
        db.add(prefs)
        db.commit()
        print(f"Created user Nikki with ID: {user.id}")
    else:
        print(f"Found existing user Nikki with ID: {user.id}")

    return user


def generate_realistic_checkins(db: Session, user: User):
    """Generate 60 days of realistic check-ins with patterns - DATA ENDS TODAY"""
    print("Generating 60 days of realistic check-ins (ending TODAY)...")

    # Clear existing check-ins for clean demo
    db.query(MoodCheckin).filter(MoodCheckin.user_id == user.id).delete()
    db.commit()

    checkins_created = 0

    # IMPORTANT: Data ends TODAY, starts 60 days ago
    # This ensures streak calculation and weekly stats work correctly
    end_date = datetime.now(timezone.utc)
    base_date = end_date - timedelta(days=60)

    for day_offset in range(60):
        current_date = base_date + timedelta(days=day_offset)
        day_name = current_date.strftime("%A")

        # Determine number of check-ins for this day (1-3)
        num_checkins = random.choice([1, 2, 2, 2, 3])  # Usually 2

        for checkin_num in range(num_checkins):
            # Determine time of day
            if checkin_num == 0:
                hour = random.randint(7, 10)  # Morning
                time_period = "morning"
            elif checkin_num == 1:
                hour = random.randint(13, 16)  # Afternoon
                time_period = "afternoon"
            else:
                hour = random.randint(19, 22)  # Evening
                time_period = "evening"

            checkin_time = current_date.replace(
                hour=hour,
                minute=random.randint(0, 59),
                second=0,
                microsecond=0
            )

            # Base mood with improvement trend
            improvement_factor = day_offset / 60 * 1.5  # Gradual improvement
            base_mood = 5.5 + improvement_factor

            # Day of week effects
            if day_name == "Monday":
                base_mood -= 1.2  # Mondays are hard
            elif day_name == "Friday":
                base_mood += 0.8
            elif day_name in ["Saturday", "Sunday"]:
                base_mood += 1.5  # Weekends are good

            # Time of day effects
            if time_period == "morning":
                base_mood -= 0.3  # Slow starts
            elif time_period == "afternoon" and hour >= 14 and hour <= 16:
                base_mood -= 0.8  # 3pm slump
            elif time_period == "evening":
                base_mood += 0.5  # Evenings are better

            # Add some randomness
            mood_score = int(max(1, min(10, base_mood + random.uniform(-1.5, 1.5))))

            # Energy correlates with mood but has its own pattern
            base_energy = mood_score - 0.5 + random.uniform(-1, 1)
            if hour >= 14 and hour <= 16:
                base_energy -= 1.5  # Afternoon energy dip
            energy_level = int(max(1, min(10, base_energy)))

            # Anxiety (inverse to mood, but higher in mornings)
            base_anxiety = 11 - mood_score + random.uniform(-2, 2)
            if time_period == "morning":
                base_anxiety += 1.5
            if day_name == "Monday":
                base_anxiety += 1.0
            anxiety_level = int(max(1, min(10, base_anxiety)))

            # Stress
            stress_level = int(max(1, min(10, anxiety_level + random.uniform(-1, 1))))

            # Executive function (ADHD pattern)
            exec_function = energy_level - random.randint(0, 2)
            if day_name == "Monday":
                exec_function -= 1
            exec_function = max(1, min(10, exec_function))

            # Emotions based on mood
            emotions = []
            if mood_score <= 3:
                emotions = random.sample(["sadness", "overwhelm", "exhaustion", "frustration"], 2)
            elif mood_score <= 5:
                emotions = random.sample(["anxiety", "stress", "neutral", "tired"], 2)
            elif mood_score <= 7:
                emotions = random.sample(["calm", "focused", "neutral", "content"], 2)
            else:
                emotions = random.sample(["joy", "calm", "energized", "grateful", "hopeful"], 2)

            # Context - create clear trigger patterns
            if mood_score <= 4:
                # Low mood - more likely in trigger contexts
                location = random.choice(["office", "commute", "office", "commute"])
                activity = random.choice(["working", "meeting", "commute", "working"])
                social = random.choice(["alone", "alone", "colleagues"])
            elif mood_score >= 7:
                # High mood - more likely in protective contexts
                location = random.choice(["home", "outdoors", "cafe", "friend_home", "outdoors"])
                activity = random.choice(["exercise", "relaxing", "hobby", "socializing"])
                social = random.choice(["with_friends", "with_family", "alone"])
            else:
                # Medium mood - mixed contexts
                if day_name in ["Saturday", "Sunday"]:
                    location = random.choice(["home", "outdoors", "cafe", "friend_home"])
                    activity = random.choice(["relaxing", "exercise", "socializing", "hobby"])
                    social = random.choice(["with_friends", "with_family", "alone"])
                else:
                    location = random.choice(["home", "office", "commute"])
                    activity = random.choice(["working", "meeting", "break", "commute"])
                    social = random.choice(["alone", "colleagues", "alone"])

            # Journal text (occasional)
            journal_text = None
            if random.random() < 0.3:  # 30% have journal entries
                if mood_score <= 4:
                    journal_text = random.choice([
                        "Feeling really overwhelmed today. Too many tasks and not enough focus.",
                        "Hard day. Anxiety is high and I can't seem to concentrate.",
                        "Struggling with time management again. ADHD brain is not cooperating.",
                        "Feeling stuck and unmotivated. Everything feels like too much.",
                    ])
                elif mood_score >= 7:
                    journal_text = random.choice([
                        "Good day! Managed to stay focused and got a lot done.",
                        "Feeling grateful for the progress I've made. The breathing exercises helped.",
                        "Had a productive morning. Energy levels are stable.",
                        "Great session with the grounding technique. Feeling much calmer.",
                    ])

            checkin = MoodCheckin(
                user_id=user.id,
                created_at=checkin_time,
                mood_score=mood_score,
                energy_level=energy_level,
                anxiety_level=anxiety_level,
                stress_level=stress_level,
                emotion_tags=emotions,
                context_location=location,
                context_activity=activity,
                context_social=social,
                journal_text=journal_text,
                executive_function_score=exec_function,
                sensory_load_score=None,
                masking_level=None,
                ai_emotion_primary=emotions[0] if emotions else None,
                ai_emotion_secondary=emotions[1] if len(emotions) > 1 else None,
                crisis_risk_score=0.0 if mood_score > 3 else random.uniform(0.1, 0.3),
                crisis_flagged=False
            )
            db.add(checkin)
            checkins_created += 1

    db.commit()
    print(f"Created {checkins_created} check-ins over 60 days (ending today)")
    return checkins_created


def generate_intervention_sessions(db: Session, user: User, ml_model: UserMLModel):
    """Generate intervention sessions with ratings and UPDATE ML MODEL properly"""
    print("Generating intervention sessions...")

    # Clear existing sessions
    db.query(InterventionSession).filter(InterventionSession.user_id == user.id).delete()
    db.commit()

    # Get some interventions
    interventions = db.query(Intervention).filter(
        Intervention.is_active == True,
        Intervention.adhd_friendly == True  # Nikki has ADHD
    ).limit(20).all()

    if not interventions:
        print("No interventions found. Run seed_interventions.py first!")
        return 0

    sessions_created = 0
    total_interactions = 0
    end_date = datetime.now(timezone.utc)
    base_date = end_date - timedelta(days=60)

    # Track intervention beliefs for Thompson Sampling
    beliefs = {}

    effective_interventions = interventions[:5]
    moderate_interventions = interventions[5:12]
    less_effective = interventions[12:]

    for day_offset in range(60):
        # Nikki tries 0-3 interventions per day
        num_sessions = random.choice([0, 0, 1, 1, 1, 2, 2, 3])

        for _ in range(num_sessions):
            # Weight towards effective ones over time (learning)
            if day_offset < 20:
                intervention = random.choice(interventions)
            elif day_offset < 40:
                pool = effective_interventions * 2 + moderate_interventions + less_effective
                intervention = random.choice(pool)
            else:
                pool = effective_interventions * 4 + moderate_interventions
                intervention = random.choice(pool)

            session_time = base_date + timedelta(
                days=day_offset,
                hours=random.randint(8, 21),
                minutes=random.randint(0, 59)
            )

            # Determine effectiveness rating based on intervention type
            if intervention in effective_interventions:
                rating = random.choice([4, 4, 4, 5, 5, 5])
            elif intervention in moderate_interventions:
                rating = random.choice([3, 3, 3, 4, 4])
            else:
                rating = random.choice([2, 2, 3, 3])

            # Context when intervention was used
            emotions = ["anxiety", "stress", "overwhelm", "sadness", "anger"]
            context_emotion = random.choice(emotions)
            context_energy = random.randint(3, 8)

            # Time of day
            hour = session_time.hour
            if hour < 12:
                tod = "morning"
            elif hour < 17:
                tod = "afternoon"
            else:
                tod = "evening"

            session = InterventionSession(
                user_id=user.id,
                intervention_id=intervention.id,
                checkin_id=None,
                created_at=session_time,
                started_at=session_time,
                completed_at=session_time + timedelta(seconds=intervention.duration_seconds),
                duration_actual_seconds=intervention.duration_seconds + random.randint(-30, 60),
                was_completed=True,
                was_skipped=False,
                effectiveness_rating=rating,
                feedback_tags=["helpful"] if rating >= 4 else ["okay"] if rating == 3 else ["not_helpful"],
                feedback_text=None,
                context_emotion=context_emotion,
                context_energy_level=context_energy,
                context_time_of_day=tod,
                predicted_effectiveness=0.5,
                actual_effectiveness=rating / 5.0,
                learning_signal=rating / 5.0 - 0.5
            )
            db.add(session)
            sessions_created += 1

            # UPDATE ML MODEL BELIEFS (what update_intervention_belief does)
            int_key = str(intervention.id)
            if int_key not in beliefs:
                beliefs[int_key] = {
                    "alpha": 1.0,
                    "beta": 1.0,
                    "count": 0,
                    "contexts": {}
                }

            # Convert rating to success
            if rating >= 4:
                success = 1.0
            elif rating <= 2:
                success = 0.0
            else:
                success = 0.5

            beliefs[int_key]["alpha"] += success
            beliefs[int_key]["beta"] += (1 - success)
            beliefs[int_key]["count"] += 1

            # Context-specific
            energy_bucket = "low" if context_energy <= 3 else "medium" if context_energy <= 7 else "high"
            ctx_key = f"{context_emotion}_{energy_bucket}_{tod}"
            if ctx_key not in beliefs[int_key]["contexts"]:
                beliefs[int_key]["contexts"][ctx_key] = {"alpha": 1.0, "beta": 1.0, "count": 0}
            beliefs[int_key]["contexts"][ctx_key]["alpha"] += success
            beliefs[int_key]["contexts"][ctx_key]["beta"] += (1 - success)
            beliefs[int_key]["contexts"][ctx_key]["count"] += 1

            total_interactions += 1

            # Update intervention global stats
            intervention.total_completions += 1
            if intervention.average_rating == 0:
                intervention.average_rating = rating
            else:
                total = intervention.average_rating * (intervention.total_completions - 1)
                intervention.average_rating = (total + rating) / intervention.total_completions

    # Save intervention beliefs to ML model
    ml_model.intervention_prior_beliefs = beliefs
    ml_model.total_interactions = total_interactions
    ml_model.last_model_update = datetime.now(timezone.utc)
    db.commit()

    print(f"Created {sessions_created} intervention sessions")
    print(f"Updated ML model with {total_interactions} total interactions")
    return sessions_created


def train_ml_model(db: Session, user: User):
    """Train the ML model with the generated data"""
    print("Training ML model with generated data...")

    result = MLTrainingService.train_user_model(db, user.id)

    print(f"Model trained successfully!")
    print(f"  Version: {result['model_version']}")
    print(f"  Patterns learned: {', '.join(result['patterns_learned'])}")
    if 'circadian_summary' in result:
        print(f"  Best hours: {result['circadian_summary'].get('best_hours', [])}")
        print(f"  Worst hours: {result['circadian_summary'].get('worst_hours', [])}")
        print(f"  Best days: {result['circadian_summary'].get('best_days', [])}")
    if 'triggers_found' in result:
        print(f"  Triggers found: {result['triggers_found']}")
    if 'emotions_mapped' in result:
        print(f"  Emotions mapped: {result['emotions_mapped']}")

    return result


def main():
    print("=" * 50)
    print("Seeding Demo Data for Nikki")
    print("=" * 50)

    db = SessionLocal()

    try:
        # Step 1: Create/get Nikki user
        nikki = create_nikki_user(db)

        # Step 2: Create/get ML model first
        ml_model = MLTrainingService.get_or_create_user_model(db, nikki.id)

        # Reset model for clean demo
        ml_model.intervention_prior_beliefs = {}
        ml_model.total_interactions = 0
        ml_model.model_version = 0  # Will become 1 after training
        db.commit()

        # Step 3: Generate realistic check-ins (ENDS TODAY)
        checkins = generate_realistic_checkins(db, nikki)

        # Step 4: Generate intervention sessions (updates ML model)
        sessions = generate_intervention_sessions(db, nikki, ml_model)

        # Step 5: Train ML model (learns patterns)
        ml_result = train_ml_model(db, nikki)

        print("\n" + "=" * 50)
        print("Demo Data Seeding Complete!")
        print("=" * 50)
        print(f"\nUser: Nikki (nikki@demo.com)")
        print(f"Password: demo123")
        print(f"\nData created:")
        print(f"  - {checkins} check-ins over 60 days (ending TODAY)")
        print(f"  - {sessions} intervention sessions")
        print(f"  - ML model trained with {len(ml_result['patterns_learned'])} patterns")
        print(f"  - Total interactions tracked: {ml_model.total_interactions}")
        print(f"\nPatterns to showcase:")
        print("  - Mondays are harder (lower mood)")
        print("  - Weekends are better")
        print("  - 3pm energy dip")
        print("  - Morning anxiety")
        print("  - Gradual improvement over 60 days")
        print("  - Some interventions work better than others")
        print(f"\nTriggers identified:")
        print("  - Location: office, commute (high negative correlation)")
        print("  - Protective: outdoors, home (high positive correlation)")
        print("\nLogin as nikki@demo.com / demo123 to explore!")

    finally:
        db.close()


if __name__ == "__main__":
    main()
