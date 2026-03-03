import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.service.auth_service import token_guard
from src.service.mongo_service import (
    get_user_details,
    get_recent_transactions,
    check_fraud_reason,
    check_connection,
    list_users,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["data"])


# --- Request / Response Models ---

class UserDetailsRequest(BaseModel):
    email: str


class TransactionsRequest(BaseModel):
    user_id: str
    limit: int = 5


class FraudCheckRequest(BaseModel):
    transaction_id: str


# --- Endpoints ---

@router.get("/health")
def health():
    db_ok = check_connection()
    return {"status": "ok" if db_ok else "error", "db": "connected" if db_ok else "disconnected"}


@router.get("/users/list")
def users_list(_token: str = Depends(token_guard)):
    users = list_users()
    return {"users": users, "count": len(users)}


@router.post("/users/details")
def user_details(body: UserDetailsRequest, _token: str = Depends(token_guard)):
    try:
        result = get_user_details(body.email)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/transactions/recent")
def recent_transactions(body: TransactionsRequest, _token: str = Depends(token_guard)):
    try:
        result = get_recent_transactions(body.user_id, body.limit)
        return {"transactions": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/fraud/check")
def fraud_check(body: FraudCheckRequest, _token: str = Depends(token_guard)):
    try:
        result = check_fraud_reason(body.transaction_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
