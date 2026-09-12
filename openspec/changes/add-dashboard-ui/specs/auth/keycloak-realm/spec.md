## ADDED Requirements

### Requirement: Browser-based client for the web dashboard
The system SHALL provide an OAuth2 client, scoped to the Speech realm, configured for the Authorization Code flow with PKCE, for the Astro dashboard's browser-based login, distinct from the backend's confidential client and speech-app's device-flow client.

#### Scenario: Dashboard initiates browser login
- **WHEN** the Astro dashboard app redirects a visitor to log in
- **THEN** the redirect uses the web dashboard client's Authorization Code + PKCE configuration and a registered redirect URI for the dashboard app

### Requirement: Admin realm role
The system SHALL define an `admin` realm role, separate from `plan-*` roles, that a user account may additionally hold to gain access to admin-only surfaces.

#### Scenario: Admin role coexists with a plan role
- **WHEN** a user account holds both a `plan-*` role and the `admin` role
- **THEN** both roles are present in the user's effective realm roles, and neither is removed by the other's assignment
