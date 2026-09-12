## 1. Keycloak permission grant

- [ ] 1.1 Grant the confidential backend client's service account realm role-management permission (e.g. `manage-users` or the narrowest equivalent Keycloak offers) in the Speech realm; verify via the admin console or admin API that the service account has the permission.
- [ ] 1.2 Re-export the realm JSON (from `deploy-keycloak-auth`'s realm-export file) including this permission change; verify `git diff` shows the updated service-account role mapping.

## 2. Plan catalog

- [ ] 2.1 Add the `plans` table migration (tier id, display name, Keycloak role, Stripe Price id nullable for free tier, word limit, period unit); verify the migration applies cleanly.
- [ ] 2.2 Seed the `plan-free` row with no Stripe Price id; verify a query returns it with a null/empty Stripe Price reference.
- [ ] 2.3 Implement `PlanRepository` and `PlanService` (list active plans); verify unit tests cover listing and the free-plan shape.
- [ ] 2.4 Implement the authenticated `/plans` controller; verify an integration test returns the seeded catalog for an authenticated request.

## 3. Stripe checkout

- [ ] 3.1 Add Stripe SDK and configuration (API key as a secret, not committed); verify the app fails fast at startup if the key is missing when billing endpoints are enabled.
- [ ] 3.2 Implement `BillingService.create_checkout_session(user, plan)`: validates the plan exists and is paid, creates a Stripe Checkout session with the user's subject id in session metadata; verify a unit test with a mocked Stripe client asserts metadata is set and an unknown plan id raises before calling Stripe.
- [ ] 3.3 Implement the authenticated `/billing/checkout` controller; verify an integration test (mocked Stripe) returns a checkout URL for a valid paid plan and an error for an invalid plan id.

## 4. Stripe webhook and role sync

- [ ] 4.1 Implement webhook signature verification using Stripe's webhook secret; verify a unit test rejects a request with an invalid/missing signature without invoking business logic.
- [ ] 4.2 Add a `user_subscriptions` (or equivalent) table/columns storing Stripe customer id and subscription status per user; verify the migration applies and a repository method can read/write it.
- [ ] 4.3 Implement `BillingService.handle_subscription_event(event)`: resolves the user (via stored customer id, or via checkout-session metadata on first purchase), determines the plan from the Stripe Price on the subscription, and calls the Keycloak admin API to remove the previous `plan-*` role and assign the new one; verify unit tests cover new-subscription-grants-role, plan-change-swaps-role, and cancellation-reverts-to-plan-free, all against a mocked Keycloak admin client.
- [ ] 4.4 Implement the `/billing/webhook` controller wired to the above; verify an integration test posts a signed sample Stripe event payload and confirms the resulting role-change call was made (mocked Keycloak admin client).
- [ ] 4.5 Document the manual reconciliation runbook (what to check in Stripe vs. Keycloak if a role appears out of sync) in `backend/README.md` or a linked ops doc; verify the doc lists concrete steps, not placeholders.

## 5. End-to-end verification

- [ ] 5.1 Manually verify end-to-end against Stripe's test mode: list plans, start checkout, complete a test payment, confirm the Keycloak role updates; verify by inspecting the user's roles via the Keycloak admin console after completing test checkout.
- [ ] 5.2 Manually verify cancellation: cancel the test subscription in Stripe test mode and confirm the user's Keycloak role reverts to `plan-free`.
