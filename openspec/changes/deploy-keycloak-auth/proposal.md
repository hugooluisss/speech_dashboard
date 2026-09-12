## Why

Speech currently has no account system: the desktop app runs fully local with no login. The new platform (landing page + dashboard + cloud transcription + paid plans) requires knowing who a user is and what plan/role they have before any billing, quota, or cloud API work can start. Keycloak is the identity provider chosen for this, and its role model doubles as the plan model (a user's Keycloak role determines their word-quota plan). Every later change (backend base, billing, usage tracking, cloud transcription API, speech-app cloud mode, dashboard UI) needs a running, reachable Keycloak instance with a defined realm/role shape to build against — this change delivers that foundation first.

## What Changes

- Stand up a self-hosted Keycloak instance (Docker Compose) for local development, with a documented path to a persistent deployment (external Postgres-backed, not the embedded dev database).
- Create a dedicated Keycloak realm for the Speech platform (not the `master` realm).
- Define a `plan-*` realm role per pricing tier (initial set: `plan-free`, `plan-pro`; exact tiers/limits are decided in the billing change, this change only establishes the role naming convention and realm-role mechanism as the source of truth for "which plan is this user on").
- Register two Keycloak clients:
  - A confidential client for the dashboard backend (FastAPI) to validate tokens and read role claims.
  - A public client configured for OAuth2 Device Authorization Grant, for the speech-app desktop app to authenticate headless/CLI-style.
- Configure realm token settings so a user's `plan-*` role is emitted as a claim in the access token (via a client scope/mapper), so the backend can read the plan without a separate lookup.
- Document realm export/import so the realm configuration is reproducible (not just clicked together once in the admin console).

## Capabilities

### New Capabilities
- `auth/keycloak-realm`: Deployment and realm/role/client configuration for the Speech identity provider, including the plan-role convention and the two OAuth2 clients (confidential backend client, public device-flow client).

### Modified Capabilities
(none — greenfield repo, no existing specs)

## Impact

- New: `speech_dashboard/infra/keycloak/` (or similar) — Docker Compose file, realm export JSON, setup docs.
- No application code changes yet (backend base, speech-app changes are separate changes that will consume this realm's clients/roles).
- Establishes the `plan-*` role naming convention that `add-plans-billing` and `add-usage-quota-tracking` will depend on.
- Establishes the two OAuth2 client contracts (confidential + device-flow public) that `add-dashboard-backend-base` and `add-speech-app-cloud-mode` will depend on.
