from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.presentation.schemas.user_schemas import UserRegisterRequest, UserLoginRequest, UserResponse, TokenResponse, RefreshTokenRequest

from app.services.user_service import UserService
from app.infrastructure.security.oauth2 import get_current_user, oauth2_scheme
from app.infrastructure.security.jwt import decode_token
from app.infrastructure.redis.redis_token_service import RedisTokenBlacklist
from jose.exceptions import ExpiredSignatureError
from app.services.auth_service import refresh_access_token
from typing import Annotated
from app.services.dependencies import get_user_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse)
async def register_user(
    data: UserRegisterRequest,
    user_service: Annotated[UserService, Depends(get_user_service)]
):
    user = await user_service.register(
        email=data.email,
        password=data.password,
        full_name=data.full_name,
        role=data.role,
    )
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
    )


@router.post("/login", response_model=TokenResponse)
async def login_user(
    data: UserLoginRequest,
    user_service: Annotated[UserService, Depends(get_user_service)]
):
    user_id, access_token, refresh_token = await user_service.login(
        email=data.email,
        password=data.password
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, user_id=str(user_id))

@router.post("/logout")
async def logout(
    data: RefreshTokenRequest,
    request: Request,
    user_service: UserService = Depends(get_user_service)
):
    try:
        payload = decode_token(data.refresh_token)
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token already expired")

    jti = payload.get("jti")
    exp = payload.get("exp")

    if not jti or not exp:
        raise HTTPException(status_code=400, detail="Invalid token")

    redis_blacklist = RedisTokenBlacklist()
    await user_service.logout(jti=jti, exp=exp, token_blacklist_service=redis_blacklist)

    return {"detail": "Successfully logged out"}

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token_route(data: RefreshTokenRequest):
    new_access_token, new_refresh_token = await refresh_access_token(data.refresh_token)
    payload = decode_token(new_refresh_token)
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        user_id=payload.get("sub")
    )

@router.get("/me")
async def get_my_user_id(request: Request):
    user_id = request.state.user_id
    return {"message": f"Hello! Your user ID is: {user_id}"}
