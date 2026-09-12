## Purpose

Provides authenticated session handling for the Astro dashboard app, so protected pages can rely on knowing who the visitor is before rendering anything.

## ADDED Requirements

### Requirement: Unauthenticated visitors are redirected to login
The system SHALL redirect a visitor with no valid session to the Speech realm's hosted login page when they request a protected dashboard route.

#### Scenario: Anonymous visitor is redirected
- **WHEN** a visitor with no session requests a protected dashboard page
- **THEN** they are redirected to the Speech realm's login page instead of seeing the page content

### Requirement: Successful login establishes a session
The system SHALL, after a visitor completes login via the Authorization Code flow with PKCE, establish a session (via a cookie) that protected routes can use to identify the visitor on subsequent requests.

#### Scenario: Login callback establishes a session
- **WHEN** a visitor completes login and is redirected back to the dashboard app's callback route
- **THEN** a session is established such that the visitor can access protected routes without logging in again

### Requirement: Logout ends the session
The system SHALL provide a logout action that clears the visitor's dashboard session and ends their Keycloak session.

#### Scenario: Visitor logs out
- **WHEN** a signed-in visitor selects logout
- **THEN** their dashboard session is cleared and a subsequent request to a protected route redirects them to login again
