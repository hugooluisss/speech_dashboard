from fastapi import APIRouter, Depends, Header, HTTPException

from app.auth import Claims, validate_token
from app.db import session_factory
from app.repositories.plans import PlanRepository
from app.repositories.usage import UsageRepository
from app.repositories.users import UserRepository
from app.repositories.subscriptions import SubscriptionRepository
from app.services.usage import UsageService
from app.messages import locale, message

router = APIRouter(prefix="/admin")


@router.get("/users")
def users(claims: Claims = Depends(validate_token), accept_language: str | None = Header(None, alias='Accept-Language')):
    if not claims.admin:
        raise HTTPException(status_code=403, detail=message('admin_role_required', accept_language))
    with session_factory()() as session:
        plans = PlanRepository(session)
        usage = UsageService(UsageRepository(session))
        subscriptions = SubscriptionRepository(session)
        rows = []
        for user in UserRepository(session).list_all():
            subscription = subscriptions.get_by_subject(user.subject_id)
            plan = plans.get(subscription.plan_tier_id if subscription else "plan-free")
            current = usage.get_usage(user.subject_id, plan) if plan else {"used": 0, "period": usage.current_period()}
            rows.append({"subject_id": user.subject_id, "plan": getattr(plan, f"name_{locale(accept_language)}") if plan else "Unknown", "usage": current["used"], "period": current["period"]})
        return rows
