from fastapi import APIRouter, Depends

from app.auth import Claims, validate_token
from app.db import session_factory
from app.repositories.plans import PlanRepository
from app.services.plans import PlanService

router = APIRouter()


@router.get("/plans")
def plans(_: Claims = Depends(validate_token)) -> list[dict]:
    with session_factory()() as session:
        entries = PlanService(PlanRepository(session)).list_active()
    return [{"tier_id": p.tier_id, "display_name": p.display_name, "keycloak_role": p.keycloak_role,
             "stripe_price_id": p.stripe_price_id, "word_limit": p.word_limit, "period_unit": p.period_unit}
            for p in entries]
