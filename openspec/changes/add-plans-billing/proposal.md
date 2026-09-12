## Why

The platform's plan model (a Keycloak `plan-*` role determines a user's word-quota tier) needs a real source of truth for which tiers exist, what each costs, and how a user actually moves between them. Without billing, `plan-*` role assignment would have to be done by hand. This change makes Stripe the system a user actually pays through, and wires successful/changed/cancelled subscriptions to the user's `plan-*` role in Keycloak, so `add-usage-quota-tracking` (built after this) can trust the role as an accurate, currently-paid-for plan.

## What Changes

- Define a `plans` table in the backend (from `add-dashboard-backend-base`) as the local catalog of tiers: each row maps a Keycloak `plan-*` role to a Stripe Price ID, a display name, and its word-limit-per-period (the limit value itself is data here; enforcement logic is `add-usage-quota-tracking`'s concern).
- Add an authenticated endpoint to list available plans (for the dashboard UI to render pricing/upgrade options).
- Add an authenticated endpoint to start a Stripe Checkout session for a plan the user selects.
- Add a Stripe webhook endpoint that handles subscription lifecycle events (created/updated/cancelled) and, on each relevant event, reassigns the user's Keycloak `plan-*` role to match their current paid subscription (or back to `plan-free` on cancellation/payment failure past Stripe's own retry grace period).
- Extend the confidential Keycloak client (from `deploy-keycloak-auth`) with realm role-management permission, since the webhook handler needs to assign/remove a user's `plan-*` role via the Keycloak admin API.
- Persist minimal Stripe linkage per user (customer id, subscription id, subscription status) so the backend can reconcile state without querying Stripe on every request.

## Capabilities

### New Capabilities
- `billing/plan-catalog`: The set of purchasable plans (tier name, Keycloak role, Stripe price, word-limit-per-period value) and an endpoint to list them.
- `billing/stripe-subscription-sync`: Checkout session creation and webhook-driven synchronization between a user's Stripe subscription state and their Keycloak `plan-*` role.

### Modified Capabilities
- `auth/keycloak-realm`: The confidential backend client needs realm role-management permission (service-account role) so this change's webhook handler can assign/remove a user's `plan-*` role via the Keycloak admin API — the original change only had the client validate tokens, not manage roles.

## Impact

- New: `plans` and `subscriptions` tables (or a single `user_subscription` table) in the backend's Postgres database, new repositories/services/controllers under the existing layered structure.
- New: Stripe integration (SDK, webhook signature verification, API keys as configuration/secrets).
- Modifies the confidential Keycloak client's permissions (realm-management role) — a `deploy-keycloak-auth` follow-up, not a new client.
- `add-usage-quota-tracking` depends on the `plans` table's word-limit values and on the user's `plan-*` role being kept accurate by this change.
