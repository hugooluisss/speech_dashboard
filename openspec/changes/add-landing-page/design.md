## Context

See proposal.md - Why. This is the first frontend code in `speech_dashboard`; no Astro project exists yet. `add-dashboard-ui` (planned after this) will add authenticated routes to the same Astro project rather than starting a second one.

## Goals / Non-Goals

**Goals:**
- A real, working Astro project scaffold that `add-dashboard-ui` can extend, not a throwaway prototype.
- Marketing content that's honest about what the product does today (per spec, sourced from `speech-app`'s actual README), so it doesn't need a rewrite the moment someone checks it against the real app.
- A page that works and looks coherent on both desktop and phone widths.

**Non-Goals:**
- Authenticated pages, account state, or any dashboard functionality — that's `add-dashboard-ui`.
- A CMS or dynamic content system for marketing copy — static content in the Astro project, edited via code changes, is enough for a single landing page.
- Live-fetched pricing from the backend — see the proposal's static-pricing decision below.
- SEO/analytics tooling, A/B testing, or a full design system — a coherent single page is the bar for this change.

## Decisions

**Astro, static output for the landing page.** Astro ships zero JS by default for static content, which is exactly what a marketing page needs (fast, simple, no client-side framework overhead) while still giving `add-dashboard-ui` a path to add interactive/authenticated islands later in the same project without switching frameworks.

**Pricing content is static copy, not a live call to the backend's `/plans` endpoint.** That endpoint (from `add-plans-billing`) requires authentication; making it public for this one page would mean adding a new public endpoint and a client-side fetch for a page that's otherwise fully static. For a small number of fixed tiers, keeping pricing copy in the Astro project and updating it by hand when tiers change is simpler and matches the proposal's accepted trade-off. Revisit only if plan tiers/pricing change often enough that manual sync becomes a real problem.

**Sign-up/login links directly to Keycloak's own hosted pages for the Speech realm**, not a custom-built login form. Keycloak already serves a complete login/registration UI; building a second one on the landing page would duplicate it for no functional gain at this stage.

**Single page, not a multi-page marketing site.** The proposal's scope (hero, features, pricing, CTA) fits comfortably as sections on one page; splitting into multiple routes is unnecessary structure for content this size.

## Risks / Trade-offs

- [Static pricing copy can drift from the actual `plans` table if someone changes a price/limit in the backend without updating this page] → Accepted as a manual step (documented in the proposal); revisit if this becomes a recurring source of bugs or confusion.
- [No analytics means no visibility into conversion from this page] → Out of scope for this change; add later if/when it's actually needed.

## Migration Plan

Greenfield addition (`frontend/` doesn't exist yet). Nothing to migrate.
