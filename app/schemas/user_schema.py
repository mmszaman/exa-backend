from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class SignupData(BaseModel):
    email: EmailStr
    newsletter: bool = False
    
class EmailResponse(BaseModel):
    message: str
    email: str

class UserData(BaseModel):
    verification_token: str
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=100)

class User(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class LoginData(BaseModel):
    email: EmailStr
    password: str

class AuthData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

class AccessToken(BaseModel):
    token: str

class UserEmail(BaseModel):
    email: EmailStr

class OtpData(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=4, max_length=4)

class OtpResponse(BaseModel):
    valid: bool
    message: str

class ResetPasswordData(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=4, max_length=4)
    new_password: str = Field(..., min_length=8)

class ResetPasswordResponse(BaseModel):
    message: str
    access_token: Optional[str] = None
    user: Optional[User] = None


class TokenResponse(BaseModel):
    message: str
    email: str
    verification_token: str
    is_verified: bool
    token_expiry: datetime.datetime
