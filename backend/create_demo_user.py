"""
Simple script to create demo user Nikki
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.services.auth import AuthService

# Ensure tables exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Check if user exists
    existing = db.query(User).filter(User.email == "nikki@demo.com").first()

    if existing:
        print(f"User already exists with ID: {existing.id}")
        # Update password just in case
        existing.password_hash = AuthService.get_password_hash("demo123")
        db.commit()
        print("Password updated to: demo123")
    else:
        # Create new user
        user = User(
            email="nikki@demo.com",
            password_hash=AuthService.get_password_hash("demo123"),
            display_name="Nikki",
            is_active=True,
            is_premium=True,
            has_adhd=True,
            has_anxiety=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created user Nikki with ID: {user.id}")

    print("\nLogin credentials:")
    print("  Email: nikki@demo.com")
    print("  Password: demo123")

finally:
    db.close()
