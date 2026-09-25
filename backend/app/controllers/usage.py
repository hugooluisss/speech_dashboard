from fastapi import APIRouter, Depends, Header, HTTPException

from app.auth import Claims, validate_token
from app.db import session_factory
from app.repositories.plans import PlanRepository
from app.repositories.subscriptions import SubscriptionRepository
from app.repositories.usage import UsageRepository
from app.services.usage import UsageService
from app.messages import message

router = APIRouter()


@router.get("/usage")
def usage(claims: Claims = Depends(validate_token), accept_language: str | None = Header(None, alias='Accept-Language')) -> dict:
    with session_factory()() as session:
        plan = PlanRepository(session).get(claims.plan)
        if not plan:
            raise HTTPException(status_code=404, detail=message('plan_not_found', accept_language))
        result = UsageService(UsageRepository(session)).get_usage(claims.subject_id, plan)
        subscription = SubscriptionRepository(session).get_by_subject(claims.subject_id)
        result["current_period_end"] = subscription.current_period_end.isoformat() if subscription and subscription.current_period_end else None
        return result
