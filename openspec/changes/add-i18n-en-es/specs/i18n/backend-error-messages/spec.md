## Purpose

Makes backend API error messages match the caller's language, so a Spanish-speaking user sees a Spanish "quota exceeded" message rather than an English one embedded in a Spanish-language dashboard.

## ADDED Requirements

### Requirement: Known error messages are localized by request language
The system SHALL render the message text of known, user-facing error responses (e.g. quota exceeded, not authenticated, unknown plan, no Stripe customer record) in Spanish when the request's `Accept-Language` header indicates Spanish, and in English otherwise.

#### Scenario: Spanish-language request gets a Spanish error message
- **WHEN** a request whose `Accept-Language` header indicates Spanish triggers a known error condition (e.g. quota exceeded)
- **THEN** the error response's message text is in Spanish

#### Scenario: Request with no language preference gets English
- **WHEN** a request with no `Accept-Language` header, or one indicating a language other than Spanish, triggers a known error condition
- **THEN** the error response's message text is in English

### Requirement: Error codes remain stable across languages
The system SHALL keep HTTP status codes and any machine-readable error identifiers unchanged regardless of language; only the human-readable message text is localized.

#### Scenario: Status code unaffected by language
- **WHEN** the same error condition is triggered by requests in different languages
- **THEN** both responses use the identical HTTP status code, differing only in message text
