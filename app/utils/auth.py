from datetime import datetime,timedelta

from typing import Optional
from jose import JWTError,jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models.user import User
import random
import string



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# -- Pasword--
def hash_password(password: str) -> str:
    return pwd_context.hash(password)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data:dict , expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def create_refresh_token(data :dict) -> str:
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=7)
    to_encode.update({"exp": expire , "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def decode_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload.get("sub") #subject = phone user

    except JWTError:
        return None

#-- DEPENDENCY--
# Tujuan: untuk mengambil user yang login login
def generate_referral_code(db, length: int = 6) -> str:
    """
    Generate referral code
    """
    chars = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choices(chars, k=length))
        exists = db.query(User).filter(User.referral_code == code).first()
        if not exists:
            return code
  

def get_current_user(
    token: str = Depends(oauth2_scheme), # ← ambil token dari header
    db: Session = Depends(get_db) # ← ambil database dari dependency
)-> User:
    """
    Decode token → cari user di DB → kembalikan user object
    """
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token not valid",
        headers={"WWW-Authenticate": "Bearer"}
    )
    phone = decode_access_token(token)
    if not phone:
        raise error
    user = db.query(User).filter(User.phone == phone).first()
    if not user:
        raise error
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
)-> User:
    """
    Ambil user yang login login
    """
    if current_user.is_active:
        return current_user
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Inactive user",
        headers={"WWW-Authenticate": "Bearer"}
    )
def get_admin_user(
    current_user: User = Depends(get_current_active_user)
)-> User:
    """
    Ambil user yang login login dan adalah admin
    """
    if current_user.role != "admin":
     
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not admin",
            headers={"WWW-Authenticate": "Bearer"}

    )
