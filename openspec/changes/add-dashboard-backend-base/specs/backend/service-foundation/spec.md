## Purpose

Establishes the dashboard backend's layered request-handling structure and its Postgres-backed persistence, so every later capability (billing, usage tracking, cloud transcription, admin actions) is added as controllers/services/repositories rather than ad hoc code.

## ADDED Requirements

### Requirement: Layered request handling
The system SHALL organize backend request handling into three layers with a fixed direction of dependency: controllers depend on services, services depend on repositories, and repositories are the only layer that accesses the data store directly. A controller SHALL NOT access the data store directly, and a service SHALL NOT perform HTTP request/response handling.

#### Scenario: Controller delegates to a service
- **WHEN** an HTTP request reaches a controller
- **THEN** the controller parses the request and delegates business logic to a service, without executing data-store queries itself

#### Scenario: Service delegates persistence to a repository
- **WHEN** a service needs to read or write data
- **THEN** it calls a repository method rather than issuing a data-store query itself

### Requirement: Unauthenticated health check
The system SHALL expose a `/health` endpoint that reports service availability without requiring authentication, so infrastructure (load balancers, uptime checks) can verify the service is running.

#### Scenario: Health check succeeds while the service is up
- **WHEN** a client sends a request to `/health`
- **THEN** the service responds with a success status and no authentication is required

### Requirement: Persisted user record
The system SHALL persist a record per known user, keyed by the Keycloak subject identifier, so later capabilities (usage tracking, billing) can attach data to a user without re-deriving identity from a token on every write.

#### Scenario: First authenticated request creates a user record
- **WHEN** a request from a Keycloak subject id with no existing user record is authenticated successfully
- **THEN** the system creates a user record for that subject id, so subsequent requests find an existing record

#### Scenario: Subsequent requests reuse the existing record
- **WHEN** a request from a Keycloak subject id with an existing user record is authenticated
- **THEN** the system does not create a duplicate user record
