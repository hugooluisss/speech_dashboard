## Context

See proposal.md - Why. Builds on `add-landing-page` and `add-dashboard-ui` (the Astro app whose content this change translates) and `add-dashboard-backend-base`/`add-usage-quota-tracking`/`add-plans-billing`/`add-cloud-transcription-api` (the backend endpoints whose error messages this change localizes). Also touches `deploy-keycloak-auth`'s realm export (a configuration addition, not a new client).

## Goals / Non-Goals

**Goals:**
- Automatic, correct language detection with no visitor action required, and an easy, obvious way to override it.
- No URL-shape change — same routes, same links, same SEO-relevant URLs regardless of language, per the user's explicit choice.
- Full coverage: no untranslated strings left on any page this change touches.

**Non-Goals:**
- More than two languages — the mechanism should be simple to extend later, but only English and Spanish content is written now.
- Per-user persisted language preference tied to their account (stored server-side, synced across devices) — a browser cookie is enough for this change; account-level preference is a future enhancement if requested.
- Translating speech-app's own desktop UI — out of scope, a separate product surface.
- A general-purpose i18n framework/library — see Decisions.

## Decisions

**Cookie-plus-header resolution, not Astro's built-in path-based i18n routing.** Astro's official i18n integration assumes locale-prefixed URLs (`/en/...`, `/es/...`), which the user explicitly said not to do. Implementing detection and override directly (read `Accept-Language`, check an override cookie, pick a locale) is a small amount of code and avoids fighting the framework's routing assumptions to get non-prefixed behavior out of it.

**Plain per-locale string dictionaries, not an i18n library.** Two languages and a bounded set of UI strings don't need pluralization rules, ICU message format, or a translation-management pipeline. A `{ en: {...}, es: {...} }` dictionary per surface (landing, dashboard) with a small `t(key, locale)` helper is simpler to write, review, and keep in sync than introducing a library (e.g. i18next) whose plural/interpolation machinery this project doesn't need yet.

**Override cookie takes precedence over `Accept-Language` on every request; no server-side account preference.** Matches the spec's persistence requirement with the least mechanism: a cookie the Astro server reads on each request, set by the language switch, requiring no database change and no authentication (works identically for anonymous landing-page visitors and signed-in dashboard users).

**Backend localizes only known, already-enumerated error messages, not free-form exception text.** The backend already raises specific `HTTPException`s with fixed detail strings for known conditions (quota exceeded, not authenticated, unknown plan, no Stripe customer). Localization is a message-key lookup at each of those existing raise sites, reading `Accept-Language` from the incoming request — it does not attempt to translate arbitrary/unexpected error text, which would require a much larger mechanism for no real benefit (unexpected errors are bugs, not something a translated string improves).

**Keycloak's built-in internationalization, not a custom-styled login page.** Keycloak ships English and Spanish message bundles out of the box; enabling `internationalizationEnabled` with `supportedLocales: [en, es]` on the realm gets a localized hosted login/consent/device page for free, consistent with how the realm export already treats Keycloak's hosted pages as the source of truth for auth UI (per `add-landing-page`'s design, which deliberately didn't build a custom login form).

## Risks / Trade-offs

- [Backend and frontend resolve language independently (frontend from cookie-or-header, backend from header only, since it doesn't see the frontend's override cookie)] → Accepted: the frontend, when calling the backend on the user's behalf, forwards the resolved language as the `Accept-Language` header on its own backend requests, so a user's manual override is respected end to end without the backend needing to know about the cookie mechanism itself.
- [String dictionaries can drift out of sync (a key added in English, forgotten in Spanish)] → Mitigated by a build/test-time check (see tasks.md) that fails if a key exists in one locale's dictionary but not the other.
- [Keycloak's default Spanish translations may use different terminology/tone than this project's own Spanish copy] → Accepted as a minor, cosmetic inconsistency; Keycloak's hosted pages are a small, well-understood surface (login/consent) where built-in translations are good enough, not worth building a custom-translated login page to avoid.

## Migration Plan

Additive: new translation dictionaries, a new cookie, a new realm setting. No existing content is removed — English strings already written for the landing page and dashboard become the English half of each dictionary. Rollback is removing the language switch and defaulting resolution to English only, with no data to migrate back.
