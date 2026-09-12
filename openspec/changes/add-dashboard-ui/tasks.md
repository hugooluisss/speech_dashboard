## 1. Keycloak: web client and admin role

- [x] 1.1 Add the `speech-dashboard-web` client to the realm export (Authorization Code + PKCE, confidential or public per Keycloak's PKCE guidance, redirect URIs for local dev and the deployed dashboard); verify a manual Authorization Code + PKCE login against a locally running realm succeeds.
- [x] 1.2 Add the `admin` realm role to the realm export; verify it appears via the admin API after re-import.
- [x] 1.3 Re-export the realm JSON including both changes; verify `git diff` shows the new client and role.

## 2. Backend additions

- [x] 2.1 Implement the billing-portal endpoint (`BillingService.create_portal_session`, controller): refuses if the user has no stored Stripe customer id, otherwise creates and returns a Stripe portal session URL; verify unit tests cover both paths with a mocked Stripe client.
- [x] 2.2 Implement an admin-gated users-listing endpoint returning each user's identifier, current plan, and current period's usage, refusing callers without the `admin` role; verify unit tests cover an admin caller getting the list and a non-admin caller being refused.

## 3. Astro session handling

- [x] 3.1 Add the Node/server adapter and configure hybrid output (static landing routes, on-demand dashboard routes); verify the landing page still builds statically and a dashboard route renders on demand.
- [x] 3.2 Implement the login redirect and Authorization Code + PKCE callback route, establishing a session cookie on success; verify a manual login flow ends with a valid session cookie set.
- [x] 3.3 Implement middleware that redirects to login when a protected route is requested with no valid session; verify a request to a protected route with no cookie redirects to Keycloak login.
- [x] 3.4 Implement logout (clear session cookie, redirect to Keycloak end-session endpoint); verify a subsequent protected-route request after logout redirects to login again.

## 4. User dashboard page

- [x] 4.1 Build the user dashboard page calling `/me` and `/usage` server-side with the session's access token, rendering plan, usage, limit, and remaining quota; verify manually with a real signed-in test user.
- [ ] 4.2 Wire the upgrade action to `/billing/checkout`, redirecting the browser to the returned Stripe Checkout URL; verify manually with Stripe test mode (or a mocked checkout URL if Stripe test credentials are not yet available — mark this task's Stripe-specific verification pending in that case).
- [ ] 4.3 Wire the "manage billing" action to the new portal endpoint, redirecting to the returned URL; verify manually with a test user that has an existing Stripe customer record (or mark pending if Stripe test credentials are not yet available).

Verification pending: Stripe test credentials and a test customer/checkout session were not available. The frontend handlers are implemented; only the Stripe-specific manual checks remain.

## 5. Admin dashboard page

- [x] 5.1 Build the admin dashboard page calling the admin-gated listing endpoint, rendering a table of users/plans/usage; verify manually with a test user holding the `admin` role.
- [x] 5.2 Verify a non-admin signed-in user requesting the admin page is refused; verify manually with a test user lacking the `admin` role.

## 6. Verification

- [x] 6.1 Manually verify the full flow end-to-end: log in via the browser, view the user dashboard, sign out, confirm the protected route redirects to login again.
