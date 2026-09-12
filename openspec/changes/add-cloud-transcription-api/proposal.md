## Why

Speech's cloud mode (the reason a user would ever hit a word quota at all) needs somewhere to actually send audio and get text back. This change adds that endpoint to the same backend that already tracks identity, plans, and quota, so the transcription request path can check and consume quota in the same place it does the work — instead of speech-app talking to a separate service that would have to re-derive plan/quota state.

## What Changes

- Add an authenticated endpoint that accepts an audio file upload and returns its transcription, backed by the same faster-whisper approach speech-app already uses locally (adapted for a server process: one shared model instance per backend process instead of per desktop session).
- Before transcribing, check the caller's remaining quota (`usage/quota-tracking`) and reject the request if they have none left, so the backend never does paid transcription work for a user who can't use the result.
- After a successful transcription, count the words in the result and record that usage against the caller's current period.
- Delete the uploaded audio file after transcription completes (or fails), matching speech-app's existing "no retained audio" privacy stance.
- Load the Whisper model once per backend process (lazily, on first request) rather than per request, since model loading is the dominant cost.

## Capabilities

### New Capabilities
- `transcription/cloud-endpoint`: An authenticated, quota-checked audio-to-text endpoint that transcribes uploaded audio and records the resulting word count as usage.

### Modified Capabilities
(none)

## Impact

- New: transcription controller/service in the backend, plus a transcription engine module adapted from speech-app's `winwhisper/transcriber.py` (model loading, device fallback) for a server context — not a shared package between the two repos in this change, to avoid coupling two independently deployed projects for what is currently ~150 lines of adapted logic.
- Depends on `add-usage-quota-tracking`'s quota-check operation and `add-dashboard-backend-base`'s authentication.
- `add-speech-app-cloud-mode` (a separate change to speech-app) will be the first real caller of this endpoint.
- New dependency: `faster-whisper` (and its model download/runtime requirements) added to the backend's dependencies, mirroring speech-app's existing usage of the same library.
