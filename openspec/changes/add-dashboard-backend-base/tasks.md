## 1. Project scaffolding

- [x] 1.1 Initialize the FastAPI project in `backend/` (dependency management, entrypoint, `.env.example`); verify `uvicorn app.main:app` starts without error.
- [x] 1.2 Create the `controllers/`, `services/`, `repositories/` package structure with a short README noting the one-directional dependency rule (controllers -> services -> repositories); verify the packages exist and import cleanly with no circular imports.
- [x] 1.3 Add the test runner setup (pytest) and a trivial smoke test; verify `pytest` runs and passes.

## 2. Postgres and migrations

- [x] 2.1 Add SQLAlchemy + Alembic, configure the database connection from environment variables; verify Alembic can connect to a local Postgres instance and run `alembic upgrade head` with zero migrations.
- [x] 2.2 Add the `users` table migration (Keycloak subject id as primary/unique key, created-at timestamp); verify the migration applies cleanly and the table appears in `\dt`.
- [x] 2.3 Implement the `UserRepository` (get-by-subject-id, create) in `repositories/`; verify unit tests cover both create and idempotent lookup.

## 3. Health check

- [x] 3.1 Implement the `/health` controller with no auth required; verify `curl /health` returns a success response with the server running and no database dependency required for this specific check.

## 4. Keycloak token validation

- [x] 4.1 Add configuration for the realm issuer URL and confidential client id (from `deploy-keycloak-auth`'s documented contract); verify the app fails fast at startup with a clear error if these are missing.
- [x] 4.2 Implement JWKS fetching and caching, and a token-validation dependency that verifies signature, issuer, and expiry; verify unit tests cover a valid token, an expired token, and a token with a bad signature.
- [x] 4.3 Implement claim extraction (subject id, `plan-*` role) from a validated token; verify a unit test decodes a sample token fixture and returns the expected subject id and plan.
- [x] 4.4 Wire the token-validation dependency into FastAPI so protected routes reject missing/invalid tokens before reaching controller logic; verify an integration test hits a protected route with no token and gets an auth error, and with a valid token fixture and gets through.

## 5. End-to-end `/me` endpoint

- [x] 5.1 Implement `UserService.get_or_create(subject_id, plan)` calling `UserRepository`; verify a unit test confirms it creates on first call and reuses on subsequent calls for the same subject id.
- [x] 5.2 Implement the `/me` controller: validates the token, calls `UserService`, returns subject id and plan; verify an integration test against a real (test) Postgres database returns the expected JSON shape for a valid token.
- [x] 5.3 Document how to run the backend locally end-to-end against the `deploy-keycloak-auth` Docker Compose setup (obtain a test token, call `/me`) in `backend/README.md`; verify the documented steps work from a clean environment.
