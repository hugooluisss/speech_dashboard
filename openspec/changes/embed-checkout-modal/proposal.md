# Proposal

## Why

Upgrading a plan currently sends the user away to a hosted `checkout.stripe.com` page, leaving the dashboard entirely. The user wants payment to happen inside the dashboard, in a modal, so the experience stays on-site end to end.

## What Changes

- The `/dashboard/checkout` action no longer returns a Stripe-hosted URL to redirect to. Instead, the backend creates a Stripe Checkout Session in **embedded mode** (`ui_mode="embedded"`) and returns its `client_secret`.
- The "Upgrade" control on the dashboard opens an in-page modal instead of submitting a form that navigates away. Stripe.js (`@stripe/stripe-js`) is loaded on the frontend for the first time and used to mount Stripe's Embedded Checkout UI inside that modal via the returned `client_secret`.
- After the embedded checkout reports completion (Stripe's `onComplete` callback / return to a same-page `return_url`), the modal closes and the dashboard refreshes plan/usage state. The existing `checkout.session.completed` webhook keeps assigning the Keycloak plan role — no change to that reconciliation logic, since the session object and its webhook event are unchanged in shape, only `ui_mode` changes.
- **BREAKING**: the `/billing/checkout` backend response shape changes from `{"url": "https://checkout.stripe.com/..."}` to `{"client_secret": "..."}`. Any caller expecting a hosted redirect URL must be updated (only caller today is `frontend/src/pages/dashboard/checkout.ts`).

## Capabilities

### New Capabilities
- `billing/embedded-checkout-modal`: on-site checkout — creating a Checkout Session that returns a client secret instead of a hosted URL, and the modal UX that mounts Stripe's embedded checkout, handles completion/cancel/error, and refreshes dashboard state afterward.

### Modified Capabilities
- None. `billing/stripe-subscription-sync` (proposed in the still-unarchived `add-plans-billing` change, 14/16 tasks done, not yet in `openspec/specs/`) describes checkout as returning a hosted URL. That requirement isn't part of the archived source of truth yet, so there is nothing to file a delta against; this change's new capability spec below states the intended final behavior directly. Once `add-plans-billing` is archived, its "Checkout session creation" scenario should be reconciled with this capability (see Impact).

## Impact

- Backend: `backend/app/services/billing.py` (`create_checkout_session`), `backend/app/controllers/billing.py` (`/billing/checkout` response shape).
- Frontend: `frontend/src/pages/dashboard/checkout.ts` (returns `client_secret` instead of redirecting), `frontend/src/pages/dashboard/index.astro` (upgrade control becomes a modal trigger instead of a form POST that navigates), new frontend dependency `@stripe/stripe-js`, and a `PUBLIC_STRIPE_PUBLISHABLE_KEY` env var the frontend needs to load Stripe.js (currently only the secret key exists in `.env`).
- No change to the `/billing/webhook` handler, `SubscriptionRepository`, or Keycloak role sync — the Checkout Session's webhook event shape is the same in embedded mode.
- Process note: `add-plans-billing`'s pending "Checkout session creation" scenario (hosted URL) will be superseded by this capability once both changes are archived — whoever archives should reconcile the two rather than keep both descriptions.
