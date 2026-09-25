from fastapi import APIRouter, Depends

from app.auth import Claims, validate_token
from app.db import session_factory
from app.repositories.subscriptions import SubscriptionRepository
from app.repositories.users import UserRepository
from app.services.users import UserService

router = APIRouter()


@router.get("/me")
def me(claims: Claims = Depends(validate_token)) -> dict:
    with session_factory()() as session:
        UserService(UserRepository(session)).get_or_create(claims.subject_id, claims.plan)
        subscription = SubscriptionRepository(session).get_by_subject(claims.subject_id)
    has_stripe_customer = bool(subscription and subscription.stripe_customer_id)
    plan = subscription.plan_tier_id if subscription else claims.plan
    return {"subject_id": claims.subject_id, "plan": plan, "has_stripe_customer": has_stripe_customer}
