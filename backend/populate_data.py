"""
Populate nikki@demo.com or nikkinach@gmail.com with test data
"""

from app.core.database import SessionLocal
from app.models.user import User
from app.models.checkin import MoodCheckin
from datetime import datetime, timedelta
import uuid
import random

def populate():
    db = SessionLocal()

    # Find user
    user = db.query(User).filter(
        User.email.in_(["nikki@demo.com", "nikkinach@gmail.com"])
    ).first()

    if not user:
        print("ERROR: User not found")
        return

    print(f"Populating data for: {user.email}")

    # Check existing
    existing = db.query(MoodCheckin).filter(MoodCheckin.user_id == user.id).count()
    print(f"Existing check-ins: {existing}")

    # Create 21 days of data for ML training
    base_date = datetime.now() - timedelta(days=21)

    patterns = [
        (5, 4, 6, "Monday blues. Work was overwhelming."),
        (5, 5, 5, "Tuesday. Felt okay, nothing special."),
        (6, 5, 5, "Had coffee with a friend. Felt better."),
        (6, 6, 4, "Productive day! Got a lot done."),
        (7, 7, 4, "Great Thursday. Feeling motivated."),
        (7, 6, 3, "Friday vibes! Weekend ahead."),
        (8, 7, 3, "Relaxing Saturday. Recharged."),
        (8, 8, 2, "Perfect Sunday. Quality time with family."),
        (7, 6, 4, "Back to work but feeling good."),
        (6, 5, 5, "Bit tired today."),
        (7, 6, 4, "Tried meditation. Really helpful!"),
        (7, 7, 3, "Feeling positive and hopeful."),
        (7, 6, 4, "Some anxiety but manageable."),
        (8, 7, 3, "Everything clicked today. Great day!"),
        (8, 8, 2, "Best day in weeks! Very grateful."),
        (7, 7, 3, "Still riding the high from yesterday."),
        (7, 6, 4, "Good solid day."),
        (6, 6, 5, "Bit stressed but okay."),
        (7, 7, 4, "Went for a walk. Felt energized."),
        (8, 7, 3, "Really proud of my progress this week."),
        (8, 8, 2, "Amazing day! Everything I hoped for."),
    ]

    emotions_list = [
        ["anxious", "worried"],
        ["neutral", "okay"],
        ["hopeful", "optimistic"],
        ["productive", "accomplished"],
        ["energized", "motivated"],
        ["calm", "peaceful"],
        ["grateful", "thankful"],
        ["tired", "low_energy"],
        ["happy", "content"],
        ["determined", "focused"],
    ]

    created = 0
    for i, (mood, energy, anxiety, journal) in enumerate(patterns):
        check_date = base_date + timedelta(days=i)

        checkin = MoodCheckin(
            id=uuid.uuid4(),
            user_id=user.id,
            mood_score=mood,
            energy_level=energy,
            anxiety_level=anxiety,
            stress_level=random.randint(2, 6),
            emotion_tags=random.choice(emotions_list),
            journal_text=journal,
            context_location="home" if i % 2 == 0 else "work",
            context_activity="working" if i < 15 else "relaxing",
            created_at=check_date
        )

        db.add(checkin)
        created += 1

    db.commit()

    total = existing + created
    print(f"\nSUCCESS!")
    print(f"Created: {created} new check-ins")
    print(f"Total now: {total} check-ins")
    print(f"Date range: {base_date.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}")
    print("\nYou can now:")
    print("  - View dashboard (mood chart will show)")
    print("  - See insights (patterns available)")
    print("  - Train ML model (21+ days of data!)")
    print("  - Get mood predictions")

    db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("POPULATE TEST DATA")
    print("=" * 60)
    populate()
    print("=" * 60)
