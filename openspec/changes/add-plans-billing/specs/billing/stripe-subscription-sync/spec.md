## Purpose

Keeps a user's Keycloak `plan-*` role in sync with what they actually pay for in Stripe, so the plan role can be trusted as the current, paid-for entitlement without a separate billing check on every request.

## ADDED Requirements

### Requirement: Checkout session creation
The system SHALL allow an authenticated user to start a Stripe Checkout session for any non-free plan in the catalog, associated with that user's identity so the resulting subscription can be attributed to them.

#### Scenario: User starts checkout for a paid plan
- **WHEN** an authenticated user requests checkout for a specific paid plan
- **THEN** the system creates a Stripe Checkout session for that plan's price and returns a URL the user can complete payment at

#### Scenario: Checkout is rejected for an unknown plan
- **WHEN** an authenticated user requests checkout for a plan identifier that does not exist in the catalog
- **THEN** the system rejects the request without creating a Stripe session

### Requirement: Subscription events update the user's plan role
The system SHALL process Stripe subscription lifecycle webhook events (subscription created, updated, cancelled) and, for each event tied to a known user, update that user's Keycloak `plan-*` role to match the plan corresponding to their current active Stripe subscription.

#### Scenario: Successful subscription grants the paid role
- **WHEN** a Stripe webhook reports an active subscription for a user on the `plan-pro` price
- **THEN** the system assigns the `plan-pro` role to that user in Keycloak and removes any previous `plan-*` role

#### Scenario: Cancelled subscription reverts to free
- **WHEN** a Stripe webhook reports a subscription has been cancelled or has finally failed payment for a user
- **THEN** the system assigns the `plan-free` role to that user in Keycloak and removes the prior paid `plan-*` role

### Requirement: Webhook authenticity verification
The system SHALL verify the authenticity of incoming Stripe webhook requests using Stripe's signature verification before acting on their contents.

#### Scenario: Unsigned or invalid webhook is rejected
- **WHEN** a request to the webhook endpoint fails Stripe signature verification
- **THEN** the system rejects the request and does not change any user's plan role

### Requirement: Stripe linkage is persisted per user
The system SHALL persist each user's Stripe customer identifier and current subscription status, so the system can reconcile plan state without querying Stripe on every request.

#### Scenario: User's Stripe identifiers are recorded after first checkout
- **WHEN** a user completes their first successful checkout
- **THEN** the system stores that user's Stripe customer identifier and subscription status for later reference
