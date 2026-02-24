from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Support AI Agent API"
    ENV: str = "dev"

    DATABASE_URL: str

    IMAP_HOST: str = ""
    IMAP_PORT: int = 993
    IMAP_USER: str = ""
    IMAP_PASSWORD: str = ""

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True

    API_KEY: str = "dev_api_key_change_me"
    KB_TS_CONFIG: str = "russian"  # russian / english etc.

settings = Settings()