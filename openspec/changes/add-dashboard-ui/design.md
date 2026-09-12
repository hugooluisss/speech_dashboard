## Context

See proposal.md - Why. Builds on `add-landing-page`'s Astro scaffolding (static marketing pages), `add-dashboard-backend-base` (`/me`), `add-usage-quota-tracking` (`/usage`), and `add-plans-billing` (`/plans`, checkout, and this change's added portal endpoint). Astro's static output (from the landing page) needs to coexist with server-rendered, session-aware routes for the dashboard.

## Goals / Non-Goals

**Goals:**
- Authenticated dashboard routes that coexist with the existing static landing page in the same Astro project, without turning the whole site into a server app.
- A user view that answers "what plan am I on, how much have I used, how do I change that" without needing a second tool.
- A minimal, read-only admin view — visibility, not a management console — appropriate for the platform's current size.

**Non-Goals:**
- A full admin CRUD console for editing plan definitions — `add-plans-billing`'s design already established that plan catalog changes are a manual backend/Stripe step; this change doesn't revisit that.
- Real-time usage updates (e.g. live-updating as a dictation happens) — the dashboard reflects usage as of page load/refresh, matching how `/usage` itself works (computed on request, not pushed).
- Multi-admin role granularity (e.g. read-only vs. full admin) — one `admin` role, one level of access, for now.
- Assigning the `admin` role to any specific user — that's an operational action for whoever deploys this, not something this change automates.

## Decisions

**Astro's hybrid/on-demand rendering for dashboard routes, static for landing page routes.** Astro supports per-route rendering control; the existing landing page stays statically generated (from `add-landing-page`), while dashboard routes (`/dashboard/*`) opt into server rendering so they can check session state per request. This avoids rebuilding the entire site as server-rendered just to add an authenticated section.

**Authorization Code flow with PKCE for the browser client**, not the device flow (that's for headless speech-app) or a shared client with the backend (the backend's confidential client holds a secret unsuitable for a browser). This is the standard OAuth2 pattern for a server-rendered web app with a real redirect URI.

**Session state is a server-side cookie referencing tokens held by the Astro server process**, not tokens stored client-side in the browser (e.g. localStorage), to avoid exposing access/refresh tokens to client-side JavaScript. The dashboard's own backend-for-frontend (the Astro server) calls the `speech_dashboard` backend API on the user's behalf using the session's stored access token.

**The admin view calls a new, admin-gated backend listing endpoint** (added as part of this change's scope alongside the portal endpoint) that joins user, plan, and usage data server-side, rather than the Astro app calling multiple existing per-user endpoints in a loop for every user — simpler and avoids N+1-style calls from the frontend. This endpoint's authorization check (does the caller have the `admin` role) mirrors the pattern already established for `plan-*` claim checks.

**Billing portal endpoint reuses the existing Stripe customer id already stored** by `add-plans-billing`'s webhook handler; no new Stripe customer-linkage logic is needed, only a new endpoint that calls Stripe's portal session API with that stored id.

## Risks / Trade-offs

- [Mixing static and server-rendered routes in one Astro project adds a small amount of build/deploy complexity compared to an all-static site] → Accepted; it's the standard way Astro supports this exact use case (hybrid output), not a workaround.
- [Admin listing endpoint reads across all users, which could become slow at scale without pagination] → Acceptable at current expected scale; pagination is a documented follow-up if the user base grows enough to matter, not built preemptively.
- [Session cookie approach requires the Astro server to be a genuinely running server process (not purely static hosting) in production] → Accepted as a real deployment requirement introduced by this change; documented so deployment planning accounts for it.

## Migration Plan

Additive: new Keycloak client and role (via realm export update), new backend endpoints, new Astro routes. No changes to existing static landing content or existing endpoint behavior. Rollback is removing the new routes/client/role without affecting the landing page or any other change's functionality.
