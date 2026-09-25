from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    keycloak_issuer_url: str
    keycloak_jwks_base_url: str | None = None
    keycloak_client_id: str
    keycloak_client_secret: str
    stripe_api_key: str
    stripe_webhook_secret: str
    dashboard_url: str = "http://localhost:4321"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def get_settings() -> Settings:
    return Settings()
