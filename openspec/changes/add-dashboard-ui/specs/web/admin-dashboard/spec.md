## Purpose

Gives an admin read-only visibility into users, their plans, and their usage, for support and operational purposes, without exposing this to non-admin users.

## ADDED Requirements

### Requirement: Admin view requires the admin role
The system SHALL only allow a visitor whose account carries the `admin` realm role to access the admin dashboard page; any other signed-in visitor SHALL be refused access.

#### Scenario: Non-admin is refused
- **WHEN** a signed-in user without the `admin` role requests the admin dashboard page
- **THEN** they are refused access and do not see any user list content

#### Scenario: Admin is granted access
- **WHEN** a signed-in user with the `admin` role requests the admin dashboard page
- **THEN** they see the user list content

### Requirement: Admin sees users with their plan and usage
The system SHALL list, on the admin dashboard page, each user's identifier, current plan, and current period's word usage.

#### Scenario: Admin views the user list
- **WHEN** an admin loads the admin dashboard page
- **THEN** they see a list of users each showing an identifier, current plan, and current period's usage
