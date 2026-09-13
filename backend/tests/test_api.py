from datetime import datetime, timedelta, timezone

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import Base
from app.main import app
from app.models import Plan, UsagePeriod
from app.repositories.usage import UsageRepository


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


def test_usage_returns_current_period_usage_from_postgres(monkeypatch):
    set_config(monkeypatch)
    engine = create_engine("postgresql+psycopg://speech:speech@localhost:5433/speech")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.query(UsagePeriod).filter_by(subject_id="usage-user").delete()
        session.query(Plan).filter_by(tier_id="plan-pro").delete()
        session.add(Plan(tier_id="plan-pro", name_en="Pro", name_es="Pro", keycloak_role="plan-pro", word_limit=100, period_unit="month"))
        session.commit()

    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = private.public_key()
    monkeypatch.setattr("app.auth.jwks_client", lambda _: type("Client", (), {"get_signing_key_from_jwt": lambda self, _: type("Key", (), {"key": public})()})())
    token = jwt.encode({"sub": "usage-user", "plan": ["plan-pro"], "iss": "http://localhost:8080/realms/speech", "exp": datetime.now(timezone.utc) + timedelta(minutes=1)}, private, algorithm="RS256")
    headers = {"Authorization": f"Bearer {token}"}

    with TestClient(app) as client:
        assert client.get("/usage", headers=headers).json() == {"used": 0, "limit": 100, "period": datetime.now(timezone.utc).strftime("%Y-%m"), "remaining": 100}
        with Session(engine) as session:
            UsageRepository(session).increment("usage-user", datetime.now(timezone.utc).strftime("%Y-%m"), 35)
        assert client.get("/usage", headers=headers).json()["used"] == 35


def set_config(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://speech:speech@localhost:5433/speech")
    monkeypatch.setenv("KEYCLOAK_ISSUER_URL", "http://localhost:8080/realms/speech")
    monkeypatch.setenv("KEYCLOAK_CLIENT_ID", "speech-dashboard-backend")
    monkeypatch.setenv("KEYCLOAK_CLIENT_SECRET", "dev-only-speech-dashboard-backend-secret")
    monkeypatch.setenv("STRIPE_API_KEY", "sk_test_mock")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_mock")
