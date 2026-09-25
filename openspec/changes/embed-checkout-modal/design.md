# Design

## Context

Today, `frontend/src/pages/dashboard/index.astro` renders a plain `<form method="post" action={appPath('dashboard/checkout')}>` with a plan `<select>` and an "Upgrade" button. Submitting it is a full-page POST to `frontend/src/pages/dashboard/checkout.ts`, which calls `POST {backend}/billing/checkout` and does `redirect((await response.json()).url)` — a server-side 302 straight to `checkout.stripe.com`.

On the backend, `BillingService.create_checkout_session` (`backend/app/services/billing.py`) calls `stripe.checkout.Session.create(mode="subscription", line_items=[...], success_url=..., cancel_url=..., metadata={"subject_id": ...}, client_reference_id=...)` and the controller (`backend/app/controllers/billing.py`) returns `{"url": session.url}`.

Subscription state is reconciled purely by webhook: `/billing/webhook` verifies the Stripe signature and calls `BillingService.handle_subscription_event`, which for `checkout.session.completed` retrieves the full `Subscription` object and, for other subscription lifecycle events, looks up the local row by `customer` id. This reconciliation is independent of how the Checkout Session was rendered (hosted page vs. embedded) — it only depends on the Session/Subscription objects Stripe emits, which are the same in both modes.

There is currently no Stripe.js on the frontend at all (only `stripe-python` on the backend), and no publishable key is exposed to the browser — only `STRIPE_API_KEY` (secret) exists in `.env`.

See `proposal.md` for why this is changing; see `specs/billing/embedded-checkout-modal/spec.md` for the exact required behavior.

## Goals / Non-Goals

**Goals:**
- Keep the user on `agents-dev.hugosantiago.dev/speech-dashboard` for the entire upgrade flow.
- Reuse the existing webhook-based reconciliation (`checkout.session.completed` → `handle_subscription_event`) unchanged.
- Minimize new surface area: no new payment-state machine, no hand-rolled PaymentIntent confirmation, no card-field validation code to maintain.

