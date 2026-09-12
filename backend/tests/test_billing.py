from types import SimpleNamespace

import pytest
import stripe
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.models import Plan, User, UserSubscription
from app.repositories.plans import PlanRepository
from app.repositories.subscriptions import SubscriptionRepository
from app.services.billing import BillingService
from fastapi.testclient import TestClient
from app.main import app
from app.auth import Claims, validate_token
from contextlib import nullcontext


def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    from app.db import Base
    Base.metadata.create_all(engine)
    return Session(engine)


def test_checkout_sets_subject_metadata_and_rejects_unknown(monkeypatch):
    session = db()
    session.add_all([Plan(tier_id="plan-free", display_name="Free", keycloak_role="plan-free", word_limit=0, period_unit="month", active=True), Plan(tier_id="plan-pro", display_name="Pro", keycloak_role="plan-pro", stripe_price_id="price_pro", word_limit=1000, period_unit="month", active=True)])
    session.commit()
    created = SimpleNamespace(url="https://checkout.test")
    monkeypatch.setattr("app.services.billing.stripe.checkout.Session.create", lambda **kwargs: (assert_metadata(kwargs), created)[1])
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    monkeypatch.setenv("KEYCLOAK_ISSUER_URL", "http://keycloak/realms/speech")
    monkeypatch.setenv("KEYCLOAK_CLIENT_ID", "client")
    monkeypatch.setenv("KEYCLOAK_CLIENT_SECRET", "secret")
    monkeypatch.setenv("STRIPE_API_KEY", "sk_test_mock")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_mock")
    service = BillingService(PlanRepository(session), SubscriptionRepository(session), keycloak=SimpleNamespace())
    assert service.create_checkout_session(User(subject_id="u1"), "plan-pro").url == "https://checkout.test"
    with pytest.raises(Exception):
        service.create_checkout_session(User(subject_id="u1"), "missing")


def test_portal_requires_customer_and_returns_url(monkeypatch):
    for key, value in {"DATABASE_URL": "sqlite://", "KEYCLOAK_ISSUER_URL": "http://keycloak/realms/speech", "KEYCLOAK_CLIENT_ID": "client", "KEYCLOAK_CLIENT_SECRET": "secret", "STRIPE_API_KEY": "sk_test_mock", "STRIPE_WEBHOOK_SECRET": "whsec_mock"}.items():
        monkeypatch.setenv(key, value)
    session = db()
    session.add(UserSubscription(subject_id="u1", stripe_customer_id="cus_1", status="active", plan_tier_id="plan-pro"))
    session.commit()
    monkeypatch.setenv("STRIPE_API_KEY", "sk_test_mock")
    def create_portal(**kwargs):
        assert kwargs["customer"] == "cus_1"
        return SimpleNamespace(url="https://billing.test")
    monkeypatch.setattr("app.services.billing.stripe.billing_portal.Session.create", create_portal)
    service = BillingService(PlanRepository(session), SubscriptionRepository(session), keycloak=SimpleNamespace())
    assert service.create_portal_session("u1").url == "https://billing.test"
    with pytest.raises(Exception):
        service.create_portal_session("missing")


def assert_metadata(kwargs):
    assert kwargs["metadata"] == {"subject_id": "u1"}


def test_subscription_events_swap_and_cancel_roles(monkeypatch):
    session = db()
    session.add_all([Plan(tier_id="plan-free", display_name="Free", keycloak_role="plan-free", word_limit=0, period_unit="month", active=True), Plan(tier_id="plan-pro", display_name="Pro", keycloak_role="plan-pro", stripe_price_id="price_pro", word_limit=1000, period_unit="month", active=True), UserSubscription(subject_id="u1", stripe_customer_id="cus_1", status="active", plan_tier_id="plan-pro")])
    session.commit()
    calls = []
    service = BillingService(PlanRepository(session), SubscriptionRepository(session), keycloak=SimpleNamespace(set_plan=lambda user, role: calls.append((user, role))))
    event = lambda typ, status, price: {"type": typ, "data": {"object": {"id": "sub_1", "customer": "cus_1", "status": status, "items": {"data": [{"price": {"id": price}}]}}}}
    service.handle_subscription_event(event("customer.subscription.updated", "active", "price_pro"))
    service.handle_subscription_event(event("customer.subscription.deleted", "canceled", "price_pro"))
    assert calls == [("u1", "plan-pro"), ("u1", "plan-free")]


