## Purpose

Provides the Speech platform's identity provider: a Keycloak realm where every user account, plan role, and OAuth2 client used by the dashboard backend and speech-app is defined, so downstream changes can authenticate users and read their plan from a token claim.

## ADDED Requirements

### Requirement: Dedicated realm for the Speech platform
The system SHALL run a Keycloak realm dedicated to the Speech platform, separate from the `master` administrative realm, and its configuration SHALL be reproducible from a committed realm export rather than only existing as manual admin-console clicks.

#### Scenario: Realm is importable from source
- **WHEN** a developer runs the documented setup against a fresh Keycloak instance
- **THEN** the Speech realm, its roles, and its clients are created automatically from the committed realm export, with no manual admin-console configuration required

#### Scenario: Master realm is untouched
- **WHEN** the Speech realm is created
- **THEN** no application user, role, or client is created in the `master` realm

### Requirement: Plan is represented as a realm role
The system SHALL represent each user's subscription plan as a Keycloak realm role named with a `plan-` prefix (e.g. `plan-free`, `plan-pro`), and every user account SHALL have exactly one `plan-*` role assigned at any given time.

#### Scenario: New user has a default plan role
- **WHEN** a user account is created in the realm without an explicit plan assignment
- **THEN** the account is assigned the `plan-free` role

#### Scenario: Plan change is a role reassignment
- **WHEN** a user's plan changes from one tier to another
- **THEN** the user's previous `plan-*` role is removed and the new tier's `plan-*` role is added, leaving exactly one `plan-*` role on the account

### Requirement: Plan role is exposed as a token claim
The system SHALL include the user's `plan-*` role in the access token issued by the realm, via a client scope/protocol mapper, so a relying party can read the user's plan without a separate API call back to Keycloak.

#### Scenario: Access token carries the plan claim
- **WHEN** a user authenticates and receives an access token from the Speech realm
- **THEN** the decoded token contains a claim identifying the user's current `plan-*` role

### Requirement: Confidential client for the dashboard backend
The system SHALL provide a confidential OAuth2 client, scoped to the Speech realm, for the dashboard backend service to validate user tokens and read role claims. Its credentials SHALL NOT be usable by public/untrusted clients (e.g. the desktop app or browser).

#### Scenario: Backend validates a user token
- **WHEN** the dashboard backend receives a request bearing a user access token
- **THEN** the backend can validate that token's signature and claims against the confidential client's configuration in the Speech realm

### Requirement: Public client for device authorization grant
The system SHALL provide a public OAuth2 client, scoped to the Speech realm, configured to support the OAuth2 Device Authorization Grant flow, for headless/desktop applications (speech-app) that cannot securely embed a client secret or host a browser-based redirect.

#### Scenario: Desktop app initiates device login
- **WHEN** a desktop application requests a device code from the Speech realm using the public device-flow client
- **THEN** the realm issues a device code and user code, and the application can poll for a token after the user approves the request in a browser

#### Scenario: Public client has no confidential secret
- **WHEN** the public client's configuration is inspected
- **THEN** it has no client secret whose disclosure would compromise the realm (it is registered as a public client)
