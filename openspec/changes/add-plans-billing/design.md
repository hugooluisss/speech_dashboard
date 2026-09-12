## Context

See proposal.md - Why. This change builds on `add-dashboard-backend-base` (layered backend, Postgres, authenticated requests, `users` table) and on `deploy-keycloak-auth` (the `plan-*` role convention and confidential client). Neither prior change defines pricing or a Keycloak admin-API integration; both are added here.

## Goals / Non-Goals

**Goals:**
- Stripe Checkout (not a custom card-entry form) for payment, since building PCI-scoped payment UI ourselves is unnecessary work for what a hosted Checkout page already solves.
- A single source of truth for "what plans exist and what they cost" (the `plans` table), so the dashboard UI, the checkout endpoint, and (later) usage-quota enforcement all read the same catalog instead of hard-coding tier names/limits in multiple places.
- Webhook-driven role sync, so Keycloak's `plan-*` role always reflects Stripe's current subscription state without a human manually flipping roles.

**Non-Goals:**
- Proration, plan-switching UX polish, invoicing/tax handling beyond what Stripe Checkout and Billing provide out of the box — accepted as Stripe defaults for now.
- Usage-based/metered billing (charging based on words used) — the proposal's model is fixed-price tiers with a word cap per period; metered billing is not requested and would be a separate future change if pricing changes.
- Multi-seat/team billing — out of scope; one user maps to one plan.
- Actual tier names, prices, and word-limit numbers — these are business decisions made by seeding the `plans` table with real data at deploy time, not hard-coded in this design.

## Decisions

**Stripe Checkout + Billing (subscriptions), not one-off Payment Intents.** Plans are recurring (word quota per period), so Stripe Subscriptions is the natural fit — it already handles renewal, retries on failed payment, and emits the lifecycle webhooks this change consumes. Alternative considered: charging manually per period via Payment Intents — rejected, reinvents what Stripe Billing already does correctly.

**`plans` table is a local cache of Stripe's pricing, keyed by our own tier identifier.** The Stripe Price ID is a foreign reference, not the primary key, so the catalog can be listed and reasoned about (e.g. by `add-usage-quota-tracking`) without calling Stripe. Seeding/updating this table when prices change in the Stripe dashboard is a manual admin step for now (documented in tasks), not built as a two-way sync — that's more infrastructure than a small number of fixed tiers needs.

**Role sync happens only from Stripe webhooks, never from the checkout-session-creation endpoint.** The checkout endpoint only starts a Stripe session; it must not optimistically grant the role before payment is confirmed. This avoids a user getting `plan-pro` access for a checkout session they abandon or that fails.

**Webhook handler resolves the user via the stored Stripe customer id, falling back to Checkout Session metadata on first purchase.** When starting checkout, the session is created with the user's subject id attached as metadata; the first `checkout.session.completed` event uses that metadata to link the new Stripe customer id to the user record. Subsequent webhook events (subscription updated/cancelled) key off the now-stored customer id.

**Keycloak admin-API access via the existing confidential client's service account, not a separate admin client.** Keycloak lets a confidential client's service account be granted realm-management roles (e.g. `manage-users`). Reusing the existing backend client avoids managing a second secret. Alternative considered: a dedicated "admin" client used only for role management — rejected as unnecessary credential sprawl for one backend service that's already trusted.

## Risks / Trade-offs

- [Webhook delivery failure or backend downtime causes the Keycloak role to drift from actual Stripe subscription state] → Rely on Stripe's automatic webhook retries; document a manual reconciliation script (list subscriptions from Stripe, compare to Keycloak roles) as an operational runbook, not built as automation in this change.
- [Granting the confidential client `manage-users`-level permission increases the blast radius if that client's credentials leak] → Scope the granted realm-management role as narrowly as Keycloak allows (role management only, not full user management) and document this constraint in `deploy-keycloak-auth`'s realm export update.
- [`plans` table drifting from Stripe if someone changes a price in the Stripe dashboard without updating the local table] → Documented as a known manual step; a follow-up change could add a reconciliation job if this proves error-prone in practice.

## Migration Plan

Additive to `add-dashboard-backend-base`'s schema (new tables, no changes to `users` beyond adding Stripe linkage columns) and to `deploy-keycloak-auth`'s realm (a permission grant, not a client recreation). Rollback: revoke the confidential client's role-management permission and stop routing checkout/webhook traffic; no destructive schema changes to reverse.
