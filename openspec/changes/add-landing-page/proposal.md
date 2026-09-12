## Why

None of the backend work (auth, billing, quota, cloud transcription) has anywhere for a new visitor to land, understand what Speech does, or start signing up. This change adds the public marketing site: a landing page describing Speech's real, existing features (from the current `speech-app` README) and its plans, with calls to action to download the app and sign up.

## What Changes

- Scaffold an Astro project at `frontend/` in this repo (the frontend for both the landing page and, in a later change, the authenticated dashboard).
- Build a single-page marketing site with: hero, feature highlights (drawn from `speech-app`'s actual current capabilities — local/private dictation, hands-free wake word, 100 languages, cross-app pasting, customizable hotkeys/cleanup/vocabulary), a pricing section listing plan tiers, and calls to action (download speech-app, sign up / log in).
- Pricing section content is static (editorial copy shipped with the page), not fetched live from the backend's authenticated `/plans` endpoint — visitors here are anonymous, and there's no public plan-listing endpoint yet.
- Login/sign-up CTA links to Keycloak's hosted login/registration for the Speech realm (no custom login form built here).
- Basic responsive layout and a favicon/branding placeholder (no dedicated design-system work beyond what's needed for a coherent single page).

## Capabilities

### New Capabilities
- `web/landing-page`: The public marketing site's structure and content (hero, features, pricing, CTAs), and the Astro project scaffolding it lives in.

### Modified Capabilities
(none)

## Impact

- New: `frontend/` Astro project (this is also where `add-dashboard-ui` will add authenticated routes afterward).
- No backend changes; the CTA to sign up links directly to Keycloak's own hosted pages for the Speech realm (`deploy-keycloak-auth`).
- Pricing copy will need to be kept in sync by hand with the actual plan catalog (`billing/plan-catalog`) until/unless a public plan-listing endpoint exists — documented as a known manual step, not automated in this change.
