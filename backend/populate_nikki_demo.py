"""
Populate nikki@demo.com specifically with 60 days of test data
"""

from app.core.database import SessionLocal
from app.models.user import User
from app.models.checkin import MoodCheckin
from datetime import datetime, timedelta
import uuid
import random
import numpy as np

db = SessionLocal()

# Find nikki@demo.com specifically
user = db.query(User).filter(User.email == "nikki@demo.com").first()

if not user:
    print("ERROR: nikki@demo.com not found!")
    print("Available users:")
    all_users = db.query(User).all()
    for u in all_users:
        print(f"  - {u.email}")
    db.close()
    exit(1)

print(f"Populating data for: {user.email}")

# Delete existing check-ins
existing = db.query(MoodCheckin).filter(MoodCheckin.user_id == user.id).count()
print(f"Deleting {existing} existing check-ins...")
db.query(MoodCheckin).filter(MoodCheckin.user_id == user.id).delete()
db.commit()

# Generate 60 days of data
base_date = datetime.now() - timedelta(days=60)

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
    day_of_week = check_date.weekday()
    is_weekend = day_of_week >= 5

    # Upward trend + weekly pattern
    trend_factor = day / 60
    weekly_factor = 2 * np.sin(2 * np.pi * day / 7)

    base_mood = 4 + (trend_factor * 3) + weekly_factor + (1.5 if is_weekend else 0)
    mood = base_mood + random.uniform(-1, 1)
    mood = max(1, min(10, int(round(mood))))

    energy = mood + random.randint(-1, 1)
    energy = max(1, min(10, energy))

    anxiety = 11 - mood + random.randint(-2, 2)
    anxiety = max(1, min(10, anxiety))

    stress = random.randint(max(1, mood - 3), min(10, mood + 2))

    if mood <= 4:
        journal = random.choice(journal_templates['low'])
        emotions = random.choice(emotion_sets['low'])
    elif mood <= 7:
        journal = random.choice(journal_templates['medium'])
        emotions = random.choice(emotion_sets['medium'])
    else:
        journal = random.choice(journal_templates['high'])
        emotions = random.choice(emotion_sets['high'])

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

    if created % 10 == 0:
        db.commit()

db.commit()

# Get stats
all_checkins = db.query(MoodCheckin).filter(MoodCheckin.user_id == user.id).all()
moods = [c.mood_score for c in all_checkins]

print("\n" + "=" * 60)
print("SUCCESS!")
print("=" * 60)
print(f"Account: {user.email}")
print(f"Created: {created} check-ins")
print(f"Date range: {base_date.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}")
print(f"\nStats:")
print(f"  Average mood: {np.mean(moods):.1f}/10")
print(f"  Mood range: {min(moods)} - {max(moods)}")
print(f"  Good days (7+): {sum(1 for m in moods if m >= 7)}")
print(f"  Challenging days (<4): {sum(1 for m in moods if m <= 4)}")
print(f"  Improvement: {moods[0]} -> {moods[-1]}")
print("\nNow restart the app and login with nikki@demo.com!")
print("=" * 60)

db.close()
