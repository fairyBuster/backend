from app.routers.auth import router
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse,UserUpdate,UserRegister
from app.utils.auth import get_admin_user, hash_password

router = APIRouter(prefix="/admin",tags=["admin"])

@router.get("/users", response_model = List[UserResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin : User = Depends(get_admin_user)
):
    return db.query(User).offset(skip).limit(limit).all()


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id:int,
    db: Session = Depends(get_db),
    admin : User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
   user_id: int,
   user_update: UserUpdate,
   db: Session = Depends(get_db),
   admin : User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    update_data = user_update.model_dump(exclude_unset=True) # mengabaikan field yang tidak diupdate
    print(update_data)
    for key, value in update_data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
  
    return user

@router.delete("/users/{user_id}")
def delete_user(
    user_id:int,
    db: Session = Depends(get_db),
    admin : User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.role == "admin":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin user cannot be deleted")

    db.delete(user)
    db.commit()
    return {"message":f"User {user.phone} deleted successfully"}


@router.patch("/users/{user_id}/toggle-active")
def toggle_active(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Suspend atau aktifkan kembali akun user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User ID {user_id} not found")

    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return {"message":f"User {user.phone} active status toggled successfully"}


