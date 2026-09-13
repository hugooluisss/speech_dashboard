from contextlib import nullcontext

from fastapi.testclient import TestClient

from app.auth import Claims, validate_token
from app.main import app
from app.models import Plan, User, UsagePeriod, UserSubscription
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    from app.db import Base
    Base.metadata.create_all(engine)
    return Session(engine)


def test_admin_users_list_and_gate(monkeypatch):
    for key, value in {"DATABASE_URL": "sqlite://", "KEYCLOAK_ISSUER_URL": "http://keycloak/realms/speech", "KEYCLOAK_CLIENT_ID": "client", "KEYCLOAK_CLIENT_SECRET": "secret", "STRIPE_API_KEY": "sk_test_mock", "STRIPE_WEBHOOK_SECRET": "whsec_mock"}.items():
        monkeypatch.setenv(key, value)
    session = db()
    session.add_all([Plan(tier_id="plan-free", display_name="Free", keycloak_role="plan-free", word_limit=100, period_unit="month", active=True), User(subject_id="u1"), UserSubscription(subject_id="u1", status="active", plan_tier_id="plan-free"), UsagePeriod(subject_id="u1", period_key="2026-09", words_used=7)])
    session.commit()
    monkeypatch.setattr("app.controllers.admin.session_factory", lambda: lambda: nullcontext(session))
    app.dependency_overrides[validate_token] = lambda: Claims("admin-user", "plan-free", True)
    try:
        with TestClient(app) as client:
            assert client.get("/admin/users").json()[0]["usage"] == 7
            app.dependency_overrides[validate_token] = lambda: Claims("u2", "plan-free")
            spanish = client.get("/admin/users", headers={"Accept-Language": "es"})
            english = client.get("/admin/users")
            assert spanish.status_code == english.status_code == 403
            assert spanish.json()["detail"] == "Se requiere el rol de administrador"
            assert english.json()["detail"] == "Admin role required"
    finally:
        app.dependency_overrides.clear()
