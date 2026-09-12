import stripe
from fastapi import APIRouter, Depends, HTTPException, Request

from app.auth import Claims, validate_token
from app.config import get_settings
from app.db import session_factory
from app.models import User
from app.repositories.plans import PlanRepository
from app.repositories.subscriptions import SubscriptionRepository
from app.services.billing import BillingService

router = APIRouter(prefix="/billing")


@router.post("/checkout")
def checkout(plan_id: str, claims: Claims = Depends(validate_token)):
    with session_factory()() as session:
        user = session.get(User, claims.subject_id) or User(subject_id=claims.subject_id)
        return {"url": BillingService(PlanRepository(session), SubscriptionRepository(session)).create_checkout_session(user, plan_id).url}


@router.post("/portal")
def portal(claims: Claims = Depends(validate_token)):
    with session_factory()() as session:
        url = BillingService(PlanRepository(session), SubscriptionRepository(session)).create_portal_session(claims.subject_id).url
    return {"url": url}


@router.post("/webhook")
async def webhook(request: Request):
    try:
        event = stripe.Webhook.construct_event(await request.body(), request.headers.get("stripe-signature", ""), get_settings().stripe_webhook_secret)
    except (ValueError, stripe.SignatureVerificationError) as exc:
        raise HTTPException(status_code=400, detail="Invalid webhook") from exc
    with session_factory()() as session:
        BillingService(PlanRepository(session), SubscriptionRepository(session)).handle_subscription_event(event)
    return {"received": True}
