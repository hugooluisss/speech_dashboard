## MODIFIED Requirements

### Requirement: Confidential client for the dashboard backend
The system SHALL provide a confidential OAuth2 client, scoped to the Speech realm, for the dashboard backend service to validate user tokens and read role claims, and to manage a user's `plan-*` realm role via the Keycloak admin API on behalf of the billing system. Its credentials SHALL NOT be usable by public/untrusted clients (e.g. the desktop app or browser).

#### Scenario: Backend validates a user token
- **WHEN** the dashboard backend receives a request bearing a user access token
- **THEN** the backend can validate that token's signature and claims against the confidential client's configuration in the Speech realm

#### Scenario: Backend reassigns a user's plan role
- **WHEN** the billing system needs to change a user's plan following a Stripe subscription event
- **THEN** the confidential client's service account has sufficient realm role-management permission to remove the user's previous `plan-*` role and assign the new one via the Keycloak admin API
