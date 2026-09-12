## Purpose

Provides the server-side transcription capability that gives Speech's cloud mode something to send audio to, enforcing each user's word quota at the point of use rather than trusting the caller to self-limit.

## ADDED Requirements

### Requirement: Authenticated audio transcription
The system SHALL provide an authenticated endpoint that accepts an uploaded audio file and returns its transcribed text.

#### Scenario: Successful transcription
- **WHEN** an authenticated user with remaining quota uploads a valid audio file
- **THEN** the system returns the transcribed text for that audio

#### Scenario: Unauthenticated request is rejected
- **WHEN** a request to the transcription endpoint has no valid access token
- **THEN** the system rejects the request without transcribing any audio

### Requirement: Quota is checked before transcription
The system SHALL check the caller's remaining word quota before performing transcription, and SHALL refuse the request without transcribing if the caller has no remaining quota.

#### Scenario: Request refused when quota is exhausted
- **WHEN** an authenticated user with zero remaining quota requests a transcription
- **THEN** the system refuses the request and does not run the audio through the transcription model

#### Scenario: Request proceeds when quota remains
- **WHEN** an authenticated user with remaining quota requests a transcription
- **THEN** the system proceeds to transcribe the uploaded audio

### Requirement: Successful transcription records word usage
The system SHALL count the words in a successful transcription's result and record that count as usage against the caller's current billing period.

#### Scenario: Usage increases after transcription
- **WHEN** a transcription completes successfully and its result contains N words
- **THEN** the caller's recorded usage for the current period increases by N

#### Scenario: Failed transcription does not record usage
- **WHEN** a transcription attempt fails (e.g. invalid audio, model error) and produces no result
- **THEN** the caller's recorded usage is not changed

### Requirement: Uploaded audio is not retained
The system SHALL delete an uploaded audio file after transcription completes or fails, and SHALL NOT persist audio content beyond the request that submitted it.

#### Scenario: Audio is removed after a successful transcription
- **WHEN** a transcription request completes successfully
- **THEN** the uploaded audio file no longer exists on the server afterward

#### Scenario: Audio is removed after a failed transcription
- **WHEN** a transcription request fails
- **THEN** the uploaded audio file no longer exists on the server afterward
