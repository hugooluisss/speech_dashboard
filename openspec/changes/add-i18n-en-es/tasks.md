## 1. Language resolution

- [x] 1.1 Implement `resolveLocale(request)` in the frontend: reads the override cookie first, then `Accept-Language`, defaulting to English if neither indicates `en` or `es`; verify unit tests cover cookie-present, header-only, and neither-present cases.
- [x] 1.2 Implement the language switch UI in `Layout.astro` (visible on both landing and dashboard pages) that sets the override cookie and reloads the current page; verify manually that switching persists across a subsequent page load.
- [x] 1.3 Wire `resolveLocale` into the shared layout so every page has the resolved locale available; verify a request with `Accept-Language: es` renders Spanish content end to end on the landing page.

## 2. Translation dictionaries

- [x] 2.1 Create `frontend/src/i18n/landing.ts` with `en`/`es` keys for every landing page string; verify a script/test asserts both locale objects have identical key sets (no missing translations).
- [x] 2.2 Create `frontend/src/i18n/dashboard.ts` with `en`/`es` keys for every dashboard UI string (nav, plan/usage labels, billing actions, admin table); verify the same key-parity check covers this dictionary.
- [x] 2.3 Update `index.astro` to render all copy through the translation dictionary and resolved locale; verify manually in both languages with no leftover hard-coded English strings.
- [x] 2.4 Update `dashboard/index.astro` and `dashboard/admin.astro` to render all UI strings through the translation dictionary; verify manually in both languages, confirming dynamic values (username, plan name, numbers) remain untranslated.

## 3. Backend error localization

- [x] 3.1 Create a small `messages` module in the backend mapping known error keys to English/Spanish text; verify a unit test confirms both languages exist for every key.
- [x] 3.2 Update each existing `HTTPException` raise site for a known user-facing error (quota exceeded, not authenticated, unknown plan, no Stripe customer record) to select its detail message via this module based on the request's `Accept-Language` header; verify unit tests cover at least one endpoint returning the Spanish message for `Accept-Language: es` and English otherwise, with the HTTP status code unchanged in both cases.
- [x] 3.3 Update the frontend's server-side calls to the backend (in `dashboard/*.astro` and the auth/billing route handlers) to forward the resolved locale as the `Accept-Language` header; verify manually that a Spanish-resolved dashboard session sees a Spanish error message from a triggered backend error (e.g. attempting checkout with an invalid plan id).

## 4. Keycloak realm internationalization

- [x] 4.1 Enable `internationalizationEnabled: true` with `supportedLocales: ["en", "es"]` and a default locale on the Speech realm in the realm export; verify by re-importing the realm and confirming the setting via the admin API.
- [x] 4.2 Manually verify a Keycloak-hosted login page renders in Spanish for a request with `Accept-Language: es` and in English otherwise.

## 5. Verification

- [x] 5.1 Manually verify the full override flow end to end: load the landing page with an English browser locale, switch to Spanish via the language switch, navigate to the dashboard, confirm it also renders in Spanish, and confirm a triggered backend error also appears in Spanish.
