## Context

See proposal.md - Why. Builds on `add-dashboard-backend-base` (layered backend, authenticated requests) and `add-plans-billing` (the `plans` table's word-limit-per-period values, and the user's current `plan-*` role). Does not touch billing or Keycloak; only adds usage accounting.

## Goals / Non-Goals

**Goals:**
- A simple, race-safe way to accumulate word counts per user per period without losing counts under concurrent requests.
- A clear, reusable "may this user do more transcription" check that `add-cloud-transcription-api` can call without duplicating quota logic.
- Correct behavior across period boundaries with no manual monthly reset job required.

**Non-Goals:**
- The actual transcription pipeline or word-counting logic from audio — that's `add-cloud-transcription-api`; this change only stores and checks numbers it's given.
- Notifying users as they approach their limit (e.g. "80% used" emails) — not requested; could be a future change.
- Historical usage analytics/reporting beyond the current period — only the current period's usage is required for enforcement and the dashboard's "usage so far" view.

## Decisions

**Period identity is a calendar month key (e.g. `2026-09`), computed from UTC, not a rolling 30-day window from signup.** Simpler to reason about, matches how the plan catalog already describes limits ("per month"), and avoids needing to track a per-user anchor date. Alternative considered: rolling window anchored to subscription start date — rejected as unnecessary complexity for what the proposal actually asked for (a period like "a month").

**Usage row is created lazily on first use of a period, not pre-created by a scheduled job.** A period with no row simply reads as zero usage (per spec). Avoids needing a cron job to pre-create rows for every user every month, and works correctly for the whole system even if it hasn't run for months.

**Increment is an atomic, single SQL statement (`UPDATE ... SET words = words + :n` / upsert), not read-then-write from the service layer.** Prevents lost updates if a user manages to trigger concurrent transcription requests. Alternative considered: application-level locking — rejected as unnecessary given Postgres can do this atomically with a single upsert statement.

**Quota check and usage recording are separate operations, not one atomic "check-and-record."** The proposal's flow is: check quota before starting a (potentially long-running) transcription, then record the actual word count after it completes — the word count isn't known until the transcription finishes, so there's an inherent gap. This means a user could start two transcriptions back-to-back and both pass the pre-check before either records usage, slightly overrunning their quota in a race. Accepted as a minor, self-correcting overrun (the next check will refuse further requests) rather than adding reservation/locking complexity for a limit that isn't a hard billing/metering boundary.

## Risks / Trade-offs

- [Concurrent requests near the quota boundary can cause a small overrun, as described above] → Accepted; not a hard metering guarantee. Revisit only if real usage shows this being exploited or causing support issues.
- [A user's plan changes mid-period (upgrade/downgrade via `add-plans-billing`) while they have existing usage recorded] → The remaining-quota computation always reads the *current* plan's limit against the *existing* period's accumulated usage, so an upgrade takes effect immediately (more remaining quota) and a downgrade could put a user immediately over their new, lower limit — both are treated as correct, immediate behavior, not a gap to fix here.
- [Calendar-month periods mean a user's period boundary isn't aligned to their individual signup/billing date] → Accepted as the simpler model; documented so `add-plans-billing` and support tooling don't assume per-user rolling periods.

## Migration Plan

Additive: new table, no changes to existing schemas. Nothing to migrate for existing users — their first check after this change deploys simply finds no usage row for the current period and reports zero used.
