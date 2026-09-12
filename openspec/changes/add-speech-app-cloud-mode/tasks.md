## 1. Settings

- [ ] 1.1 Add `cloud_mode_enabled`, `cloud_api_base_url`, `cloud_access_token`, `cloud_refresh_token` (names indicative) fields to `Settings` in `config.py`, all optional/defaulted so old settings files remain valid; verify existing settings fixtures/tests still load unchanged.
- [ ] 1.2 Add a `_migrate_*` step for these new fields per the project's migration convention; verify a test loads a pre-change settings JSON fixture and confirms the new fields come back at their defaults with no error.

## 2. Device authorization sign-in

- [ ] 2.1 Implement `cloud_auth.py`: request a device code from the Keycloak realm's public device client, expose the verification URL/user code, and poll the token endpoint at the returned interval until success, expiry, or denial; verify unit tests cover successful polling (mocked HTTP), expiry, and denial.
- [ ] 2.2 Wire a tray menu "Sign in for cloud mode" action that starts the device flow on a background thread and shows the verification URL/code via the existing notification mechanism; verify manually that starting sign-in shows a code and does not block the tray UI.
- [ ] 2.3 On successful sign-in, store the access and refresh tokens in settings and enable `cloud_mode_enabled`; verify a test confirms settings are persisted after a mocked successful poll.
- [ ] 2.4 Implement token refresh: before a cloud request, if the access token is expired (or the API returns an auth error), use the refresh token to get a new one and retry once; verify unit tests cover a successful refresh-and-retry and a refresh failure that surfaces a re-authentication error.
- [ ] 2.5 Add a tray "Sign out" action that clears stored tokens and disables `cloud_mode_enabled`; verify a test confirms tokens are cleared from settings after sign-out.

## 3. Cloud transcriber

- [ ] 3.1 Implement `CloudTranscriber` matching `Transcriber`'s `transcribe(audio_path, language_mode) -> TranscriptionResult` interface: uploads the audio file to `add-cloud-transcription-api`'s endpoint with the current access token, parses the response into a `TranscriptionResult`; verify a unit test with a mocked HTTP client returns the expected result shape.
- [ ] 3.2 Wire `AppController` to hold either the local `Transcriber` or `CloudTranscriber` based on `cloud_mode_enabled` and sign-in status, with no other change to `_stop_and_process()`'s pipeline; verify a unit test confirms the correct transcriber is selected for each combination of cloud-mode-enabled/signed-in state.

## 4. Error handling

- [ ] 4.1 Detect and surface "not signed in" distinctly (cloud mode on, no valid tokens) before attempting a request; verify a unit test confirms this path never calls the network.
- [ ] 4.2 Detect and surface "cloud API unreachable" (network/connection error) distinctly from other failures; verify a unit test simulates a connection error and confirms the specific notification path is used.
- [ ] 4.3 Detect and surface "quota exceeded" from the cloud API's specific error response distinctly from other failures; verify a unit test simulates that error response and confirms the specific notification path is used.

## 5. Verification

- [ ] 5.1 Manually verify end-to-end against a running `speech_dashboard` backend and Keycloak: enable cloud mode, sign in via the device flow, dictate, confirm the transcription is pasted and usage increases on the backend.
- [ ] 5.2 Manually verify quota-exceeded behavior end-to-end: exhaust a test user's quota on the backend, attempt a cloud dictation, confirm the specific quota notification appears and no text is pasted.
