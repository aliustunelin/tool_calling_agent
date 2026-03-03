import logging

import uvicorn
from fastapi import FastAPI

from src.router.auth import router as auth_router
from src.router.data_api import router as data_router
from src.utils.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(title="Tool Agent - API Service")

app.include_router(auth_router)
app.include_router(data_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.API_SERVICE_PORT)
