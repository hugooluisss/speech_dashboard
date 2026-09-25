# Spec Delta

## Purpose

Lets an authenticated user pay for a plan upgrade without leaving the dashboard, by rendering Stripe's checkout UI inside an on-page modal instead of redirecting to a Stripe-hosted page.

## ADDED Requirements

### Requirement: Checkout session returns an embeddable client secret
The system SHALL create a Stripe Checkout Session for the requested plan in embedded mode and return a client secret the frontend can use to render payment inline, instead of a hosted URL to redirect to.

#### Scenario: User starts checkout for a paid plan
- **WHEN** an authenticated user requests checkout for a specific paid plan
- **THEN** the system creates a Stripe Checkout Session for that plan's price in embedded mode and returns a client secret associated with that session

#### Scenario: Checkout is rejected for an unknown plan
- **WHEN** an authenticated user requests checkout for a plan identifier that does not exist in the catalog
- **THEN** the system rejects the request without creating a Stripe session

### Requirement: Upgrade opens an on-site payment modal
The system SHALL let the user complete a plan upgrade inside a modal on the dashboard page, without navigating away to a different origin.

#### Scenario: User opens the upgrade modal
- **WHEN** an authenticated user chooses a paid plan and confirms they want to upgrade
- **THEN** the dashboard opens a modal in place, on the same page, and renders Stripe's embedded checkout UI inside it using the session's client secret

#### Scenario: User closes the modal without paying
- **WHEN** the user dismisses the modal before completing payment
- **THEN** the modal closes, no plan change is applied, and the user remains on the dashboard with their current plan unchanged

### Requirement: Modal reflects payment completion
The system SHALL detect when the embedded checkout reports the payment as complete and reflect that outcome to the user without a full-page redirect to Stripe.

#### Scenario: Payment completes successfully
- **WHEN** the embedded checkout reports successful completion of the Checkout Session
- **THEN** the modal shows a success state, closes, and the dashboard reflects the user's updated plan once the subscription is confirmed

#### Scenario: Payment fails inside the modal
- **WHEN** the embedded checkout reports a payment error (e.g. card declined)
- **THEN** the modal shows the error inline and lets the user retry without closing the modal or losing their plan selection

### Requirement: Current period shows the paid plan's renewal date
The system SHALL display when a paid plan's current billing period ends, for a user with an active paid subscription.

#### Scenario: Paid user sees their renewal date
- **WHEN** an authenticated user with an active paid subscription views their dashboard
- **THEN** the current period display includes the date their subscription renews

#### Scenario: Free user sees no renewal date
- **WHEN** an authenticated user with no active paid subscription views their dashboard
- **THEN** the current period display includes no renewal date
