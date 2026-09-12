## Purpose

Defines the set of purchasable plans (tier, corresponding Keycloak role, price, and word-limit-per-period) as data the rest of the system reads, so pricing/limits live in one place instead of being hard-coded per feature.

## ADDED Requirements

### Requirement: Plan catalog entry shape
The system SHALL store each plan as a record containing: a unique tier identifier, a human-readable display name, the corresponding Keycloak `plan-*` role name, a Stripe Price identifier, and a word-limit-per-period value with its period unit (e.g. monthly).

#### Scenario: A plan record is complete
- **WHEN** a plan is defined in the catalog
- **THEN** it has a tier identifier, display name, Keycloak role name, Stripe Price identifier, word limit, and period unit, with none of these fields empty

### Requirement: Free plan exists with no payment required
The system SHALL include a `plan-free` catalog entry that has no associated Stripe Price and represents the default tier a user has before any successful checkout.

#### Scenario: Free plan has no checkout requirement
- **WHEN** the plan catalog is listed
- **THEN** the `plan-free` entry is present and does not require a Stripe purchase to be active

### Requirement: Authenticated plan listing
The system SHALL provide an authenticated endpoint that lists all active plans in the catalog, for display in the dashboard's pricing/upgrade UI.

#### Scenario: Authenticated user lists plans
- **WHEN** an authenticated user requests the plan catalog
- **THEN** the response includes every active plan's display name, price information, and word-limit-per-period
