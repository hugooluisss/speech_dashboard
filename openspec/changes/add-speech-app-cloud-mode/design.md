## Context

See proposal.md - Why and its cross-repo note: this change's code lands in the sibling `speech-app` repository, not `speech_dashboard`. speech-app today (per its own `CLAUDE.md`) is a platform-split desktop app with a central `AppController` orchestrating a `Recorder` -> `Transcriber` -> `formatter` -> `inserter` pipeline in `_stop_and_process()`, and a pydantic `Settings` model with `_migrate_*` steps for safe upgrades. This change depends on `deploy-keycloak-auth` (the public device-flow client) and `add-cloud-transcription-api` (the endpoint this talks to) both being implemented in `speech_dashboard`.

## Goals / Non-Goals

**Goals:**
- Cloud mode as a drop-in alternative transcriber behind the existing pipeline, so `_stop_and_process()` doesn't need to know which mode it's in beyond picking which transcriber object to call.
- Zero behavior change for existing users who never touch cloud mode — matches the project's own stated priority of not regressing the platform-split, migration-safe settings patterns already in place.
- Clear, distinct error reporting for the three cloud-specific failure modes (auth, connectivity, quota), reusing the app's existing notify/error UI rather than inventing a new one.

**Non-Goals:**
- Any change to local transcription, hotkeys, wake word, or the recording pipeline itself — cloud mode only changes what happens between "audio captured" and "text ready to paste."
- A polished account-management UI (profile page, plan display inside the app) — sign-in/sign-out from the tray menu and simple notifications are enough for this change; a fuller account UI is the dashboard's job, not the desktop app's.
- Automatic fallback from cloud mode to local transcription on cloud failure — a user who opted into cloud mode gets a clear error, not a silent switch to a different (and possibly slower or unwanted) local model.

## Decisions

**`CloudTranscriber` implements the same interface as `Transcriber`** (`transcribe(audio_path: Path, language_mode: str) -> TranscriptionResult`), so `AppController` only needs one branch point (which transcriber instance to hold) rather than duplicating the pipeline. Mirrors the project's own existing pattern of platform-specific implementations behind a shared call shape (e.g. `recorder.py` vs `recorder_mac.py`).

**Tokens are stored in the existing settings JSON file, not the OS keyring.** speech-app already persists all configuration (including things like custom vocabulary) in a plain JSON settings file under the platform app-data dir; adding a keyring dependency (and its platform-specific quirks — Keychain, Secret Service, Credential Manager) for this change is more than the current threat model calls for, since the app already assumes the local machine/user account is the trust boundary. This is a known trade-off, not an oversight: a stolen settings file exposes a refresh token, same as it already exposes an OpenAI API key when LLM cleanup is configured. Revisit if this project later wants a stronger threat model for stored credentials.

**Device Authorization Grant, not Authorization Code + local redirect server.** Matches the earlier user decision this design.md's ecosystem context already settled: no embedded browser, no loopback HTTP server to manage, just polling a token endpoint — simplest correct option for a Tk tray app.

**No automatic retry loop inside the pipeline for a not-yet-approved device code.** The tray shows the code/URL and the app polls in a background thread at the interval Keycloak returns, exactly like a CLI tool would; dictation itself is not blocked waiting on sign-in — a user simply can't use cloud mode until sign-in completes.

**Quota-exceeded is detected from the cloud API's response (a specific status/error body from `add-cloud-transcription-api`), not pre-checked client-side.** speech-app doesn't need its own copy of quota logic; it just needs to recognize "quota exceeded" in the API's error response and show the right message. This keeps quota as a single source of truth on the backend.

## Risks / Trade-offs

- [Plaintext token storage in the settings file] → Accepted per Decisions above; consistent with the app's existing handling of the OpenAI API key, and scoped to the same local-machine trust boundary.
- [A user on a flaky connection in cloud mode gets more failures than local mode ever produced] → Accepted; distinct, clear error messaging (per spec) is the mitigation, not hiding the trade-off by silently falling back to local.
- [Device flow requires the user to have Speech's dashboard/browser sign-in experience finished (`add-dashboard-ui` or at least Keycloak's own login page) to actually complete the flow] → Keycloak's own hosted login page is sufficient for this change even before the dashboard exists (as already proven manually against `deploy-keycloak-auth`); the dashboard is not a hard dependency for this change to function, only for a nicer experience later.

## Migration Plan

Additive to `Settings`: new fields default to disabled/empty, with a `_migrate_*` step (per the project's own convention) ensuring old settings files load without the new fields present. No changes to existing local-mode behavior. Rollback is disabling/removing the tray menu entry and ignoring the new settings fields; no destructive change to revert.
