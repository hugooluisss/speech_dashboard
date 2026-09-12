from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    keycloak_issuer_url: str
    keycloak_client_id: str
    keycloak_client_secret: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def get_settings() -> Settings:
    return Settings()
