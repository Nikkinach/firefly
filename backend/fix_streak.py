"""
Check and fix streak for nikki@demo.com
Ensures consecutive days ending with today
"""

from app.core.database import SessionLocal
from app.models.user import User
from app.models.checkin import MoodCheckin
from datetime import datetime, timedelta
import uuid

db = SessionLocal()

# Find user
user = db.query(User).filter(User.email == "nikki@demo.com").first()

if not user:
    print("ERROR: User not found")
    exit(1)

# Get all check-ins
all_checkins = db.query(MoodCheckin).filter(MoodCheckin.user_id == user.id).order_by(MoodCheckin.created_at).all()
dates_with_checkins = set([c.created_at.date() for c in all_checkins])

print(f"User: {user.email}")
print(f"Total check-ins: {len(all_checkins)}")
print(f"Unique days: {len(dates_with_checkins)}")

# Calculate current streak
today = datetime.now().date()
streak = 0

for i in range(100):  # Check up to 100 days back
    check_date = today - timedelta(days=i)
    if check_date in dates_with_checkins:
        streak += 1
    else:
        break

print(f"\nCurrent streak: {streak} days")

if streak == 0:
    print("\nNO CURRENT STREAK - Last check-in not today")
    print("Adding today's check-in...")

    # Add today's check-in
    today_checkin = MoodCheckin(
        id=uuid.uuid4(),
        user_id=user.id,
        mood_score=8,
        energy_level=8,
        anxiety_level=3,
        stress_level=3,
        emotion_tags=['happy', 'motivated'],
        journal_text='Testing Firefly today! The ML features look incredible. So excited!',
        context_location='home',
        context_activity='working',
        context_social='alone',
        created_at=datetime.now()
    )
    db.add(today_checkin)
    db.commit()

    # Recalculate
    streak = 1
    for i in range(1, 100):
        check_date = today - timedelta(days=i)
        if check_date in dates_with_checkins:
            streak += 1
        else:
            break

    print(f"STREAK FIXED! Current streak: {streak} days")

else:
    print(f"\nStreak is good! {streak} consecutive days")

# Show last 7 days
print(f"\nLast 7 days:")
for i in range(6, -1, -1):
    check_date = today - timedelta(days=i)
    has_checkin = check_date in dates_with_checkins
    status = "YES" if has_checkin else "NO"
    print(f"  {check_date} ({check_date.strftime('%A')}): {status}")

db.close()

print(f"\nTotal unique days with check-ins: {len(dates_with_checkins) + (1 if streak > 0 else 0)}")
print("Refresh your dashboard to see the streak!")
