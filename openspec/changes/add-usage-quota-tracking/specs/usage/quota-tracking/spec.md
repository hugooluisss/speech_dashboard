## Purpose

Tracks how many words a user has transcribed in their current billing period against their plan's word limit, so the platform can show usage to the user and refuse further paid transcription once the limit is reached.

## ADDED Requirements

### Requirement: Per-period usage is tracked per user
The system SHALL record, for each user and each billing period (a calendar month, UTC), the total number of words transcribed by that user in that period.

#### Scenario: First transcription in a new period
- **WHEN** a user's first successful transcription of a new calendar month is recorded
- **THEN** the system creates a usage record for that user and period starting from that word count

#### Scenario: Subsequent transcription in the same period
- **WHEN** a user who already has a usage record for the current period completes another transcription
- **THEN** the system adds the new word count to the existing period's total rather than creating a second record

#### Scenario: New period has no prior usage
- **WHEN** a user's usage is checked for a calendar month with no recorded transcriptions yet
- **THEN** the system reports zero words used for that period, not an error

### Requirement: Remaining quota is computed from the user's plan
The system SHALL compute a user's remaining quota as their plan's word-limit-per-period minus their current period's recorded usage, reading the limit from the plan catalog (`billing/plan-catalog`).

#### Scenario: User with unused quota
- **WHEN** a user on a plan with a 10,000-word limit has used 3,000 words this period
- **THEN** their computed remaining quota is 7,000 words

#### Scenario: User who has exhausted their quota
- **WHEN** a user's recorded usage for the period meets or exceeds their plan's word limit
- **THEN** their computed remaining quota is zero (not negative)

### Requirement: Quota is checked before accepting further usage
The system SHALL provide a check that a caller performs before recording new usage, indicating whether the user has any quota remaining, so a caller can reject an action (such as starting a cloud transcription) before performing costly work for a user with no quota left.

#### Scenario: Request is allowed when quota remains
- **WHEN** a caller checks quota for a user with remaining quota greater than zero
- **THEN** the check indicates the action may proceed

#### Scenario: Request is refused when quota is exhausted
- **WHEN** a caller checks quota for a user with zero remaining quota
- **THEN** the check indicates the action must not proceed

### Requirement: Authenticated usage endpoint
The system SHALL provide an authenticated endpoint that returns the caller's own current period's word usage, their plan's limit, and their remaining quota.

#### Scenario: User retrieves their own usage
- **WHEN** an authenticated user requests their usage
- **THEN** the response includes their current period's words used, their plan's word limit, and their remaining quota
