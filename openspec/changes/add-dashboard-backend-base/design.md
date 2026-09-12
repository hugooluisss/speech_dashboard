## Context

See proposal.md - Why. `deploy-keycloak-auth` (implemented separately) provides the realm, the `plan-*` role convention exposed as a token claim, and a confidential OAuth2 client for this backend to validate tokens against. This change builds the backend service that consumes that contract; it does not touch Keycloak configuration itself.

## Goals / Non-Goals

**Goals:**
- A backend skeleton whose layering (controllers/services/repositories) is enforced by directory/module structure, not just convention, so later changes have an obvious place to put new code.
- Token validation that works against the realm's published JWKS (no shared-secret hack), so it keeps working if Keycloak rotates signing keys.
- A real, working authenticated endpoint (`/me`) exercising the full stack, not just scaffolding with no runnable path.

**Non-Goals:**
- Plan/quota business logic (`add-usage-quota-tracking`), billing (`add-plans-billing`), or transcription (`add-cloud-transcription-api`) — this change only proves the foundation works.
- Admin-only endpoints or role-based authorization beyond reading the plan claim — no endpoint in this change restricts access by plan or role yet.
- Rate limiting, request logging/observability infrastructure — out of scope until a change needs it.

## Decisions

**FastAPI over other Python web frameworks.** Async-first (matters once the transcription endpoint streams audio), Pydantic-based request/response models give free validation and match the typed, layered style requested, and it's a natural fit for a Python backend that will eventually host or call into faster-whisper-based transcription (`add-cloud-transcription-api`). Alternative considered: Flask — rejected, no native async and weaker typing story for this size of project.

**Layering enforced via package structure.** `backend/app/controllers/`, `backend/app/services/`, `backend/app/repositories/` as separate Python packages, with a lint/review rule (not a runtime check) that controllers only import services, and services only import repositories. A runtime enforcement (e.g. import-linter) is left as a follow-up if the convention proves hard to keep by review alone — not built now, to avoid adding tooling before there's evidence it's needed.

**Token validation via JWKS, not a shared secret.** The backend fetches (and caches) the realm's public signing keys from its JWKS endpoint (from the realm's OpenID configuration, using the confidential client's issuer URL) and validates tokens locally. Alternative considered: token introspection (calling Keycloak on every request) — rejected as an unnecessary network round-trip per request when local JWT validation is sufficient and standard.

**SQL migrations via a dedicated tool (Alembic), not hand-run SQL.** Matches SQLAlchemy (the natural repository-layer ORM/toolkit for Postgres in this stack) and gives every later change a consistent way to evolve the schema (`add-plans-billing`'s plan table, `add-usage-quota-tracking`'s usage table) without ad hoc scripts.

**`users` table keyed by Keycloak subject id, plan not duplicated as source of truth.** The table exists so foreign keys (usage records, billing records) have something stable to point at; it does not try to be a second source of truth for the plan (Keycloak stays authoritative). The `/me` endpoint reads the plan from the token, not from this table, to avoid a caching-invalidation problem this change doesn't need to solve yet.

## Risks / Trade-offs

- [JWKS fetch fails or is slow if Keycloak is unreachable] → Cache fetched keys in memory with a reasonable TTL; document that the backend depends on Keycloak being reachable at least intermittently (no offline-token-validation fallback in this change).
- [Layering discipline (controllers never touching the DB) can erode over time without automated enforcement] → Called out explicitly in code review guidance in the backend README; automated enforcement is a documented follow-up, not silently assumed to happen on its own.
- [`users` table could drift from Keycloak if a user is deleted/renamed there] → Out of scope for this change; noted as a known gap for whichever later change needs user lifecycle sync (likely `add-plans-billing`, since Stripe webhooks will need to resolve users reliably).

## Migration Plan

Greenfield addition to a new repo — no existing backend to migrate from. First deploy is: run migrations to create the `users` table, then start the service. Rollback is deleting the service/database, since nothing else depends on it yet.