**Non-Goals:**
- Replacing Stripe Checkout with raw Stripe Elements/Payment Element (that would require building a price/subscription-creation flow by hand and expanding the webhook handler's responsibilities — out of scope for a UX-only change).
- Changing the plan catalog, pricing, or subscription lifecycle rules.
- Building a general-purpose modal component system; a minimal, single-purpose modal for this one flow is sufficient.

## Decisions

### Use Stripe Checkout in embedded mode (`ui_mode="embedded"`), not Payment Element / PaymentIntent
Stripe offers two ways to keep checkout on-site:
1. **Embedded Checkout** (`ui_mode="embedded"` on the existing `checkout.Session.create` call) — Stripe still owns the Session object and its lifecycle; the frontend mounts Stripe's own checkout UI (fields, validation, 3DS, wallets) into a container via `@stripe/stripe-js`'s `initEmbeddedCheckout({ clientSecret })`. The webhook (`checkout.session.completed`) fires exactly as it does today.
2. **Payment Element on a raw PaymentIntent/SetupIntent** — the backend would create and manage a Subscription (or PaymentIntent) directly, hand a `client_secret` to `stripe.confirmPayment`, and the webhook handler would need new logic to react to `payment_intent.succeeded` and tie it back to a subscription/plan, duplicating what Checkout Sessions already do.

Chosen: **(1) Embedded Checkout**. It changes only `ui_mode` and the response shape (`url` → `client_secret`) on the backend, and lets the existing webhook handler stay untouched — the lowest-risk way to satisfy "modal, not redirect."

Alternative considered and rejected: an `<iframe src={hostedUrl}>` wrapping the existing hosted Checkout page. Rejected because Stripe's hosted Checkout page sets `X-Frame-Options`/`frame-ancestors` to prevent exactly this kind of embedding — it will not render in an iframe.

### `return_url` instead of `success_url`/`cancel_url`
Embedded mode does not use `success_url`/`cancel_url`; it uses a single `return_url` (required by Stripe if the payment method requires an off-site redirect step, e.g. some bank redirects or 3DS flows) and an `onComplete` client-side callback for the common case where no redirect is needed. Set `return_url` to the dashboard URL itself (`{DASHBOARD_URL}/dashboard`) so that even the rare redirect-required path lands the user back on the dashboard rather than a dead page.

### New frontend dependency and config
- Add `@stripe/stripe-js` to `frontend/package.json`.
- Add `PUBLIC_STRIPE_PUBLISHABLE_KEY` (Stripe's publishable key, safe for the browser) to `.env` and pass it through in `docker-compose.dev.yml` the same way other `PUBLIC_*` vars are passed to the frontend service — this project has already been bitten twice (Keycloak's `KC_HTTP_RELATIVE_PATH` and `KC_HOSTNAME`) by an env var existing in `.env` but not being wired into the container's `environment:` block; tasks.md must call this out explicitly so it isn't missed a third time.

### Modal implementation
The "Upgrade" `<form>` becomes a `<button type="button">` that opens a modal (plain `<dialog>` element or an equivalent minimal markup + CSS already consistent with this codebase's terse inline-style conventions — no new UI framework). On open, it does `POST {appPath('dashboard/checkout')}` via `fetch` (not a navigating form submit) with the chosen `plan_id`, receives `{ client_secret }`, and calls `stripe.initEmbeddedCheckout({ clientSecret })` then `.mount(...)` into the modal's container. `frontend/src/pages/dashboard/checkout.ts` changes from `redirect(...)` to returning `{ client_secret }` as JSON (still going through `authenticatedFetch`/`AuthRefreshError` handling exactly as it does today).

On `onComplete`, the modal shows a brief success state, unmounts the embedded checkout, closes, and reloads the dashboard data (a client-side re-fetch or `location.reload()` — simplest is acceptable here) so the upgraded plan/usage reflects once the webhook has updated the subscription row. Because webhook delivery is asynchronous, the plan may not be updated the instant the modal closes; this is the same eventual-consistency window that already exists today with the redirect-based flow (the user currently lands back on `success_url` before the webhook necessarily finishes too), so it's not a regression.

## Risks / Trade-offs

- **[Risk]** Webhook delivery lag means the dashboard may briefly still show the old plan right after the modal closes. → **Mitigation**: none required beyond what exists today (same behavior as the current redirect flow); optionally note this as a follow-up UX polish (e.g. a "processing…" state), not required for this change.
- **[Risk]** `PUBLIC_STRIPE_PUBLISHABLE_KEY` must reach the frontend container correctly, following the same env-passthrough pattern this project has repeatedly missed. → **Mitigation**: tasks.md includes an explicit step to verify the var is both in `.env` and in `docker-compose.dev.yml`'s frontend `environment:` block, and to restart/verify via `docker inspect`/`docker exec ... env` the way prior fixes in this project were verified.
- **[Risk]** Embedded Checkout requires a Stripe API version and account configuration that supports `ui_mode="embedded"`. → **Mitigation**: `stripe-python` is already pinned to `>=12,<14`, which supports embedded mode; verify against the test-mode account already in use (`acct_1E5jBaEPRLYLqFCl`) during implementation with a real test checkout, the same way the Stripe key itself was smoke-tested earlier in this project.
- **[Trade-off]** Losing the hosted page's own domain/TLS "this is really Stripe" trust signal for users who look at the URL bar. Accepted: the embedded UI is still rendered and served by Stripe.js from Stripe's own iframe internally, which is Stripe's supported, PCI-compliant pattern for this exact use case.

## Migration Plan

1. Backend: switch `create_checkout_session` to `ui_mode="embedded"` + `return_url`, return `client_secret` from the controller instead of `url`.
2. Frontend: add `@stripe/stripe-js`, wire `PUBLIC_STRIPE_PUBLISHABLE_KEY`, replace the upgrade `<form>` with a modal trigger + embedded checkout mount, update `checkout.ts` to return JSON instead of redirecting.
3. Manual verification: log in as the `tester` user, open the upgrade modal, complete a test-mode payment with a Stripe test card, confirm the modal shows success and the dashboard reflects the new plan after the webhook fires; verify closing the modal without paying leaves the plan unchanged.
4. No feature flag or gradual rollout needed — this is a dev-mode-only dashboard behind Keycloak auth with a small user base; a straightforward cutover is acceptable. Rollback is reverting the two changed files/config if issues surface.
