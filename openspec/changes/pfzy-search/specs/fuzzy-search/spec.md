# Fuzzy Search Specification

## ADDED Requirements

### Requirement: Fuzzy subsequence matching

The system SHALL support fuzzy matching where users can type non-consecutive characters to match items. Each character in the query MUST appear in the target string in order, but gaps are allowed between matched characters.

#### Scenario: Non-consecutive character matching

- **WHEN** user types "nfp" in search box
- **THEN** system matches "new float pane" (n matches 'n', f matches 'f', p matches 'p')

#### Scenario: Partial word matching

- **WHEN** user types "n p" in search box (with space)
- **THEN** system matches "new float pane" (space allows matching across word boundaries)

#### Scenario: Typo tolerance

- **WHEN** user types "flaot" in search box (typo)
- **THEN** system matches "new float pane" (f-l-a-o-t with gap finds float)

### Requirement: Match scoring and ranking

The system SHALL score each match and display results in descending score order. Higher scores indicate better matches based on: position of first match, consecutive matches, and word boundary bonuses.

#### Scenario: Score-based ordering

- **WHEN** user types "new" and results include "new file", "new pane", "renew"
- **THEN** results are sorted by match score with highest scores first

#### Scenario: Empty query shows all

- **WHEN** user clears search input
- **THEN** system displays all options sorted by group and title alphabetically

### Requirement: Match highlighting

The system SHALL highlight matched characters in the display. Matched characters MUST be visually distinct from non-matched characters using a different color.

#### Scenario: Highlight matched characters

- **WHEN** user types "nfp" and "new float pane" is in results
- **THEN** the characters 'n', 'f', 'p' are highlighted with a distinct color

#### Scenario: Title highlighting

- **WHEN** search matches within the title field
- **THEN** matched characters in title are highlighted

#### Scenario: Output highlighting

- **WHEN** search matches within the output field
- **THEN** matched characters in output are highlighted

### Requirement: Multi-field search

The system SHALL search across title, output, and group fields. The match score SHALL be calculated per field, and the highest score determines the item's ranking.

#### Scenario: Title match

- **WHEN** user types "pi" and item title is "pi session"
- **THEN** item is matched with title score

#### Scenario: Output match

- **WHEN** user types "zellij" and item output contains "zellij"
- **THEN** item is matched with output score

#### Scenario: Group match

- **WHEN** user types "zellij" and item group is "zellij"
- **THEN** item is matched with group score

### Requirement: Numeric quick select compatibility

The system SHALL preserve numeric quick select functionality. When the input consists only of digits, the system SHALL interpret it as an index for direct selection rather than a search query.

#### Scenario: Numeric selection

- **WHEN** user types "1" and presses Enter
- **THEN** first item is selected regardless of search results

#### Scenario: Multi-digit selection

- **WHEN** user types "12" and presses Enter
- **THEN** 12th item is selected (if exists)

### Requirement: Group filtering in resolving mode

The system SHALL support group filtering when resolving a `{{g|group_name}}` placeholder. The search SHALL be limited to items in the specified group.

#### Scenario: Group-filtered search

- **WHEN** system is in resolving_g mode for group "zellij"
- **THEN** search only includes items where group equals "zellij"

#### Scenario: Group selection with fuzzy search

- **WHEN** user types "new" in zellij group selection
- **THEN** only zellij items matching "new" are shown
