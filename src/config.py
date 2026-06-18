from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL:str
    JWT_SECRET: str               # load from env
    JWT_ALGORITHM: str = "HS256"
    JWT_AUDIENCE: str = "fastapi-app"
    JWT_ISSUER: str = "auth-service"
    ACCESS_TOKEN_EXPIRY_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRY_DAYS: int = 7
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD:str | None=None

    model_config = SettingsConfigDict(
        env_file= ".env",
        extra="ignore"
    )

CONF = Settings()