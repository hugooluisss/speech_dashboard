from fastapi import APIRouter, Depends

from app.auth import Claims, validate_token
from app.db import session_factory
from app.repositories.users import UserRepository
from app.services.users import UserService

router = APIRouter()


@router.get("/me")
def me(claims: Claims = Depends(validate_token)) -> dict[str, str]:
    with session_factory()() as session:
        UserService(UserRepository(session)).get_or_create(claims.subject_id, claims.plan)
    return {"subject_id": claims.subject_id, "plan": claims.plan}
