from app.database import SessionLocal
from app.models.user import User
from app.utils.auth import hash_password, generate_referral_code
from sqlalchemy import or_

def seed():
    db = SessionLocal()
    try:
        email = "admin@admin.com"
        username = "admin123"
        phone = "123456789"

        existing_user = (
            db.query(User)
            .filter(or_(User.email == email, User.username == username, User.phone == phone))
            .first()
        )
        if existing_user:
            return existing_user

        user = User(
            email=email,
            hashed_password=hash_password("qwaszx555"),
            referral_code=generate_referral_code(db),
            first_name="admin",
            last_name="admin",
            username=username,
            role="admin",
            phone=phone,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()

if __name__ == "__main__":
    seed()
    print("Seed completed")
