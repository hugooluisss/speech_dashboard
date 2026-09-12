# Local Keycloak

This directory runs a local Keycloak `speech` realm backed by its own Postgres database. The committed file `realm-export/speech-realm.json` is the source of truth; do not rely on manual admin-console changes.

## Start

```sh
cd infra/keycloak
cp .env.example .env
# Change both passwords in .env.
docker compose up -d
```

Keycloak is available at <http://localhost:8080>; sign in to the admin console with the bootstrap credentials from `.env`. The `speech` realm is imported automatically. Postgres is internal to Compose and is not exposed on a host port.

To reset the local instance and re-import the committed realm:

```sh
docker compose down -v
docker compose up -d
```

The Compose file pins Keycloak to `26.3.3` and Postgres to `16-alpine`. The design did not specify token lifetimes, so this initial baseline uses a 5-minute access token, a 30-minute idle SSO session, and a 10-hour maximum SSO session. Change those values in the export only when the contract is intentionally revised.

## Contract for downstream changes

- Realm: `speech` (never `master`)
- Backend client ID: `speech-dashboard-backend`
- Backend client type: confidential; development secret in the export is `dev-only-speech-dashboard-backend-secret` and must be replaced outside local development.
- Desktop client ID: `speech-desktop-device`
- Desktop client type: public; OAuth2 Device Authorization Grant enabled; no client secret.
- Plan roles: exactly one `plan-*` realm role per user; initial placeholders are `plan-free` and `plan-pro`. New users receive `plan-free` by default.
- Access-token claim: `plan`, containing the user's realm role(s). At present the realm defines only `plan-*` roles, so the claim contains the user's plan role. If non-plan realm roles are added later, the mapper must be narrowed before they are exposed through this contract.

The device endpoint is:

```text
POST http://localhost:8080/realms/speech/protocol/openid-connect/auth/device
```

Use the public client ID above and no secret. The backend can use its confidential client credentials at:

```text
POST http://localhost:8080/realms/speech/protocol/openid-connect/token
```

Realm changes should be made in `realm-export/speech-realm.json`, followed by a volume reset so the import is applied to a fresh local database.

## Verification status

All tasks (1.1 through 4.1) have been verified against a clean local volume,
including the end-to-end device-code flow: a device code was requested with
`speech-desktop-device`, approved as a test user via direct HTTP calls to the
login/consent endpoints (no browser UI, but the real Keycloak login+consent
flow), and the resulting access token was confirmed to carry the `plan` claim
with the user's `plan-free` role. The test user was deleted and the stack torn
down (`docker compose down -v`) afterward, so the committed realm export is
the only persisted state.
