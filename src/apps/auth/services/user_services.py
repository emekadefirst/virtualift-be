from tortoise.expressions import Q
from tortoise import timezone
from fastapi import Query, Request
from src.utilities.jwt import JWTService
from src.error.base import ErrorHandler
from src.utilities.base_service import BaseModelService
from src.apps.auth.models import User
from src.apps.auth.schemas import RegisterSchema, LoginSchema
from src.utilities.crypto import verify_password


class UserAuthService:
    boa = BaseModelService(User)
    model = User
    error = ErrorHandler(User)
    jwt = JWTService

    @staticmethod
    def extract_ip(request: Request) -> str:
        """
        Extract real client IP, checking forwarded headers.
        """
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.client.host
        return ip
    
    @classmethod
    async def create(cls, dto: RegisterSchema, request: Request):
        exists = await cls.model.filter(Q(email=dto.email)).exists()
        if exists:
            return cls.error.get(400, detail="Email already registered")

        ip_address = cls.extract_ip(request)

        user = await cls.model.create(**dto.model_dump(), ip_address=ip_address)
        if not user:
            return cls.error.get(400, message="User creation failed")
        return cls.jwt.generate_token(str(user.id))

    @classmethod
    async def login(cls, dto: LoginSchema, request: Request):
        user = await cls.model.filter(Q(email=dto.email)).first()
        if not user:
            return cls.error.get(401, message="Invalid credentials")
        if not verify_password(user.password, dto.password):
            return cls.error.get(401, message="Invalid credentials")
        ip_address = cls.extract_ip(request)
        user.ip_address = ip_address
        user.last_login = timezone.now()
        await user.save()
        return cls.jwt.generate_token(str(user.id))
    
    @classmethod
    async def all(cls):
        return await cls.boa.all()

    @classmethod
    async def all_with_permissions(cls):
        return await cls.boa.all_with_related(["permission_groups"])
    
    

