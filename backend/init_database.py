"""
Initialize database with tables and demo user
Run this before starting the app for the first time
"""

import asyncio
from app.core.database import Base, engine
from app.models.user import User, UserPreferences
from app.models.checkin import MoodCheckin
from app.models.intervention import Intervention, InterventionSession
from app.models.ml_model import UserMLModel
from app.models.achievement import UserAchievement
from app.models.summary import WeeklySummary
from app.models.crisis import CrisisEvent
from app.ml.models import (
    JournalAnalysis,
    MoodPrediction,
    SeasonalPattern,
    CorrelationAnalysis,
    UserProfile,
    InterventionEffectiveness,
    ABTest,
    ABTestAssignment,
    ABTestResult,
    MLModelVersion
)
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")

def create_demo_user():
    """Create a demo user for testing"""
    print("\nCreating demo user...")

    try:
        db = Session(bind=engine)

        # Check if demo user already exists
        existing = db.query(User).filter(User.email == "demo@firefly.com").first()
        if existing:
            print("✓ Demo user already exists")
            print(f"  Email: demo@firefly.com")
            print(f"  Password: Demo123!")
            db.close()
            return

        # Create demo user
        demo_user = User(
            id=uuid.uuid4(),
            email="demo@firefly.com",
            password_hash=pwd_context.hash("Demo123!"),
            display_name="Demo User",
            is_active=True,
            has_anxiety=True,
            has_depression=False,
            has_adhd=False,
            has_autism_spectrum=False,
            data_sharing_consent=True
        )
        db.add(demo_user)
        db.flush()

        # Create user preferences
        preferences = UserPreferences(
            id=uuid.uuid4(),
            user_id=demo_user.id,
            theme="calm_light",
            communication_style="warm",
            morning_checkin_enabled=True,
            evening_reflection_enabled=True
        )
        db.add(preferences)

        db.commit()
        print("✓ Demo user created successfully")
        print(f"  Email: demo@firefly.com")
        print(f"  Password: Demo123!")
        db.close()

    except Exception as e:
        print(f"✗ Error creating demo user: {e}")
        import traceback
        traceback.print_exc()

def seed_interventions():
    """Add sample interventions"""
    print("\nSeeding interventions...")

    try:
        db = Session(bind=engine)

        # Check if interventions already exist
        count = db.query(Intervention).count()
        if count > 0:
            print(f"✓ {count} interventions already exist")
            db.close()
            return

        interventions = [
            {
                "name": "5-Minute Breathing Exercise",
                "description": "Simple breathing technique to reduce anxiety and promote calm",
                "therapeutic_approach": "mindfulness",
                "category": "breathing",
                "duration_seconds": 300,
                "difficulty_level": "beginner",
                "is_adhd_friendly": True,
                "is_asd_friendly": True,
                "target_emotions": ["anxious", "stressed", "overwhelmed"],
                "instructions": "Find a comfortable position. Breathe in for 4 counts, hold for 4, breathe out for 6. Repeat for 5 minutes."
            },
            {
                "name": "Gratitude Journaling",
                "description": "Write down three things you're grateful for today",
                "therapeutic_approach": "positive_psychology",
                "category": "journaling",
                "duration_seconds": 600,
                "difficulty_level": "beginner",
                "is_adhd_friendly": True,
                "is_asd_friendly": True,
                "target_emotions": ["sad", "hopeless", "disconnected"],
                "instructions": "List 3 things you're grateful for and why they matter to you."
            },
            {
                "name": "Progressive Muscle Relaxation",
                "description": "Systematically tense and relax muscle groups to release physical tension",
                "therapeutic_approach": "relaxation",
                "category": "body_scan",
                "duration_seconds": 900,
                "difficulty_level": "intermediate",
                "is_adhd_friendly": False,
                "is_asd_friendly": True,
                "target_emotions": ["tense", "anxious", "restless"],
                "instructions": "Starting with your toes, tense each muscle group for 5 seconds, then release."
            },
            {
                "name": "10-Minute Walk",
                "description": "Light physical activity to boost mood and energy",
                "therapeutic_approach": "behavioral_activation",
                "category": "movement",
                "duration_seconds": 600,
                "difficulty_level": "beginner",
                "is_adhd_friendly": True,
                "is_asd_friendly": True,
                "target_emotions": ["low_energy", "unmotivated", "stuck"],
                "instructions": "Take a 10-minute walk, ideally outdoors. Notice your surroundings."
            },
            {
                "name": "Guided Meditation",
                "description": "15-minute guided meditation for anxiety relief",
                "therapeutic_approach": "mindfulness",
                "category": "meditation",
                "duration_seconds": 900,
                "difficulty_level": "beginner",
                "is_adhd_friendly": False,
                "is_asd_friendly": False,
                "target_emotions": ["anxious", "overwhelmed", "racing_thoughts"],
                "instructions": "Follow along with a guided meditation app or video."
            }
        ]

        for i_data in interventions:
            intervention = Intervention(
                id=uuid.uuid4(),
                **i_data
            )
            db.add(intervention)

        db.commit()
        print(f"✓ Added {len(interventions)} interventions")
        db.close()

    except Exception as e:
        print(f"✗ Error seeding interventions: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("=" * 60)
    print("FIREFLY DATABASE INITIALIZATION")
    print("=" * 60)

    # Step 1: Create tables
    create_tables()

    # Step 2: Create demo user
    create_demo_user()

    # Step 3: Seed interventions
    seed_interventions()

    print("\n" + "=" * 60)
    print("✓ DATABASE INITIALIZATION COMPLETE")
    print("=" * 60)
    print("\nYou can now:")
    print("  1. Start the backend: python -m uvicorn app.main:app --reload")
    print("  2. Start the frontend: cd frontend && npm run dev")
    print("  3. Login with: demo@firefly.com / Demo123!")
    print()

if __name__ == "__main__":
    main()
