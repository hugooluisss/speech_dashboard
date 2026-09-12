## 1. Usage table

- [ ] 1.1 Add the `usage_periods` migration (subject id, period key e.g. `YYYY-MM`, words used, updated-at; unique on subject id + period key); verify the migration applies cleanly.
- [ ] 1.2 Implement `UsageRepository` with an atomic upsert-increment method and a get-by-subject-and-period method; verify unit tests cover creating a new period row and incrementing an existing one, including a concurrency test (two increments in parallel sum correctly).

## 2. Quota computation

- [ ] 2.1 Implement `UsageService.get_usage(subject_id, plan)`: resolves the current UTC calendar-month period key, reads (or defaults to zero) the usage row, reads the plan's word limit, and returns used/limit/remaining (remaining never negative); verify unit tests cover zero-usage-for-new-period, partial usage, and usage at/over the limit.
- [ ] 2.2 Implement `UsageService.has_remaining_quota(subject_id, plan) -> bool`; verify unit tests cover true when remaining > 0 and false when remaining == 0.
- [ ] 2.3 Implement `UsageService.record_usage(subject_id, word_count)` calling the repository's atomic increment; verify a unit test confirms repeated calls in the same period accumulate correctly.

## 3. Authenticated usage endpoint

- [ ] 3.1 Implement the `/usage` controller: validates the token, resolves the caller's plan (from the token's `plan-*` claim and the plan catalog), calls `UsageService.get_usage`, returns used/limit/period/remaining; verify an integration test against a real Postgres database returns the expected shape for a user with no prior usage and for a user with recorded usage.

## 4. Verification

- [ ] 4.1 Manually verify period rollover behavior: insert a usage row for a past period key, confirm `/usage` for the current period still reports zero used (not carrying over the prior period's total).
