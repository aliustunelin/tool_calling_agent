import logging

import httpx
from src.utils.config import settings

logger = logging.getLogger(__name__)

_token: str | None = None


async def _ensure_token(client: httpx.AsyncClient) -> str:
    global _token
    if _token is not None:
        return _token

    resp = await client.post(
        f"{settings.API_SERVICE_URL}/auth/login",
        json={"username": settings.API_USERNAME, "password": settings.API_PASSWORD},
    )
    resp.raise_for_status()
    _token = resp.json()["token"]
    logger.info("API token alındı.")
    return _token


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def list_users() -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        token = await _ensure_token(client)
        resp = await client.get(
            f"{settings.API_SERVICE_URL}/api/users/list",
            headers=_auth_headers(token),
        )
        resp.raise_for_status()
        return resp.json()


async def get_user_details(email: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        token = await _ensure_token(client)
        resp = await client.post(
            f"{settings.API_SERVICE_URL}/api/users/details",
            json={"email": email},
            headers=_auth_headers(token),
        )
        if resp.status_code == 404:
            return {"error": resp.json().get("detail", "Kullanıcı bulunamadı")}
        resp.raise_for_status()
        return resp.json()


async def get_recent_transactions(user_id: str, limit: int = 5) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        token = await _ensure_token(client)
        resp = await client.post(
            f"{settings.API_SERVICE_URL}/api/transactions/recent",
            json={"user_id": user_id, "limit": limit},
            headers=_auth_headers(token),
        )
        if resp.status_code == 404:
            return {"error": resp.json().get("detail", "İşlem bulunamadı")}
        resp.raise_for_status()
        return resp.json()


async def check_fraud_reason(transaction_id: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        token = await _ensure_token(client)
        resp = await client.post(
            f"{settings.API_SERVICE_URL}/api/fraud/check",
            json={"transaction_id": transaction_id},
            headers=_auth_headers(token),
        )
        if resp.status_code == 404:
            return {"error": resp.json().get("detail", "Fraud kaydı bulunamadı")}
        resp.raise_for_status()
        return resp.json()
