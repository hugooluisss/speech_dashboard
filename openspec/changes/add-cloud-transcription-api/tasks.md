## 1. Transcription engine

- [x] 1.1 Add `faster-whisper` as a backend dependency; verify it installs and imports cleanly in the backend's environment.
- [x] 1.2 Implement a `TranscriptionEngine` service (adapted from speech-app's `winwhisper/transcriber.py`): lazy-loaded shared `WhisperModel` instance, lock around load and inference, CPU fallback on device/compute-type failure; verify a unit test transcribes a short sample audio fixture and returns non-empty text (using the smallest model size to keep tests fast).

## 2. Quota-gated endpoint

- [x] 2.1 Implement the `/transcribe` controller: validates the token, calls `UsageService.has_remaining_quota`, rejects with no transcription attempted if false; verify a unit test with a mocked usage service confirms no transcription call happens when quota is exhausted.
- [x] 2.2 Wire successful-path transcription: save uploaded audio to a temp file, call `TranscriptionEngine`, count words in the result, call `UsageService.record_usage`, return the transcribed text; verify an integration test uploads a real short audio fixture and confirms both the response text and the recorded usage increase by the expected word count.
- [x] 2.3 Ensure temp audio cleanup happens on both success and failure paths; verify a unit test forces a transcription failure (e.g. corrupt audio fixture) and confirms the temp file no longer exists afterward and usage is not recorded.

## 3. Verification

- [ ] 3.1 Manually verify end-to-end: authenticate via the device flow (per `deploy-keycloak-auth`), upload a real short audio clip to `/transcribe`, confirm the returned text is correct and `/usage` (from `add-usage-quota-tracking`) reflects the new word count afterward.
- [ ] 3.2 Manually verify quota enforcement: reduce a test user's plan limit or pre-fill their usage near the limit, confirm a `/transcribe` request is refused once quota is exhausted.
