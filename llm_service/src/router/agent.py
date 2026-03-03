import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.service.agent_service import run_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["agent"])


class ChatRequest(BaseModel):
    message: str


class ToolCallLog(BaseModel):
    tool: str
    args: dict
    result: dict


class ChatResponse(BaseModel):
    response: str
    tool_calls_log: list[ToolCallLog]


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest):
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="Mesaj boş olamaz")

    logger.info("Kullanıcı mesajı: %s", body.message)

    try:
        result = await run_agent(body.message)
        return ChatResponse(**result)
    except Exception as e:
        logger.error("Agent hatası: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent hatası: {str(e)}")
