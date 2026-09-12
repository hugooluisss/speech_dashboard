## Why

Every downstream capability — billing, usage/quota tracking, the cloud transcription endpoint, and the dashboard UI — needs a running backend that already knows how to authenticate a request against Keycloak, read the caller's plan from the token, and persist data in Postgres through a consistent layering. Without this foundation first, each later change would reinvent auth plumbing and data access instead of building on one contract. `deploy-keycloak-auth` already defines the realm, the `plan-*` role convention, and the confidential backend client this change consumes.

## What Changes

- Scaffold a Python backend service (FastAPI) in `speech_dashboard/backend/` structured as `controllers -> services -> repositories`:
  - Repositories: the only layer with direct data access (Postgres).
  - Services: business rules, orchestration; no direct DB access, no HTTP concerns.
  - Controllers: HTTP request/response handling (FastAPI routers), delegate to services only.
- Add Postgres connectivity, a migration tool, and a base schema for a `users` table (mirrors Keycloak subject id + cached plan role — the source of truth for the role stays Keycloak; this table exists so later changes have a place to attach usage/billing data keyed by user without re-deriving it from a token every time).
- Add Keycloak token validation middleware/dependency: verifies the access token's signature against the realm's confidential client, extracts the subject (user id) and the `plan-*` claim, and rejects unauthenticated/invalid requests.
- Add a minimal authenticated `/me` endpoint (controller -> service -> repository, end to end) returning the caller's user id and current plan, to prove the full stack works together.
- Add project tooling: dependency management, test runner setup, and a health-check endpoint (`/health`) with no auth required.

## Capabilities

### New Capabilities
- `backend/service-foundation`: The backend's layered structure (controllers/services/repositories), Postgres connectivity, and the `/health` endpoint as a base every later backend capability builds on.
- `backend/keycloak-token-auth`: Validating Keycloak-issued access tokens on incoming requests and exposing the authenticated user's id and plan to request handlers.

### Modified Capabilities
(none — no existing specs beyond `auth/keycloak-realm`, which this change consumes but does not modify)

## Impact

- New: `speech_dashboard/backend/` (FastAPI app, `controllers/`, `services/`, `repositories/`, migrations, tests).
- Depends on `deploy-keycloak-auth`'s confidential client credentials and realm metadata (issuer URL, JWKS endpoint) being available as configuration/environment variables.
- Establishes the `users` table shape and the authenticated-request pattern that `add-plans-billing`, `add-usage-quota-tracking`, and `add-cloud-transcription-api` will all extend.
