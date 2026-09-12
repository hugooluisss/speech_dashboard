## Context

See proposal.md - Why. Builds on `add-dashboard-backend-base` (authenticated requests, layered structure) and `add-usage-quota-tracking` (the quota check/record operations). speech-app's `src/winwhisper/transcriber.py` (in the sibling `speech-app` repo) is the reference implementation for faster-whisper usage, device fallback, and result shape — this change adapts that approach for a server process, not a desktop session.

## Goals / Non-Goals

**Goals:**
- A working audio-in/text-out endpoint whose quota enforcement can't be bypassed by calling it directly (the check happens server-side, not trusted from the client).
- Model loaded once per backend process and reused across requests, since loading a Whisper model is the expensive part.
- Correct usage accounting even when transcription fails partway through.

**Non-Goals:**
- Wake-word detection, hotkey handling, clipboard/paste behavior, or any other speech-app desktop concern — this is a plain request/response transcription endpoint.
- Streaming/partial transcription results — the endpoint returns a complete result after the full audio is processed, matching speech-app's own current behavior (no streaming there either).
- Multi-model support (different Whisper model sizes per plan tier) — one model size for all cloud requests initially; the model size is an operational choice, not a per-plan feature, unless a later change asks for it.
- GPU autoscaling/multi-worker inference pooling — a single shared model instance with a lock around inference is the starting point; revisit only if latency/throughput under real load requires it.

## Decisions

**Adapt, don't share, the transcription logic between speech-app and this backend.** The two are independently packaged and deployed (a desktop app vs. a server), and speech-app's `Transcriber` includes desktop-specific concerns (mid-inference CPU fallback logged as a user-facing tray notification via `on_device_fallback`, hotwords from user-configured vocabulary settings) that don't apply the same way server-side. Copying and trimming the core model-loading/fallback pattern (~150 lines) into the backend is simpler than introducing a shared internal package across two repos for this amount of code. Revisit if the two implementations drift enough to cause real bugs from duplication.

**One shared `WhisperModel` instance per backend process, loaded lazily on first request, guarded by a lock for both loading and inference.** Mirrors speech-app's own lazy-load-with-lock pattern. A lock around inference (not just loading) means concurrent requests queue rather than run in parallel on one model instance — accepted as a correctness-first starting point; CTranslate2/faster-whisper model instances are not documented as safe for concurrent `.transcribe()` calls from multiple threads. Alternative considered: a pool of model instances for parallelism — deferred as premature until real concurrent load is observed.

**Word count for quota purposes is a simple whitespace split of the transcription result text.** Matches the everyday meaning of "word" well enough for a quota (not a linguistic word-boundary algorithm), is trivial to implement correctly, and is the same denominator the user will intuitively expect when told "N words used."

**Quota check and usage recording are two separate calls into `add-usage-quota-tracking`'s service** (`has_remaining_quota` before, `record_usage` after) rather than this change reimplementing quota logic. This endpoint is a consumer of that capability, not a second source of truth for it.

**Uploaded audio is written to a temporary file for the duration of the request and removed in a `finally`-equivalent cleanup, whether transcription succeeds or fails.** Matches speech-app's own "temporary WAV files are deleted after transcription" privacy stance and avoids ever needing a cleanup job for stray files.

## Risks / Trade-offs

- [A single shared model instance with a global inference lock limits throughput under concurrent load] → Accepted as the simplest correct starting point; noted as the first place to optimize (worker pool, batching) if usage grows enough to matter.
- [Word-count-by-whitespace-split slightly under/overcounts compared to a "true" linguistic word count for some languages] → Accepted; consistent and simple beats linguistically precise for a usage cap, and this is the same rough approach any reasonable implementation would take without deep NLP tooling.
- [Duplicating transcription logic between speech-app and the backend risks the two drifting apart over time] → Accepted for now (see Decisions); flagged as a spot to watch, not solved here.

## Migration Plan

Additive: new endpoint, new dependency (`faster-whisper`), no changes to existing schemas or endpoints. Nothing to migrate.
