#!/usr/bin/env python
"""
set_admin.py
Usage:
  python set_admin.py --email=adminuser@example.com
This script sets a user with the specified email as an admin (is_admin=True).
"""

import argparse
from app.database import SessionLocal
from app.models.user import User

def make_user_admin(email: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"[ERROR] User with email {email} does not exist.")
            return
        user.is_admin = True
        user.user_type = "admin"  # Also set user_type if you rely on that
        db.commit()
        db.refresh(user)
        print(f"[SUCCESS] {email} is now an admin user.")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set a user as admin.")
    parser.add_argument("--email", required=True, help="Email of the user to be admin")
    args = parser.parse_args()
    make_user_admin(args.email)
