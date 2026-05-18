# Placeholder V2 Specification

## ADDED Requirements

### Requirement: Placeholder Syntax Format

The placeholder SHALL use `{{intent[:prompt][|default]}}` syntax with the following parts:

- Intent (MUST be required): single character, `g` for group selection, `i` for input
- Prompt (optional): text after colon, SHALL be displayed in UI
- Default value (optional): text after pipe, SHALL be used as default for input mode

#### Scenario: g mode basic syntax

- **WHEN** placeholder is `{{g|zellij}}`
- **THEN** intent is `g`, group name is `zellij`, no prompt

#### Scenario: i mode with prompt

- **WHEN** placeholder is `{{i:Please enter port}}`
- **THEN** intent is `i`, prompt is "Please enter port", no default

#### Scenario: i mode with default

- **WHEN** placeholder is `{{i:Please enter port|8080}}`
- **THEN** intent is `i`, prompt is "Please enter port", default is "8080"

#### Scenario: g mode with prompt

- **WHEN** placeholder is `{{g:Select container|zellij}}`
- **THEN** intent is `g`, prompt is "Select container", group name is `zellij`

### Requirement: g Mode - Group Selection

When intent is `g`, the system SHALL display all options of the corresponding group for user selection.

#### Scenario: Show group options list

- **WHEN** parsing `{{g|zellij}}`
- **THEN** display all options under zellij group (title + output), highlight first item
- **AND** input box shows prompt "Please select" (default prompt)

#### Scenario: Custom group prompt

- **WHEN** parsing `{{g:Select container|zellij}}`
- **THEN** input box shows prompt "Select container"

#### Scenario: Replace and continue after selection

- **WHEN** user selects an option and presses enter
- **THEN** replace placeholder with selected item's output
- **AND** continue checking for next placeholder in remaining string

#### Scenario: Error when group not found

- **WHEN** placeholder specifies non-existent group
- **THEN** print error message to stderr and exit with code 1

### Requirement: i Mode - Input

When intent is `i`, the system SHALL show an input dialog prompting user to enter content manually.

#### Scenario: Show input box

- **WHEN** parsing `{{i:Please enter port}}`
- **THEN** clear options list
- **AND** display input box in original position with prompt "Please enter port"

#### Scenario: With default value

- **WHEN** parsing `{{i:Please enter port|8080}}`
- **THEN** input box pre-fills "8080"

#### Scenario: User enters content and presses enter

- **WHEN** user enters "9000" in input box and presses enter
- **THEN** replace placeholder with "9000"
- **AND** continue checking for next placeholder in remaining string

#### Scenario: Empty content on enter causes error

- **WHEN** user presses enter with no content in input box
- **THEN** print error message to stderr and exit with code 1

### Requirement: Placeholder Parsing Flow

The system SHALL parse placeholders in output string sequentially, and output final result after all replacements.

#### Scenario: Multiple nested placeholders

- **WHEN** output is "docker run -p {{port:Port|8080}} -v {{path:Path|/data}}"
- **THEN** process first placeholder, then second
- **AND** final output is like "docker run -p 9000 -v /opt"

#### Scenario: Max nesting depth check

- **WHEN** nesting depth reaches 3
- **THEN** print error message to stderr and exit with code 1

## MODIFIED Requirements

### Requirement: Placeholder Detection

The system SHALL parse placeholders according to the new syntax format.

**Original**: `{{group_name}}` syntax, only supports group selection

**New**: `{{intent[:prompt][|default]}}` syntax, SHALL support both group selection and input modes, SHALL NOT support old syntax

#### Scenario: Old syntax handling

- **WHEN** config uses old syntax `{{old_group}}`
- **THEN** system shows error, prompting to migrate to new syntax `{{g|old_group}}`
