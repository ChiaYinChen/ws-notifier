"""Setting."""
from pydantic import BaseSettings, RedisDsn


class Settings(BaseSettings):

    TESTING: bool = False
    redis_dsn: RedisDsn = "redis://redis:6379"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
