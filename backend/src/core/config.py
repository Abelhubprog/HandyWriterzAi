from pydantic import BaseSettings, PostgresDsn, RedisDsn

class Settings(BaseSettings):
    db_url: PostgresDsn
    redis_url: RedisDsn
    openrouter_key: str
    stripe_secret: str
    class Config:
        env_file = ".env"

settings = Settings()
