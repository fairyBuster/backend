
from alembic.config import Config
from pydantic import BaseModel, ConfigDict , EmailStr
from datetime import datetime
from typing import  Optional





# mencari phone berdasarkan id
class ReferralUser(BaseModel):
    id: int
    phone: str
    model_config = ConfigDict(from_attributes=True)
       
class UserBase(BaseModel):
    phone: str
    username: str 
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    referral_by: Optional[int] = None
    referral_code: Optional[str] = None
  
    balance: Optional[int] = None
    balance_deposit: Optional[int] = None
    is_active: Optional[bool] = None
    
class UserRegister(UserBase):
    password: str
    
class UserLogin(BaseModel):
    phone:str
    password:str

# -- INI RESPONSE DARI SCHEMAS DATA YANG KELUAR --
class UserResponse(UserBase):
    id:int
    role:str
    is_active:bool
    created_at:datetime
    referral_user: Optional[ReferralUser] = None
    
    update_at:Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
   


    
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
    referral_by: Optional[int] = None
    referral_code: Optional[str] = None
    balance: Optional[int] = None
    balance_deposit: Optional[int] = None

