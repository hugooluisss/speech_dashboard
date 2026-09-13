## Purpose

Ensures every piece of visitor-facing copy on the landing page and dashboard has both an English and a Spanish version, so the language-preference mechanism always has real content to show in either language.

## ADDED Requirements

### Requirement: Landing page is fully translated
The system SHALL provide a Spanish version of every piece of landing page copy that has an English version (hero, features, pricing, calls to action), with no landing page text left untranslated.

#### Scenario: Landing page in Spanish has no English leftovers
- **WHEN** the landing page renders in Spanish
- **THEN** every visible text element (hero, features, pricing, CTAs) is in Spanish, with none left in English

### Requirement: Dashboard is fully translated
The system SHALL provide a Spanish version of every dashboard UI string (navigation, plan/usage labels, billing actions, admin table headers), with no dashboard text left untranslated.

#### Scenario: Dashboard in Spanish has no English leftovers
- **WHEN** the user dashboard or admin dashboard renders in Spanish
- **THEN** every visible UI string is in Spanish, with none left in English

### Requirement: Dynamic values are not mistranslated
The system SHALL translate UI labels and static copy, while leaving user-specific dynamic values (usernames, plan display names sourced from the plan catalog, numeric usage figures) unchanged regardless of language.

#### Scenario: Username unaffected by language
- **WHEN** a page renders in either language
- **THEN** the visitor's own username displays exactly as stored, not translated or altered
