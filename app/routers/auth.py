from app.models import user
from app.schemas.user import UserRegister
from fastapi import APIRouter , Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import User
from app.utils.auth import hash_password, verify_password, create_access_token, get_current_active_user,generate_referral_code,create_refresh_token
from app.schemas.user import UserResponse,UserLogin,UserRegister,TokenResponse, Token,RefreshTokenRequest,RefreshTokenResponse
from app.database import get_db
from sqlalchemy.orm import Session
from app.config import settings
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister , db: Session = Depends(get_db)):
    # cek email username dan password
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    if db.query(User).filter(User.phone == user_data.phone).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone already registered")

    # cek referral_code
    if user_data.referral_code:
        referral_user = db.query(User).filter(User.referral_code == user_data.referral_code).first()
        if not referral_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Referral_code not found")

        user_data.referral_by = referral_user.id

    new_user = User(
        email=user_data.email,
        username=user_data.username,
        phone=user_data.phone,
        hashed_password=hash_password(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        referral_by=user_data.referral_by,
        referral_code=generate_referral_code(db),
       
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully" }


@router.post("/token", response_model=Token)
def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    phone = form_data.username
    password = form_data.password

    user = db.query(User).filter(User.phone == phone).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone or password is incorrect")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not active")

    access_token = create_access_token(
        data={"sub": user.phone},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == user_data.phone).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not active")
    
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password is incorrect")

    token = create_access_token(
        data={"sub": user.phone},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    refresh = create_refresh_token(
        data={"sub": user.phone},
    )
    
    return {"access_token": token, "refresh_token": refresh, "token_type": "bearer" ,"user":user}

@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(
            data.refresh_token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        token_type = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token")

        phone = payload.get("sub")
        if not phone:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token")

        user = db.query(User).filter(User.phone == phone).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        access_token = create_access_token(
            data={"sub": phone},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        )
        refresh = create_refresh_token(
            data={"sub": phone},
        )
        return {"access_token": access_token, "refresh_token": refresh, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token")

@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_active_user)):
    return current_user