def test_webhook_rejects_invalid_signature_before_business_logic(monkeypatch):
    for key, value in {"DATABASE_URL": "sqlite://", "KEYCLOAK_ISSUER_URL": "http://keycloak/realms/speech", "KEYCLOAK_CLIENT_ID": "client", "KEYCLOAK_CLIENT_SECRET": "secret", "STRIPE_API_KEY": "sk_test_mock", "STRIPE_WEBHOOK_SECRET": "whsec_mock"}.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr("app.controllers.billing.session_factory", lambda: (_ for _ in ()).throw(AssertionError("business logic called")))
    with TestClient(app) as client:
        assert client.post("/billing/webhook", content=b"{}", headers={"stripe-signature": "bad"}).status_code == 400


def test_catalog_and_checkout_routes(monkeypatch):
    for key, value in {"DATABASE_URL": "sqlite://", "KEYCLOAK_ISSUER_URL": "http://keycloak/realms/speech", "KEYCLOAK_CLIENT_ID": "client", "KEYCLOAK_CLIENT_SECRET": "secret", "STRIPE_API_KEY": "sk_test_mock", "STRIPE_WEBHOOK_SECRET": "whsec_mock"}.items():
        monkeypatch.setenv(key, value)
    session = db()
    session.add(Plan(tier_id="plan-pro", display_name="Pro", keycloak_role="plan-pro", stripe_price_id="price_pro", word_limit=1000, period_unit="month", active=True))
    session.commit()
    monkeypatch.setattr("app.controllers.plans.session_factory", lambda: lambda: nullcontext(session))
    monkeypatch.setattr("app.controllers.billing.session_factory", lambda: lambda: nullcontext(session))
    monkeypatch.setattr("app.services.billing.KeycloakAdmin", lambda: SimpleNamespace())
    monkeypatch.setattr("app.services.billing.stripe.checkout.Session.create", lambda **_: SimpleNamespace(url="https://checkout.test"))
    app.dependency_overrides[validate_token] = lambda: Claims("u1", "plan-free")
    try:
        with TestClient(app) as client:
            assert client.get("/plans").json()[0]["tier_id"] == "plan-pro"
            assert client.post("/billing/checkout", params={"plan_id": "plan-pro"}).json() == {"url": "https://checkout.test"}
            assert client.post("/billing/checkout", params={"plan_id": "missing"}).status_code == 400
    finally:
        app.dependency_overrides.clear()


def test_signed_webhook_wires_to_service(monkeypatch):
    for key, value in {"DATABASE_URL": "sqlite://", "KEYCLOAK_ISSUER_URL": "http://keycloak/realms/speech", "KEYCLOAK_CLIENT_ID": "client", "KEYCLOAK_CLIENT_SECRET": "secret", "STRIPE_API_KEY": "sk_test_mock", "STRIPE_WEBHOOK_SECRET": "whsec_mock"}.items():
        monkeypatch.setenv(key, value)
    session = db()
    monkeypatch.setattr("app.controllers.billing.session_factory", lambda: lambda: nullcontext(session))
    called = []
    monkeypatch.setattr("app.controllers.billing.stripe.Webhook.construct_event", lambda payload, signature, secret: {"type": "customer.subscription.updated", "data": {"object": {}}})
    monkeypatch.setattr("app.controllers.billing.BillingService", lambda *args: SimpleNamespace(handle_subscription_event=lambda event: called.append(event)))
    with TestClient(app) as client:
        assert client.post("/billing/webhook", content=b"sample", headers={"stripe-signature": "signed"}).json() == {"received": True}
    assert called[0]["type"] == "customer.subscription.updated"
