from sqlalchemy import Column, ForeignKey, Integer, String, DateTime,Boolean,BigInteger
from app.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True ) #index True berarti akan dibuat index untuk kolom id tujuan untuk percepatan pencarian
    phone = Column(String, index=True, unique=True, nullable= False)
    username = Column(String, index=True, unique=True, nullable=False)
    email = Column(String, index=True, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String, nullable=False)
    balance = Column(BigInteger, default=0)
    balance_deposit = Column(BigInteger, default=0)
    referral_code = Column(String, nullable=False, default="", unique=True, index=True)
    referral_by = Column(Integer,ForeignKey("users.id"), nullable=True)
    referral_user = relationship("User", remote_side=[id])
    role = Column(String, default="user", nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


