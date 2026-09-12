## 1. Local Keycloak infrastructure

- [x] 1.1 Add `infra/keycloak/docker-compose.yml` running Keycloak + a dedicated Postgres database/schema, with `--import-realm` enabled; verify `docker compose up` starts both containers healthy and Keycloak's admin console is reachable on localhost.
- [x] 1.2 Document local setup (env vars, admin bootstrap credentials via `.env.example`, ports, how to reset the volume) in `infra/keycloak/README.md`; verify a developer can follow it on a clean checkout with no prior context.

## 2. Realm, roles, and token claim

- [x] 2.1 Create the Speech realm (not `master`) with baseline settings (token lifetimes, no self-registration by default); verify the realm appears in the admin console after import.
- [x] 2.2 Create `plan-free` and `plan-pro` realm roles as placeholders for the plan convention; verify both roles exist via the admin REST API (`GET /admin/realms/speech/roles`).
- [x] 2.3 Add a client scope + protocol mapper that includes the user's `plan-*` realm role in the access token; verify by creating a test user with `plan-free`, obtaining a token via the direct-grant/password flow, decoding it, and confirming the plan claim is present.
- [x] 2.4 Export the realm configuration to a committed JSON file (`infra/keycloak/realm-export/speech-realm.json`) and wire it into the Compose file's import path; verify a fresh `docker compose up -v` (no prior volume) reproduces the same realm, roles, and clients from the export alone.

## 3. OAuth2 clients

- [x] 3.1 Create the confidential backend client (server-side, holds a secret, standard/service-account flows enabled as needed); verify a client-credentials or token-introspection call succeeds using its client ID/secret.
- [x] 3.2 Create the public device-flow client with OAuth2 Device Authorization Grant enabled and no client secret; verify a device-code request (`POST /realms/speech/protocol/openid-connect/auth/device`) returns a `device_code` and `user_code`.
- [x] 3.3 Verify end-to-end device flow manually: request device code → approve in browser as a test user → poll token endpoint → receive an access token containing the `plan-*` claim.
- [x] 3.4 Re-export the realm JSON after clients 3.1-3.3 are configured, so the committed export includes both clients; verify `git diff` shows the new clients in the export file.

## 4. Documentation handoff

- [x] 4.1 Document the two client IDs, the plan-role convention, and the token claim name in `infra/keycloak/README.md` (or a linked doc) as the contract for `add-dashboard-backend-base` and `add-speech-app-cloud-mode` to consume; verify the doc lists concrete client IDs and claim name, not placeholders.
