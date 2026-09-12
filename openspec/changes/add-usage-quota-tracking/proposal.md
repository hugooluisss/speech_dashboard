## Why

The whole point of the plan model is that a plan caps how many words a user can transcribe in a period (e.g. a month). `add-plans-billing` establishes what plan a user is on and its word limit; this change makes that limit actually mean something: recording how many words a user has used, exposing that to the dashboard, and giving the cloud transcription endpoint a way to check and enforce the limit before it does paid, metered work.

## What Changes

- Add a `usage_periods` table tracking, per user and per billing period (calendar month, UTC), how many words have been transcribed so far.
- Add `UsageService` operations: check remaining quota for a user (reads their plan's word limit from `add-plans-billing`'s `plans` table and their current period's usage), and record additional words used after a successful transcription.
- Add an authenticated endpoint returning the caller's current usage (words used, limit, period, remaining) for the dashboard UI to render.
- Define the enforcement contract: a caller that wants to start a cloud transcription must check remaining quota first and receive a rejection if the user has none left; this change implements the check itself, `add-cloud-transcription-api` (built after this) is responsible for calling it from the actual transcription request path.
- Handle period rollover: a new calendar month with no usage row yet reads as zero used, not an error.

## Capabilities

### New Capabilities
- `usage/quota-tracking`: Recording per-period word usage per user, computing remaining quota against the user's plan, and exposing both to authenticated callers (the dashboard UI and, later, the transcription endpoint).

### Modified Capabilities
(none)

## Impact

- New: `usage_periods` table and corresponding repository/service/controller in the backend's layered structure.
- Depends on `add-plans-billing`'s `plans` table (word limit per plan) and `add-dashboard-backend-base`'s authenticated-user pattern.
- `add-cloud-transcription-api` depends on this change's quota-check operation to decide whether to accept a transcription request.
