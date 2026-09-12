from datetime import datetime, timedelta, timezone

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException

from app.auth import extract_claims, validate_token


def test_extracts_subject_and_plan():
    assert extract_claims({"sub": "user-1", "plan": ["plan-pro"]}).plan == "plan-pro"


def test_token_validation_covers_valid_expired_and_bad_signature(monkeypatch):
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = private.public_key()
    monkeypatch.setattr("app.auth.jwks_client", lambda _: type("Client", (), {"get_signing_key_from_jwt": lambda self, _: type("Key", (), {"key": public})()})())
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://speech:speech@localhost/speech")
    monkeypatch.setenv("KEYCLOAK_ISSUER_URL", "http://localhost:8080/realms/speech")
    monkeypatch.setenv("KEYCLOAK_CLIENT_ID", "speech-dashboard-backend")
    monkeypatch.setenv("KEYCLOAK_CLIENT_SECRET", "test-secret")
    monkeypatch.setenv("STRIPE_API_KEY", "sk_test_mock")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_mock")
    base = {"sub": "user-1", "plan": ["plan-pro"], "iss": "http://localhost:8080/realms/speech"}
    valid = jwt.encode({**base, "exp": datetime.now(timezone.utc) + timedelta(minutes=1)}, private, algorithm="RS256")
    assert validate_token(type("Credentials", (), {"credentials": valid})()).subject_id == "user-1"
    expired = jwt.encode({**base, "exp": datetime.now(timezone.utc) - timedelta(minutes=1)}, private, algorithm="RS256")
    with pytest.raises(HTTPException):
        validate_token(type("Credentials", (), {"credentials": expired})())
    with pytest.raises(HTTPException):
        validate_token(type("Credentials", (), {"credentials": valid + "bad"})())
