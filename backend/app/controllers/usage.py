from fastapi import APIRouter, Depends, HTTPException

from app.auth import Claims, validate_token
from app.db import session_factory
from app.repositories.plans import PlanRepository
from app.repositories.usage import UsageRepository
from app.services.usage import UsageService

router = APIRouter()


@router.get("/usage")
def usage(claims: Claims = Depends(validate_token)) -> dict[str, int | str]:
    with session_factory()() as session:
        plan = PlanRepository(session).get(claims.plan)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        return UsageService(UsageRepository(session)).get_usage(claims.subject_id, plan)
