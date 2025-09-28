import jwt
from argon2 import PasswordHasher
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta, timezone
from fastapi import Depends
from jwt import ExpiredSignatureError, InvalidTokenError, decode
from src.apps.auth import User
from src.error.base import ErrorHandler
from src.configs.env import (
    JWT_ACCESS_EXPIRY,
    JWT_REFRESH_EXPIRY,
    JWT_ACCESS_SECRET,
    JWT_ALGORITHM,
)

error = ErrorHandler(User)



class JWTService:
    @staticmethod
    def generate_token(subject: str) -> dict:
        now = datetime.now(timezone.utc)

        access_exp = now + timedelta(minutes=JWT_ACCESS_EXPIRY)
        refresh_exp = now + timedelta(days=JWT_REFRESH_EXPIRY)

        access_payload = {
            "sub": str(subject),
            "exp": access_exp,
            "type": "access",
        }

        refresh_payload = {
            "sub": str(subject),
            "exp": refresh_exp,
            "type": "refresh",
        }

        access_token = jwt.encode(access_payload, JWT_ACCESS_SECRET, algorithm=JWT_ALGORITHM)
        refresh_token = jwt.encode(refresh_payload, JWT_ACCESS_SECRET, algorithm=JWT_ALGORITHM)

        return {"access_token": access_token, "refresh_token": refresh_token}

    @staticmethod
    def decode_token(token: str):
        try:
            return jwt.decode(token, JWT_ACCESS_SECRET, algorithms=[JWT_ALGORITHM])
        except ExpiredSignatureError:
            raise error.get(401, "Token has expired")
        except InvalidTokenError:
            raise error.get(401, "Invalid token")

    @staticmethod
    def refresh_token(refresh_token: str) -> dict:
        payload = JWTService.decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise error.get(401, "Invalid token type")
        subject = payload.get("sub")
        return JWTService.generate_token(subject)

    @staticmethod
    def get_subject(token: str) -> str:
        payload = JWTService.decode_token(token)
        return payload.get("sub")

    @staticmethod
    async def get_current_user(
        token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    ):
        from src.apps.auth.models import User 
        error = ErrorHandler(User)

        payload = JWTService.decode_token(token.credentials)
        user_id: str = payload.get("sub")
        if not user_id:
            raise error.get(400, "Invalid authentication credentials")

        user = await User.get_or_none(id=user_id)
        if not user:
            raise error.get(404, "User not found")
        return user
