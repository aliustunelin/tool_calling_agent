from fastapi import APIRouter
from pydantic import BaseModel

from src.service.auth_service import verify_login

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest):
    token = verify_login(body.username, body.password)
    return LoginResponse(token=token)
