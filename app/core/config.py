from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Mesin Kasir POS"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/mesin_kasir"
    store_name: str = "Mesin Kasir Store"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
