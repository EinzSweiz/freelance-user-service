from app.infrastructure.redis.redis_token_service import RedisTokenBlacklist
from app.infrastructure.security.jwt import decode_token, create_access_token, create_refresh_token
from fastapi import HTTPException, status

async def refresh_access_token(refresh_token: str):
    payload = decode_token(refresh_token)
    jti = payload.get("jti")
    user_id = payload.get("sub")
    exp = payload.get("exp")

    if not jti or not user_id or not exp:
        raise HTTPException(status_code=400, detail="Invalid refresh token")

    redis_blacklist = RedisTokenBlacklist()
    if await redis_blacklist.is_token_blacklisted(jti):
        raise HTTPException(status_code=401, detail="Refresh token has been revoked")

    # Blacklist old token
    await redis_blacklist.blacklist_token(jti, exp)

    new_access_token = create_access_token({"sub": user_id})
    new_refresh_token = create_refresh_token({"sub": user_id})  # new JTI
    return new_access_token, new_refresh_token
