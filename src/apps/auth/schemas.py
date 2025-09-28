import datetime
import uuid  
from typing import Annotated, Optional
from pydantic import BaseModel, EmailStr, Field

## password reset schemas
class RequestResetSchema(BaseModel):
    email: EmailStr

class VerifyRequestSchema(BaseModel):
    token: str
    otp: str

class ResetPasswordSchema(BaseModel):
    token: str
    password: str


## Login, Register and Refresh Schema
class LoginSchema(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=6)]


class RegisterSchema(BaseModel):
    first_name: Optional[str] = Field(None, max_length=200)
    last_name: Optional[str] = Field(None, max_length=200)
    app_name: Optional[str] = Field(None, max_length=200)
    email: EmailStr
    password: Annotated[str, Field(min_length=6)]


class RefreshTokenDto(BaseModel):
    token: str

    

## Google Auth schema
class OauthASchema(BaseModel):
    token: str

## update schema profile
class Profile(BaseModel):
    first_name: Optional[str] = Field(None, max_length=200)
    last_name: Optional[str] = Field(None, max_length=200)
    app_name: Optional[str] = Field(None, max_length=200)
    email: Optional[EmailStr] = None


## response schema
class UserResponseDto(BaseModel):
    id: uuid.UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    is_verified: bool
    is_superuser: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True
