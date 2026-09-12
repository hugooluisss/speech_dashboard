## Purpose

Lets the backend authenticate incoming requests using Keycloak-issued access tokens and expose the caller's identity and plan to request handlers, so every protected endpoint has a single, consistent way to know who is calling and what plan they're on.

## ADDED Requirements

### Requirement: Requests require a valid access token
The system SHALL reject requests to protected endpoints that do not include a valid, unexpired access token issued by the Speech realm, signed by a key the backend trusts (validated against the realm's published signing keys).

#### Scenario: Missing token is rejected
- **WHEN** a request to a protected endpoint has no access token
- **THEN** the system responds with an authentication error and does not invoke the endpoint's business logic

#### Scenario: Invalid or expired token is rejected
- **WHEN** a request includes a token that fails signature verification or has expired
- **THEN** the system responds with an authentication error and does not invoke the endpoint's business logic

#### Scenario: Valid token is accepted
- **WHEN** a request includes a token that is correctly signed, unexpired, and issued by the Speech realm
- **THEN** the system invokes the endpoint's business logic

### Requirement: Authenticated identity and plan are available to handlers
The system SHALL extract the user's subject identifier and current `plan-*` role from a validated access token and make both available to the request handler, so business logic never needs to re-parse the token.

#### Scenario: Handler receives the caller's plan
- **WHEN** a request with a valid token containing the `plan-pro` claim reaches a protected endpoint
- **THEN** the handler can read the caller's subject identifier and that their plan is `plan-pro`

### Requirement: Authenticated self endpoint
The system SHALL provide an authenticated endpoint that returns the caller's own subject identifier and current plan, proving the full authentication path works end to end.

#### Scenario: Caller retrieves their own identity and plan
- **WHEN** an authenticated user requests their own profile endpoint
- **THEN** the response includes their subject identifier and their current `plan-*` role
