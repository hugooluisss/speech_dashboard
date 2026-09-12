## Why

A user who signs up needs somewhere to see their plan, how much of their word quota they've used, and manage billing — and the platform needs a minimal way to see how users/plans look in aggregate. Every backend piece for this already exists (`/me`, `/usage`, `/plans`, checkout); this change is the authenticated web UI in front of it, built on the Astro project `add-landing-page` already scaffolded.

## What Changes

- Add a new Keycloak client for the web dashboard using the Authorization Code flow with PKCE (browser-based login, unlike the backend's confidential client or speech-app's device-flow client), with redirect URIs for the Astro app.
- Add Astro server-rendered (non-static) routes under an authenticated area: a login redirect to Keycloak, a session cookie set on callback, and middleware that redirects unauthenticated visitors to login before reaching any protected route.
- Add a user dashboard page showing: current plan, word usage vs. limit for the current period (from `/me` and `/usage`), an upgrade/change-plan action (starts Stripe Checkout via the existing backend endpoint), and a "manage billing" action (opens Stripe's hosted customer portal).
- Add a small backend addition to `billing/stripe-subscription-sync`: an authenticated endpoint that creates a Stripe customer portal session for the caller, so "manage billing" has something to link to.
- Add an `admin` realm role and an admin-only dashboard page listing users with their current plan and usage (read-only visibility; it does not edit plan definitions — the plan catalog itself remains a manual backend/Stripe step per `add-plans-billing`'s design).
- Add a logout action that clears the session cookie and ends the Keycloak session.

## Capabilities

### New Capabilities
- `web/dashboard-app`: Authenticated session handling for the Astro app (login redirect, callback, session cookie, protected-route middleware, logout).
- `web/user-dashboard`: The signed-in user's own plan/usage/billing-management view.
- `web/admin-dashboard`: A read-only, admin-only view listing users with their current plan and usage.

### Modified Capabilities
- `auth/keycloak-realm`: Adds a browser-based (Authorization Code + PKCE) OAuth2 client for the Astro dashboard, and an `admin` realm role for gating the admin view.
- `billing/stripe-subscription-sync`: Adds an authenticated endpoint that creates a Stripe customer billing-portal session for the caller.

## Impact

- Extends `frontend/` (from `add-landing-page`) with authenticated, server-rendered routes alongside the existing static landing page.
- Extends the backend with one new billing-portal endpoint; no changes to existing endpoints' behavior.
- Depends on `add-dashboard-backend-base` (`/me`), `add-usage-quota-tracking` (`/usage`), `add-plans-billing` (`/plans`, checkout), and `deploy-keycloak-auth`'s realm (new client, new role).
- Introduces the platform's first admin-gated surface; the `admin` role is not assigned to anyone by this change — assigning it to a specific user is an operational step, not automated here.
