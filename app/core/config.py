from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise Financial Ledger & General Ledger API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./ledger.db"
    BASE_CURRENCY: str = "USD"

    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()