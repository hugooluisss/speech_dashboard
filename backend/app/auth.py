from dataclasses import dataclass
from functools import lru_cache

import jwt
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

from app.config import get_settings

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class Claims:
    subject_id: str
    plan: str


@lru_cache
def jwks_client(issuer: str) -> PyJWKClient:
    return PyJWKClient(f"{issuer.rstrip('/')}/protocol/openid-connect/certs", cache_jwk_set=True, lifespan=300)


def extract_claims(payload: dict) -> Claims:
    subject_id = payload.get("sub")
    roles = payload.get("plan", [])
    roles = [roles] if isinstance(roles, str) else roles
    plan = next((role for role in roles if isinstance(role, str) and role.startswith("plan-")), None)
    if not subject_id or not plan:
        raise HTTPException(status_code=401, detail="Token is missing subject or plan")
    return Claims(subject_id=subject_id, plan=plan)


def validate_token(credentials: HTTPAuthorizationCredentials | None = Security(bearer)) -> Claims:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated", headers={"WWW-Authenticate": "Bearer"})
    settings = get_settings()
    try:
        key = jwks_client(settings.keycloak_issuer_url).get_signing_key_from_jwt(credentials.credentials).key
        payload = jwt.decode(credentials.credentials, key, algorithms=["RS256"], issuer=settings.keycloak_issuer_url, options={"verify_aud": False})
        return extract_claims(payload)
    except (jwt.PyJWTError, Exception) as exc:
        if isinstance(exc, HTTPException):
            raise
        raise HTTPException(status_code=401, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"}) from exc
