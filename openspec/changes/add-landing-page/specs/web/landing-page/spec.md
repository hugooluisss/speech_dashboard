## Purpose

Gives a new visitor a public page that explains what Speech does, what plans exist, and how to get started (download the app, sign up), as the front door to the rest of the platform.

## ADDED Requirements

### Requirement: Public accessibility with no authentication
The system SHALL serve the landing page to any visitor without requiring sign-in or an account.

#### Scenario: Anonymous visitor loads the page
- **WHEN** a visitor with no account navigates to the landing page
- **THEN** the page loads fully, including feature and pricing content, with no login prompt

### Requirement: Feature content reflects actual product capabilities
The system SHALL describe Speech's dictation features on the landing page using only capabilities that exist in the current product (local/private dictation, hands-free wake word, multi-language support, cross-application pasting, customizable hotkeys/cleanup/vocabulary), without describing capabilities that do not yet exist.

#### Scenario: Feature list matches shipped functionality
- **WHEN** the landing page's feature section is reviewed against `speech-app`'s current README
- **THEN** every claim on the landing page corresponds to a capability described there

### Requirement: Pricing section lists plan tiers
The system SHALL display each plan tier's name, price, and word-limit-per-period on the landing page.

#### Scenario: Visitor sees plan tiers
- **WHEN** a visitor views the pricing section
- **THEN** they see each available plan's name, price, and word limit per period

### Requirement: Calls to action lead to download and sign-up
The system SHALL provide a call to action to download speech-app and a separate call to action to sign up or log in, with the sign-up/login action directing the visitor to the Speech realm's hosted authentication pages.

#### Scenario: Visitor starts sign-up
- **WHEN** a visitor selects the sign-up/login call to action
- **THEN** they are directed to the Speech realm's hosted login/registration page
