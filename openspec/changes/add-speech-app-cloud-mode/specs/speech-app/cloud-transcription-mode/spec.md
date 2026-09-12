## Purpose

Lets a speech-app user opt into an authenticated cloud transcription mode instead of local-only dictation, so their word usage counts toward a plan, while leaving today's fully local, no-account behavior as the unchanged default.

## ADDED Requirements

### Requirement: Cloud mode is opt-in and off by default
The system SHALL default to local transcription (today's behavior) for both new and existing installations, and SHALL only use cloud transcription when the user has explicitly enabled cloud mode and is signed in.

#### Scenario: Existing installation upgrades unaffected
- **WHEN** a user with an existing settings file upgrades to a version of speech-app that includes cloud mode
- **THEN** their dictation continues to run fully locally with no sign-in prompt, unless they explicitly enable cloud mode

#### Scenario: New installation defaults to local
- **WHEN** speech-app is installed fresh and run for the first time
- **THEN** dictation runs locally with no account required, matching current behavior

### Requirement: Sign-in uses OAuth2 Device Authorization Grant
The system SHALL authenticate the user for cloud mode using the OAuth2 Device Authorization Grant against the Speech realm's public device client, displaying the verification URL and user code for the user to complete in a browser.

#### Scenario: User signs in successfully
- **WHEN** a user starts sign-in from the tray menu and approves the device code in their browser
- **THEN** speech-app receives and stores an access token and refresh token, and cloud mode becomes usable

#### Scenario: User does not complete approval
- **WHEN** a user starts sign-in but does not approve the device code before it expires
- **THEN** speech-app reports that sign-in did not complete and cloud mode remains unusable

### Requirement: Access tokens are refreshed transparently
The system SHALL use the stored refresh token to obtain a new access token when the current one has expired, without requiring the user to repeat the device flow, as long as the refresh token itself remains valid.

#### Scenario: Expired access token is refreshed automatically
- **WHEN** a signed-in user starts a cloud dictation after their access token has expired but their refresh token is still valid
- **THEN** speech-app obtains a new access token automatically and the dictation proceeds without prompting the user to sign in again

#### Scenario: Expired refresh token requires re-authentication
- **WHEN** a signed-in user's refresh token has also expired or been revoked
- **THEN** speech-app reports that the user must sign in again and does not attempt cloud transcription until they do

### Requirement: Cloud dictation uses the cloud transcription API
The system SHALL send dictation audio to the cloud transcription API when cloud mode is enabled and the user is signed in, and SHALL use the resulting text the same way local transcription results are used (cleanup, paste at cursor).

#### Scenario: Cloud transcription result is pasted
- **WHEN** a signed-in user in cloud mode completes a dictation and the cloud API returns transcribed text
- **THEN** speech-app applies the same cleanup and paste behavior it uses for a local transcription result

### Requirement: Cloud-specific failures are distinguishable to the user
The system SHALL give the user a distinct, specific notification for each of: not signed in, cloud API unreachable, and word quota exceeded — rather than a single generic transcription-failed message.

#### Scenario: Quota exceeded is reported specifically
- **WHEN** a cloud dictation request is refused because the user's word quota is exhausted
- **THEN** speech-app notifies the user that their plan's word limit has been reached, distinct from a connectivity or authentication failure

#### Scenario: Unreachable API is reported specifically
- **WHEN** a cloud dictation request fails because the cloud API cannot be reached
- **THEN** speech-app notifies the user of a connectivity failure, distinct from a quota or authentication failure

### Requirement: Sign-out clears stored credentials
The system SHALL provide a way to sign out of cloud mode that clears stored tokens and returns dictation to local-only behavior.

#### Scenario: Signing out disables cloud mode
- **WHEN** a signed-in user signs out from the tray menu
- **THEN** speech-app discards its stored tokens and subsequent dictation runs locally until the user signs in again
