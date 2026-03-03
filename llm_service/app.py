import logging

import uvicorn
from fastapi import FastAPI

from src.router.agent import router as agent_router
from src.utils.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(title="Tool Agent - LLM Service")

app.include_router(agent_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.LLM_SERVICE_PORT)
