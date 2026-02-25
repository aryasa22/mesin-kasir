from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Mesin Kasir POS"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/mesin_kasir"
    store_name: str = "Mesin Kasir Store"

    # ESC/POS thermal printer configuration
    printer_mode: str = "network"  # network | usb
    printer_network_host: str = "127.0.0.1"
    printer_network_port: int = 9100
    printer_usb_vendor_id: int = 0x04B8
    printer_usb_product_id: int = 0x0202
    printer_usb_timeout_ms: int = 0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
