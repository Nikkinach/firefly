"""
Create test mood check-in data for the demo user
This populates the dashboard with sample data
"""

from app.core.database import SessionLocal
from app.models.user import User
from app.models.checkin import MoodCheckin
from datetime import datetime, timedelta
import uuid
import random

def create_test_checkins():
    """Create 14 days of test check-in data"""
    db = SessionLocal()

    try:
        # Find demo user - try multiple possible emails
        user = db.query(User).filter(
            User.email.in_(["nikki@demo.com", "demo@firefly.com", "nikkinach@gmail.com"])
        ).first()

        if not user:
            print("✗ No user found. Available emails in database:")
            all_users = db.query(User).all()
            for u in all_users:
                print(f"  - {u.email}")
            return

        print(f"Creating test data for user: {user.email}")

        # Check if data already exists
        existing_count = db.query(MoodCheckin).filter(MoodCheckin.user_id == user.id).count()
        if existing_count > 0:
            print(f"✓ User already has {existing_count} check-ins")
            response = input("Create more check-ins? (y/n): ")
            if response.lower() != 'y':
                return

        # Create 14 days of check-ins
        base_date = datetime.now() - timedelta(days=14)

        mood_patterns = [
            # Week 1: Gradual improvement
            (5, 4, 6, "Feeling a bit down today. Work was stressful."),
            (5, 5, 5, "Okay day. Nothing special."),
            (6, 5, 5, "Had a good conversation with a friend. Feeling better."),
            (6, 6, 4, "Productive day at work. Feeling accomplished."),
            (7, 7, 4, "Great day! Went for a walk and felt energized."),
            (7, 6, 3, "Weekend started well. Relaxed and rested."),
            (8, 7, 3, "Wonderful Sunday. Spent time with family."),
            # Week 2: Some ups and downs
            (7, 6, 4, "Back to work but feeling good."),
            (6, 5, 5, "Bit tired today but manageable."),
            (6, 6, 4, "Tried meditation. It helped!"),
            (7, 7, 3, "Feeling motivated and positive."),
            (7, 6, 4, "Had some anxiety but used breathing exercises."),
            (8, 7, 3, "Really good day. Everything clicked."),
            (8, 8, 2, "Best day in a while! Feeling grateful."),
        ]

        emotions_pool = [
            ["happy", "content"],
            ["neutral", "okay"],
            ["hopeful", "optimistic"],
            ["productive", "accomplished"],
            ["energized", "motivated"],
            ["calm", "peaceful"],
            ["grateful", "thankful"],
            ["neutral", "tired"],
            ["anxious", "worried"],
            ["hopeful", "determined"],
        ]

        created_count = 0
        for i, (mood, energy, anxiety, journal) in enumerate(mood_patterns):
            # Create check-in
            checkin_date = base_date + timedelta(days=i)

            checkin = MoodCheckin(
                id=uuid.uuid4(),
                user_id=user.id,
                mood_score=mood,
                energy_level=energy,
                anxiety_level=anxiety,
                stress_level=random.randint(2, 6),
                emotion_tags=random.choice(emotions_pool),
                journal_text=journal,
                context_location="home" if i % 2 == 0 else "work",
                context_activity="relaxing" if i % 3 == 0 else "working",
                created_at=checkin_date
            )

            db.add(checkin)
            created_count += 1

        db.commit()
        print(f"\n✓ Created {created_count} test check-ins")
        print(f"  Date range: {base_date.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}")
        print(f"  Mood range: 5-8 (showing improvement over time)")
        print("\nYou can now:")
        print("  1. View dashboard to see mood chart")
        print("  2. Check insights for patterns (after 21 days, you can train ML model)")
        print("  3. Create more check-ins manually")

    except Exception as e:
        print(f"✗ Error creating test data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("CREATE TEST CHECK-IN DATA")
    print("=" * 60)
    print()
    create_test_checkins()
    print()
    print("=" * 60)
