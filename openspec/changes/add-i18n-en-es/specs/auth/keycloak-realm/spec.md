## ADDED Requirements

### Requirement: Realm supports English and Spanish
The system SHALL enable internationalization on the Speech realm with English and Spanish as supported locales, so Keycloak's own hosted pages (login, consent, device flow) render in the visitor's browser language.

#### Scenario: Spanish browser sees a Spanish login page
- **WHEN** a visitor with a Spanish-preferring browser reaches a Keycloak-hosted page for the Speech realm
- **THEN** the page renders in Spanish

#### Scenario: Unsupported browser language falls back to the realm default
- **WHEN** a visitor's browser language is neither English nor Spanish
- **THEN** the Keycloak-hosted page renders in the realm's configured default locale
