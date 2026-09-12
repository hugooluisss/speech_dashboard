from fastapi.testclient import TestClient

from app.main import app


def test_health(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://speech:speech@localhost/speech")
    monkeypatch.setenv("KEYCLOAK_ISSUER_URL", "http://localhost:8080/realms/speech")
    monkeypatch.setenv("KEYCLOAK_CLIENT_ID", "speech-dashboard-backend")
    monkeypatch.setenv("KEYCLOAK_CLIENT_SECRET", "test-secret")
    monkeypatch.setenv("STRIPE_API_KEY", "sk_test_mock")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_mock")
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}
