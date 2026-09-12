## ADDED Requirements

### Requirement: Billing portal session creation
The system SHALL allow an authenticated user with an existing Stripe customer record to request a Stripe customer billing-portal session, returning a URL the user can use to manage their payment method and subscription directly with Stripe.

#### Scenario: User with a Stripe customer record requests portal access
- **WHEN** an authenticated user who has completed at least one checkout requests a billing-portal session
- **THEN** the system returns a URL to a Stripe customer portal session scoped to that user's Stripe customer record

#### Scenario: User with no Stripe customer record is refused
- **WHEN** an authenticated user who has never completed a checkout requests a billing-portal session
- **THEN** the system refuses the request without calling Stripe's portal API
