import httpx
import stripe
from fastapi import HTTPException

from app.config import get_settings
from app.repositories.plans import PlanRepository
from app.repositories.subscriptions import SubscriptionRepository
from app.messages import message


class KeycloakAdmin:
    def __init__(self, settings=None):
        self.settings = settings or get_settings()

    def set_plan(self, subject_id: str, role_name: str):
        base = self.settings.keycloak_issuer_url.rstrip("/").replace("/realms/", "/admin/realms/")
        with httpx.Client() as client:
            token = client.post(f"{self.settings.keycloak_issuer_url.rstrip('/')}/protocol/openid-connect/token", data={"grant_type": "client_credentials", "client_id": self.settings.keycloak_client_id, "client_secret": self.settings.keycloak_client_secret}).raise_for_status().json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            roles = client.get(f"{base}/users/{subject_id}/role-mappings/realm", headers=headers).raise_for_status().json()
            old = [r for r in roles if r.get("name", "").startswith("plan-")]
            if old:
                client.request("DELETE", f"{base}/users/{subject_id}/role-mappings/realm", headers=headers, json=old).raise_for_status()
            role = client.get(f"{base}/roles/{role_name}", headers=headers).raise_for_status().json()
            client.post(f"{base}/users/{subject_id}/role-mappings/realm", headers=headers, json=[role]).raise_for_status()


class BillingService:
    def __init__(self, plans: PlanRepository, subscriptions: SubscriptionRepository, keycloak=None):
        self.plans, self.subscriptions, self.keycloak = plans, subscriptions, keycloak or KeycloakAdmin()

    def create_checkout_session(self, user, plan_id: str, accept_language: str | None = None):
        plan = self.plans.get(plan_id)
        if not plan or not plan.active or not plan.stripe_price_id:
            raise HTTPException(status_code=400, detail=message('unknown_plan', accept_language))
        stripe.api_key = get_settings().stripe_api_key
        return stripe.checkout.Session.create(mode="subscription", line_items=[{"price": plan.stripe_price_id, "quantity": 1}], success_url="http://localhost:3000/billing/success", cancel_url="http://localhost:3000/billing/cancel", metadata={"subject_id": user.subject_id}, client_reference_id=user.subject_id)

    def create_portal_session(self, subject_id: str, accept_language: str | None = None):
        subscription = self.subscriptions.get_by_subject(subject_id)
        if not subscription or not subscription.stripe_customer_id:
            raise HTTPException(status_code=400, detail=message('no_stripe_customer', accept_language))
        stripe.api_key = get_settings().stripe_api_key
        return stripe.billing_portal.Session.create(
            customer=subscription.stripe_customer_id,
            return_url="http://localhost:4321/dashboard",
        )

    def handle_subscription_event(self, event):
        obj = event["data"]["object"]
        if event["type"] == "checkout.session.completed":
            subject_id = obj.get("metadata", {}).get("subject_id")
            subscription_id = obj.get("subscription")
            if not subscription_id or not subject_id:
                return
            stripe.api_key = get_settings().stripe_api_key
            obj = stripe.Subscription.retrieve(subscription_id)
        else:
            customer_id = obj.get("customer")
            row = self.subscriptions.get_by_customer(customer_id) if customer_id else None
            if not row:
                return
            subject_id, subscription_id = row.subject_id, obj.get("id")
        status = obj.get("status", "canceled")
        active = status in {"active", "trialing"} and event["type"] != "customer.subscription.deleted"
        price_id = ((obj.get("items", {}).get("data") or [{}])[0].get("price", {}) or {}).get("id")
        plan = next((p for p in self.plans.list_active() if p.stripe_price_id == price_id), None) if active else self.plans.get("plan-free")
        if not plan:
            return
        self.subscriptions.save(subject_id, obj.get("customer"), subscription_id, status, plan.tier_id)
        self.keycloak.set_plan(subject_id, plan.keycloak_role)
