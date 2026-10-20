from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    app_name: str = "Awesome API"
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    database_url: str
    cors_allowed_origins: list[str] = ["*"]


settings = Settings()
