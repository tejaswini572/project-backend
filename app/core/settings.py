from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    debug: bool = False
    app_env: str = "development"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
