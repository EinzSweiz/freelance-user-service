from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jose import JWTError
from app.infrastructure.security.jwt import decode_token
from app.domain.common.logger import AbstractLogger
from app.infrastructure.redis.redis_token_service import RedisTokenBlacklist
from app.infrastructure.logger.logger import get_logger

logger: AbstractLogger = get_logger()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        jti = payload.get("jti")

        if not user_id or not jti:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        redis_blacklist = RedisTokenBlacklist()
        if await redis_blacklist.is_token_blacklisted(jti):
            logger.warning(f"Token is blacklisted: {jti}")
            raise HTTPException(status_code=401, detail="Token has been revoked")

        logger.debug(f"Authenticated user_id from token: {user_id}")
        return user_id

    except JWTError as e:
        logger.warning(f"JWT decoding failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
