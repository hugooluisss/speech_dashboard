## Why

Everything built so far (Keycloak, the backend, billing, quota, the cloud transcription endpoint) has no real user until speech-app can actually log in and use it. This change is the desktop-side counterpart: speech-app gains an opt-in cloud mode that authenticates the user against Keycloak and sends dictation audio to the cloud transcription API instead of transcribing locally, while local mode (today's fully offline, no-account behavior) remains the default and keeps working unchanged.

**Cross-repo note:** this change's implementation target is the sibling `speech-app` repository (`../speech-app` relative to this `speech_dashboard` OpenSpec root), a Python/Tk desktop app — not `speech_dashboard` itself. OpenSpec planning lives here because the platform-wide plan is being tracked in one place, but an implementing agent must operate on the `speech-app` checkout.

## What Changes

- Add a `cloud_mode_enabled` setting (default `false`) and cloud-related settings (API base URL, stored tokens) to speech-app's `Settings` model, with a `_migrate_*` step so existing installed settings files load cleanly with cloud mode off.
- Add a tray menu option to enable cloud mode and sign in, which starts the OAuth2 Device Authorization Grant flow against the Speech realm's public device client: request a device code, show the user the verification URL/code (via the existing tray notification mechanism), poll for a token, and store the resulting tokens.
- Add token refresh handling so a signed-in user doesn't have to re-authenticate every time the access token expires.
- Add a `CloudTranscriber` implementing the same interface as the existing local `Transcriber` (`transcribe(audio_path, language_mode) -> TranscriptionResult`), so `AppController`'s dictation pipeline (`_stop_and_process` in `main.py`) can use either one based on `cloud_mode_enabled` without changing the rest of the pipeline.
- Surface cloud-specific failures distinctly from existing transcription errors: not signed in, network/API unreachable, and quota exceeded each get a clear, distinct user-facing notification (reusing the existing error/notify pathway) rather than a generic failure.
- Add a way to sign out (clears stored tokens, returns to local mode).

## Capabilities

### New Capabilities
- `speech-app/cloud-transcription-mode`: An opt-in mode where speech-app authenticates via Keycloak Device Authorization Grant and sends dictation audio to the cloud transcription API instead of transcribing locally, with distinct handling for auth, connectivity, and quota failures.

### Modified Capabilities
(none — no existing OpenSpec-tracked capabilities for speech-app; local dictation behavior is unchanged and not being altered by this change)

## Impact

- Modifies `speech-app`: `src/winwhisper/config.py` (new settings + migration), `src/winwhisper/main.py` (`AppController` picks local vs. cloud transcriber), `src/winwhisper/tray.py` (sign-in/sign-out menu items), plus a new `cloud_auth.py` (device flow + token storage/refresh) and `cloud_transcriber.py` (the `CloudTranscriber`).
- Depends on `deploy-keycloak-auth`'s public device-flow client contract and `add-cloud-transcription-api`'s endpoint contract (request/response shape, error codes for auth/quota failures).
- Local-only, no-account dictation remains the default and is not changed by this work — cloud mode is purely additive and opt-in.
