from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    LLM_BASE_URL: str = "https://openrouter.ai/api/v1"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "openai/gpt-4o-mini"

    API_SERVICE_URL: str = "http://localhost:2198"

    API_USERNAME: str = "admin"
    API_PASSWORD: str = "changeme"

    LLM_SERVICE_PORT: int = 6712

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
