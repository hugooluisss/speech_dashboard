## Why

The landing page, dashboard, and backend error messages are all English-only today. The product needs to serve both English and Spanish speakers without forcing a language choice on anyone: detect the visitor's browser language automatically, and let them override it with a visible switch.

## What Changes

- Add a language-preference mechanism shared by the landing page and dashboard (both live in the same Astro app): resolve the visitor's language from (in order) a manual-override cookie, then the browser's `Accept-Language` header, falling back to English if neither indicates English or Spanish. No URL prefix (`/en`, `/es`) — the same routes serve either language.
- Add a visible language switch (e.g. "EN / ES") in the shared layout, on both the landing page and the dashboard, that sets the override cookie and re-renders in the chosen language.
- Translate all landing page copy and dashboard UI strings (navigation, labels, buttons, plan/usage text) into English and Spanish.
- Localize backend error messages (e.g. "quota exceeded," "not signed in," "unknown plan") based on the caller's `Accept-Language` header, so API error responses match the caller's language without the frontend needing its own copy of every backend error string.
- Enable Keycloak's built-in realm internationalization (English + Spanish) so the hosted login/consent/device-flow pages Keycloak itself renders also respect the visitor's browser language — Keycloak ships these translations already; this is a realm configuration change, not new UI to build.

## Capabilities

### New Capabilities
- `i18n/language-preference`: Resolving and overriding the visitor's language (cookie override, `Accept-Language` fallback, English default) shared across the landing page and dashboard.
- `i18n/site-translations`: English and Spanish content for the landing page and dashboard UI.
- `i18n/backend-error-messages`: Backend API error messages rendered in the caller's language based on `Accept-Language`.

### Modified Capabilities
- `auth/keycloak-realm`: Enables realm internationalization (English + Spanish) so Keycloak's own hosted pages (login, consent, device flow) match the visitor's browser language.

## Impact

- Extends `frontend/`: a translation-dictionary mechanism and a language switch in `Layout.astro`, applied to `index.astro` and the `dashboard/*` pages.
- Extends `backend/`: error-message localization applied where `HTTPException` details are raised for known, user-facing error conditions.
- Extends `infra/keycloak/realm-export/speech-realm.json`: internationalization settings on the realm.
- No changes to speech-app (the desktop app's own UI language is out of scope for this change).
