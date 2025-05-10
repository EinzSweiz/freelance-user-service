# app/infrastructure/security/middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException
from starlette.responses import JSONResponse
from jose import JWTError
from app.infrastructure.security.jwt import decode_token
from app.infrastructure.redis.redis_token_service import RedisTokenBlacklist


PUBLIC_PATHS = [
    "/auth/login",
    "/auth/register",
    "/auth/refresh",
    "/docs",
    "/openapi.json"
]


class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Разрешить доступ к публичным роутам
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401, content={"detail": "Authorization header missing or invalid"}
            )

        token = auth_header.split(" ")[1]

        try:
            payload = decode_token(token)
            jti = payload.get("jti")
            if jti:
                redis_blacklist = RedisTokenBlacklist()
                if await redis_blacklist.is_token_blacklisted(jti):
                    return JSONResponse(status_code=401, content={"detail": "Token has been revoked"})
            # Сохраняем user_id в request.state
            request.state.user_id = payload.get("sub")

        except JWTError:
            return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})

        return await call_next(request)
