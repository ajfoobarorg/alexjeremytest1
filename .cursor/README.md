# Cursor Rules

This directory contains configuration files for Cursor editor rules specific to this project.

## How Rules Are Assembled and Applied

### Rule Organization

- `settings.json` - The main configuration file that includes all rule files
- `rules/` - Directory containing individual rule files (one rule per file)

### How Rules Work

1. **Assembly**: The `settings.json` file is the master configuration file that Cursor reads first
2. **Inclusion**: The `include` array in `settings.json` tells Cursor which rule files to load
3. **Application**: Rules are automatically applied to matching files based on patterns
4. **Activation**: Cursor automatically detects and loads these rules when opening the project

### Activating Rules in Cursor

Cursor automatically loads rules from the `.cursor` directory at the project root. No additional steps are needed beyond:

1. Creating the `.cursor` directory
2. Adding a `settings.json` file with proper configuration
3. Creating rule files referenced in the `settings.json`

## Rule Format

All rules in this project use the Markdown (MDC) format, which includes:

- **Title and Description** - What the rule does
- **Purpose** - Why the rule exists
- **Configuration** - JSON configuration in a code block
- **Examples** - When applicable
- **Usage Notes** - Additional context about the rule

## Rule Files

### Python Rules

- `python-formatter.mdc` - Black formatter with 88 character line length and isort with Black compatibility
- `python-linter.mdc` - Ruff linting configuration
- `python-docstrings.mdc` - Required Google-style docstrings
- `python-imports.mdc` - Structured import ordering

### JavaScript/Svelte Rules

- `js-formatter.mdc` - Prettier formatting with consistent style settings
- `js-linter.mdc` - ESLint for code quality
- `svelte-structure.mdc` - Svelte component structure rules (script, style, template order)

## Adding New Rules

To add a new rule:

1. Create a new `.mdc` file in the `.cursor/rules/` directory
2. Include title, purpose, configuration (in JSON), examples, and usage notes
3. Add the new rule file to the "include" array in `settings.json`
4. Update this README with documentation about the new rule 