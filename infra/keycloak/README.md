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
- Plan roles: exactly one `plan-*` realm role per user; initial placeholders are `plan-free` and `plan-pro`. This is a **directly-assigned realm role, not a Keycloak realm "default role."** Whichever system provisions a user (currently: manual admin API calls; later: `add-plans-billing`'s webhook handler) must assign `plan-free` explicitly at creation and swap it explicitly on plan changes. Do not add plan roles to the realm's `defaultRoles`/`default-roles-speech` composite — a role granted that way is inherited by every user and cannot be removed per-user, which breaks the "exactly one plan-* role, swappable" contract (confirmed by testing: with `plan-free` in `defaultRoles`, every token showed both `plan-free` and the user's real plan, and removing the direct role mapping had no effect since the composite still granted it).
- Access-token claim: `plan`, containing the user's realm role(s) plus Keycloak's own built-in composite roles (`offline_access`, `uma_authorization`, `default-roles-speech`) since the mapper reads all effective realm roles. Callers must select the role that starts with `plan-` from this list, not assume it is the only entry. If non-plan realm roles are added later, the mapper must be narrowed before they are exposed through this contract.
- The access token also carries an explicit `sub` claim (subject id) via a dedicated protocol mapper on the `plan-roles` client scope. This is required because Keycloak 26's access tokens omit standard OIDC claims like `sub` by default (they only appear in the ID token unless a client scope mapper forces them into the access token) — confirmed by testing against a real token from this realm.

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
flow), the resulting access token was confirmed to carry a `sub` claim and a
`plan` claim containing exactly one `plan-*` role, and a real backend `/me`
call (from `add-dashboard-backend-base`) against that token succeeded. Two
defects surfaced only by this real end-to-end run (not caught by the
narrower per-task checks) were found and fixed in the committed realm
export:

1. Both clients' `defaultClientScopes` originally listed only the custom
   `plan-roles` scope, replacing rather than extending Keycloak's built-in
   default scopes. Fixed by including the standard scopes (`profile`,
   `roles`, `email`, `web-origins`, `acr`, `basic`) alongside `plan-roles`.
2. Keycloak 26's access tokens omit the standard `sub` claim by default
   (it only appears in the ID token) unless a mapper explicitly forces it
   in. Fixed by adding an explicit `oidc-sub-mapper` to the `plan-roles`
   client scope.
3. `plan-free` was originally a realm `defaultRole`, which composites it
   into `default-roles-speech` and grants it to every user permanently —
   it cannot be removed per-user, so every token showed both `plan-free`
   and the user's real plan simultaneously. Fixed by removing it from
   `defaultRoles`; `plan-free` must now be assigned as a direct,
   swappable role mapping by whatever provisions the user (see the
   Contract section above).

Test users were deleted and the stack torn down (`docker compose down -v`)
after verification, so the committed realm export is the only persisted
state.
