from fastapi import APIRouter, Depends, Header, HTTPException

from app.auth import Claims, validate_token
from app.db import session_factory
from app.repositories.plans import PlanRepository
from app.repositories.usage import UsageRepository
from app.services.usage import UsageService
from app.messages import message

router = APIRouter()


@router.get("/usage")
def usage(claims: Claims = Depends(validate_token), accept_language: str | None = Header(None, alias='Accept-Language')) -> dict[str, int | str]:
    with session_factory()() as session:
        plan = PlanRepository(session).get(claims.plan)
        if not plan:
            raise HTTPException(status_code=404, detail=message('plan_not_found', accept_language))
        return UsageService(UsageRepository(session)).get_usage(claims.subject_id, plan)
