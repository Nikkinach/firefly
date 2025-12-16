"""
Populate comprehensive test data for insights, streaks, and analytics
Creates 60 days of varied data showing patterns, streaks, and trends
"""

from app.core.database import SessionLocal
from app.models.user import User
from app.models.checkin import MoodCheckin
from datetime import datetime, timedelta
import uuid
import random
import numpy as np

def populate_comprehensive_data():
    db = SessionLocal()

    # Find user
    user = db.query(User).filter(
        User.email.in_(["nikki@demo.com", "nikkinach@gmail.com"])
    ).first()

    if not user:
        print("ERROR: User not found")
        return

    print(f"Populating comprehensive data for: {user.email}")

    # Delete existing check-ins to start fresh
    existing = db.query(MoodCheckin).filter(MoodCheckin.user_id == user.id).count()
    print(f"Deleting {existing} existing check-ins...")
    db.query(MoodCheckin).filter(MoodCheckin.user_id == user.id).delete()
    db.commit()

    # Generate 60 days of data with patterns
    base_date = datetime.now() - timedelta(days=60)

    # Create realistic patterns
    journal_templates = {
        'low': [
            "Feeling down today. Everything seems difficult.",
            "Had trouble getting out of bed. Low motivation.",
            "Overwhelmed with tasks. Feeling stressed.",
            "Not my best day. Struggling a bit.",
            "Feeling anxious about everything."
        ],
        'medium': [
            "Okay day. Some ups and downs.",
            "Normal day. Nothing special.",
            "Manageable stress levels today.",
            "Had some good moments and some challenges.",
            "Average day overall."
        ],
        'high': [
            "Great day! Feeling productive and happy.",
            "Really good mood today. Things are going well.",
            "Accomplished a lot and feeling proud.",
            "Wonderful day with friends. Feeling grateful.",
            "Energized and motivated. Best day this week!",
            "Had an amazing breakthrough today!",
            "Everything clicked. Perfect balance.",
            "Feeling so positive and hopeful about the future."
        ]
    }

    emotion_sets = {
        'low': [["sad", "tired"], ["anxious", "overwhelmed"], ["stressed", "worried"], ["down", "unmotivated"]],
        'medium': [["neutral", "okay"], ["calm", "content"], ["focused", "steady"]],
        'high': [["happy", "energized"], ["grateful", "joyful"], ["motivated", "productive"], ["peaceful", "content"]]
    }

    contexts = {
        'location': ['home', 'work', 'outdoors', 'gym', 'cafe'],
        'activity': ['working', 'relaxing', 'exercising', 'socializing', 'creative_work', 'resting']
    }

    created = 0

    for day in range(60):
        check_date = base_date + timedelta(days=day)

        # Create weekly pattern (better on weekends)
        day_of_week = check_date.weekday()
        is_weekend = day_of_week >= 5

        # Create overall upward trend
        trend_factor = day / 60  # 0 to 1 over 60 days

        # Weekly variation
        weekly_factor = 2 * np.sin(2 * np.pi * day / 7)

        # Calculate base mood (1-10 scale)
        base_mood = 4 + (trend_factor * 3) + weekly_factor + (1.5 if is_weekend else 0)

        # Add some randomness
        mood = base_mood + random.uniform(-1, 1)
        mood = max(1, min(10, int(round(mood))))

        # Energy correlates with mood but with some variation
        energy = mood + random.randint(-1, 1)
        energy = max(1, min(10, energy))

        # Anxiety inversely correlates with mood
        anxiety = 11 - mood + random.randint(-2, 2)
        anxiety = max(1, min(10, anxiety))

        # Stress
        stress = random.randint(max(1, mood - 3), min(10, mood + 2))

        # Choose journal and emotions based on mood
        if mood <= 4:
            journal = random.choice(journal_templates['low'])
            emotions = random.choice(emotion_sets['low'])
        elif mood <= 7:
            journal = random.choice(journal_templates['medium'])
            emotions = random.choice(emotion_sets['medium'])
        else:
            journal = random.choice(journal_templates['high'])
            emotions = random.choice(emotion_sets['high'])

        # Create check-in
        checkin = MoodCheckin(
            id=uuid.uuid4(),
            user_id=user.id,
            mood_score=mood,
            energy_level=energy,
            anxiety_level=anxiety,
            stress_level=stress,
            emotion_tags=emotions,
            journal_text=journal,
            context_location=random.choice(contexts['location']),
            context_activity=random.choice(contexts['activity']),
            context_social='alone' if random.random() > 0.3 else 'with_others',
            created_at=check_date
        )

        db.add(checkin)
        created += 1

        # Commit every 10 to avoid huge transactions
        if created % 10 == 0:
            db.commit()

    # Final commit
    db.commit()

    print(f"\nSUCCESS!")
    print(f"Created: {created} check-ins")
    print(f"Date range: {base_date.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}")
    print(f"\nData characteristics:")
    print(f"  - Overall trend: IMPROVING (mood 4 -> 7)")
    print(f"  - Weekly pattern: Better on weekends")
    print(f"  - Mood range: 1-10 (full spectrum)")
    print(f"  - 60 days of data (enough for seasonal patterns!)")
    print(f"\nNow you can:")
    print(f"  1. View dashboard - see 60-day mood chart")
    print(f"  2. Check insights - weekly patterns, streaks")
    print(f"  3. Train ML model - predict next 7 days")
    print(f"  4. View analytics - seasonal patterns detected")
    print(f"  5. Get recommendations - personalized based on your data")

    # Calculate and display some stats
    all_checkins = db.query(MoodCheckin).filter(MoodCheckin.user_id == user.id).all()
    moods = [c.mood_score for c in all_checkins]

    print(f"\nStats:")
    print(f"  Average mood: {np.mean(moods):.1f}")
    print(f"  Mood range: {min(moods)} - {max(moods)}")
    print(f"  Std deviation: {np.std(moods):.2f}")
    print(f"  Days above 7: {sum(1 for m in moods if m >= 7)}")
    print(f"  Days below 4: {sum(1 for m in moods if m <= 4)}")

    db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("POPULATE COMPREHENSIVE TEST DATA")
    print("=" * 60)
    populate_comprehensive_data()
    print("=" * 60)
