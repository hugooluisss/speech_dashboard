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
`KEYCLOAK_CLIENT_ID`, `KEYCLOAK_CLIENT_SECRET`, `STRIPE_API_KEY`, and
`STRIPE_WEBHOOK_SECRET` at startup. Missing values
fail startup with a validation error. Tests use a real PostgreSQL container:

```sh
DATABASE_URL=postgresql+psycopg://speech:speech@localhost:5433/speech \
KEYCLOAK_ISSUER_URL=http://localhost:8080/realms/speech \
KEYCLOAK_CLIENT_ID=speech-dashboard-backend \
KEYCLOAK_CLIENT_SECRET=dev-only-speech-dashboard-backend-secret \
uv run pytest -q
```

## Billing reconciliation runbook

If a paid user has the wrong Keycloak plan role:

1. In Stripe Dashboard test/live mode, open the customer and confirm the active subscription, status, and subscription item's Price ID.
2. Compare that Price ID with `plans.stripe_price_id` and confirm the corresponding `keycloak_role` is active.
3. In Keycloak Admin Console, open the Speech realm user by subject ID and inspect realm roles. Remove every stale `plan-*` role and assign exactly the catalog role (or `plan-free` for cancelled/inactive subscriptions).
4. Inspect backend logs and Stripe webhook delivery attempts; replay the relevant event after fixing configuration or connectivity.
5. Record the Stripe customer/subscription IDs and final Keycloak role, then verify a fresh access token contains exactly one `plan-*` role.

Manual Stripe test-mode verification is still pending: it requires a Stripe test secret key and webhook signing secret, a reachable backend webhook URL, and a Keycloak test user. Tasks 5.1 and 5.2 must be completed by running checkout/payment and cancellation in Stripe test mode and inspecting the user's roles in Keycloak; no real Stripe account was available for this implementation.
