## Purpose

Gives a signed-in user visibility into their own plan and usage, and a way to change plans or manage billing, without needing to contact support or inspect raw API responses.

## ADDED Requirements

### Requirement: User sees their own plan and usage
The system SHALL display, on the signed-in user's dashboard page, their current plan name, their word usage for the current period, their plan's word limit, and their remaining quota.

#### Scenario: User views their dashboard
- **WHEN** a signed-in user loads their dashboard page
- **THEN** they see their current plan, usage, limit, and remaining quota for the current period

### Requirement: User can start a plan upgrade
The system SHALL provide an action on the user's dashboard that starts a Stripe Checkout session for a plan the user selects, redirecting them to complete payment.

#### Scenario: User starts an upgrade
- **WHEN** a signed-in user selects a paid plan's upgrade action
- **THEN** they are redirected to a Stripe Checkout session for that plan

### Requirement: User can manage billing
The system SHALL provide an action on the user's dashboard that opens Stripe's hosted customer billing portal for the signed-in user.

#### Scenario: User opens billing management
- **WHEN** a signed-in user with an existing Stripe customer record selects "manage billing"
- **THEN** they are redirected to their Stripe customer portal session
