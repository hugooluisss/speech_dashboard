## Purpose

Determines which language (English or Spanish) a visitor sees on the landing page and dashboard, from their browser's language and an explicit override, without requiring a URL change.

## ADDED Requirements

### Requirement: Language resolves from browser preference by default
The system SHALL render the landing page and dashboard in Spanish when the visitor's browser reports Spanish as a preferred language (via the `Accept-Language` header) and no manual override is set, and in English otherwise.

#### Scenario: Spanish browser gets Spanish content
- **WHEN** a visitor with no language override cookie requests a page with `Accept-Language` indicating Spanish
- **THEN** the page renders in Spanish

#### Scenario: Unsupported browser language falls back to English
- **WHEN** a visitor with no language override cookie requests a page with `Accept-Language` indicating a language that is neither English nor Spanish
- **THEN** the page renders in English

### Requirement: Visitor can override the detected language
The system SHALL provide a visible control that lets a visitor switch between English and Spanish, and SHALL remember that choice for subsequent requests regardless of their browser's language.

#### Scenario: Visitor switches language
- **WHEN** a visitor selects Spanish from the language switch while viewing an English page
- **THEN** the page re-renders in Spanish and subsequent page loads also render in Spanish

#### Scenario: Override persists across visits
- **WHEN** a visitor who previously chose a language returns later with the same browser
- **THEN** the page renders in their previously chosen language, even if their browser's language preference would otherwise resolve differently

### Requirement: No URL change for language
The system SHALL serve the same URL for a given page regardless of which language is being displayed; language SHALL NOT be encoded as a URL path prefix or query parameter.

#### Scenario: Same URL in both languages
- **WHEN** the same page is requested by a Spanish-preferring visitor and an English-preferring visitor
- **THEN** both requests use the identical URL, differing only in the rendered language
