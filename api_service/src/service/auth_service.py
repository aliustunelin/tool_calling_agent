from fastapi import Header, HTTPException
from src.utils.config import settings


def verify_login(username: str, password: str) -> str:
    if username == settings.API_USERNAME and password == settings.API_PASSWORD:
        return settings.STATIC_TOKEN
    raise HTTPException(status_code=401, detail="Geçersiz kullanıcı adı veya şifre")


def token_guard(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Geçersiz Authorization header formatı")

    token = authorization.removeprefix("Bearer ").strip()
    if token != settings.STATIC_TOKEN:
        raise HTTPException(status_code=401, detail="Geçersiz token")

    return token
