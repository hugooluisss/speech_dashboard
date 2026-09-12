from datetime import datetime, timedelta, timezone

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from app.main import app


def test_protected_me_rejects_missing_token(monkeypatch):
    set_config(monkeypatch)
    with TestClient(app) as client:
        assert client.get("/me").status_code == 401


def test_me_returns_claims_and_persists_user_in_postgres(monkeypatch):
    set_config(monkeypatch)
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = private.public_key()
    monkeypatch.setattr("app.auth.jwks_client", lambda _: type("Client", (), {"get_signing_key_from_jwt": lambda self, _: type("Key", (), {"key": public})()})())
    token = jwt.encode({"sub": "integration-user", "plan": ["plan-pro"], "iss": "http://localhost:8080/realms/speech", "exp": datetime.now(timezone.utc) + timedelta(minutes=1)}, private, algorithm="RS256")
    with TestClient(app) as client:
        response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json() == {"subject_id": "integration-user", "plan": "plan-pro"}


def set_config(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://speech:speech@localhost:5433/speech")
    monkeypatch.setenv("KEYCLOAK_ISSUER_URL", "http://localhost:8080/realms/speech")
    monkeypatch.setenv("KEYCLOAK_CLIENT_ID", "speech-dashboard-backend")
    monkeypatch.setenv("KEYCLOAK_CLIENT_SECRET", "dev-only-speech-dashboard-backend-secret")
