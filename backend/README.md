# Speech Dashboard Backend

FastAPI backend with one-way dependencies: `controllers -> services -> repositories`.
Controllers handle HTTP only, services hold business logic, and repositories are
the only layer allowed to access the database.

## Local end-to-end

Start the realm first, following [`infra/keycloak/README.md`](../infra/keycloak/README.md),
then start Postgres and configure the backend:

```sh
cd backend
cp .env.example .env
uv sync --dev
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

Obtain a token with the device client (the device endpoint, client ID, and
approval flow are documented in the Keycloak README), then call:

```sh
curl http://localhost:8000/health
curl -H "Authorization: Bearer $ACCESS_TOKEN" http://localhost:8000/me
```

The backend requires `DATABASE_URL`, `KEYCLOAK_ISSUER_URL`,
`KEYCLOAK_CLIENT_ID`, and `KEYCLOAK_CLIENT_SECRET` at startup. Missing values
fail startup with a validation error. Tests use a real PostgreSQL container:

```sh
DATABASE_URL=postgresql+psycopg://speech:speech@localhost:5433/speech \
KEYCLOAK_ISSUER_URL=http://localhost:8080/realms/speech \
KEYCLOAK_CLIENT_ID=speech-dashboard-backend \
KEYCLOAK_CLIENT_SECRET=dev-only-speech-dashboard-backend-secret \
uv run pytest -q
```
