from fastapi import Depends, Request
from src.utilities.route_builder import build_router
from src.apps.auth.services.user_services import UserAuthService
from src.apps.auth.schemas import LoginSchema, RegisterSchema
from src.utilities.jwt import JWTService

user_router = build_router(path="user", tags=["Users"])


@user_router.post("/register", status_code=201)
async def register(dto: RegisterSchema, request: Request):
    return await UserAuthService.create(dto=dto, request=request)


@user_router.post("/login")
async def login(dto: LoginSchema, request: Request):
    return await UserAuthService.login(dto=dto, request=request)


@user_router.get("/whoami")
async def whoami(user=Depends(JWTService.get_current_user)):
    return user


@user_router.get("/users")
async def get_all_users():
    return await UserAuthService.all()
