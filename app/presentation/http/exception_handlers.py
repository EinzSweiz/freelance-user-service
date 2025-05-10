from fastapi import Request
from fastapi.responses import JSONResponse
from app.domain.exceptions import UserAlreadyExists, InvalidCredentials


async def user_already_exists_handler(request: Request, exc: UserAlreadyExists):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)}
    )

async def invalid_credentials_handler(request: Request, exc: InvalidCredentials):
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc)}
    )
