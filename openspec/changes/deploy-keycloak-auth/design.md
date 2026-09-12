## Context

See proposal.md - Why. This is a greenfield repo: no existing Keycloak instance, no existing realm. This change only stands up identity infrastructure and its contract (realm, roles, clients) — no backend or speech-app code consumes it yet; those are later changes (`add-dashboard-backend-base`, `add-speech-app-cloud-mode`).

## Goals / Non-Goals

**Goals:**
- A reproducible local Keycloak instance (Docker Compose) any developer can bring up from a clean checkout.
- A realm export checked into the repo as the source of truth, so realm config isn't only "whatever is in someone's admin console."
- The two client contracts (confidential backend client, public device-flow client) and the plan-role convention, stable enough for later changes to build against without renegotiating names.

**Non-Goals:**
- Production Keycloak hosting/HA setup (documented as a follow-up path, not built here).
- Defining the actual pricing tiers or word-limit values — that's `add-plans-billing`. This change only defines the `plan-*` role naming convention and the mechanism, with `plan-free`/`plan-pro` as placeholder roles to prove the pattern.
- Any dashboard backend or speech-app code changes.
- User self-registration flows, email verification, password policies — default Keycloak behavior is accepted as-is for now.

## Decisions

**Docker Compose for local dev, with Postgres from the start.** Keycloak's embedded dev database (H2) is explicitly not for anything persistent. Since this repo already standardizes on Postgres for the dashboard backend, the Compose file runs Keycloak against its own Postgres database/schema from day one, so the local setup matches the shape a real deployment would take (swap the Compose Postgres service for a managed one later — no data-store migration needed).

**Realm export as source of truth, not admin-console clicks.** Keycloak supports exporting/importing realm JSON. Committing this export and importing it on container start (`--import-realm`) means the realm, roles, and clients are defined in version control and code review, not tribal knowledge in someone's browser session. Alternative considered: Terraform (`keycloak` provider) for full GitOps management — rejected for this change as more infra than a single realm needs right now; the exported-JSON approach is the smaller step and can be replaced by Terraform later without changing the realm's shape.

**Plan as a realm role, not a custom user attribute.** Roles are natively included in token claims via standard mappers, natively assignable/removable via the admin API (which `add-plans-billing`'s Stripe webhook handler will call), and natively enforceable in Keycloak-aware middleware. A custom attribute would require a custom mapper anyway and gains nothing. Naming convention `plan-<tier>` (not `role-<tier>` or bare tier names) keeps plan roles visually distinct from any future non-plan roles (e.g. `admin`) in the realm.

**Two separate OAuth2 clients, not one.** The backend needs a confidential client (can hold a secret, validates tokens server-side). The desktop app cannot hold a secret safely and needs Device Authorization Grant, which requires a public client. Mixing these into one client would force the more permissive/less secure configuration on both consumers.

## Risks / Trade-offs

- [Realm export drifts from what's actually running if someone changes config by hand in the admin console] → Document and enforce (via PR review) that realm changes are made by editing the export JSON and reimporting, not by clicking in the console.
- [Local Docker Compose setup diverges from eventual production Keycloak hosting] → Keep the realm export and role/client contracts hosting-agnostic; only the Compose file itself is dev-specific, so switching hosting later doesn't touch the realm definition.
- [`plan-free`/`plan-pro` placeholder roles get treated as final by a later change] → proposal.md and this design explicitly flag them as placeholders for `add-plans-billing` to finalize; tasks.md will note this.

## Migration Plan

Greenfield addition, nothing to migrate. Rollback is `docker compose down -v` against the Keycloak service — no other system depends on this yet.
