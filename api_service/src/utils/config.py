from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGO_URI: str
    MONGO_DB_NAME: str = "tool_agent_demo"

    API_USERNAME: str = "admin"
    API_PASSWORD: str = "changeme"
    STATIC_TOKEN: str = "changeme-static-token"

    API_SERVICE_PORT: int = 2198

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
