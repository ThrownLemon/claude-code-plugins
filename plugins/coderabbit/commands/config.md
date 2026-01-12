---
description: Configure CodeRabbit plugin preferences
---

# CodeRabbit Plugin Configuration

View and modify CodeRabbit plugin settings.

## Configuration Options

### Review Defaults

| Setting | Description | Options |
|---------|-------------|---------|
| Default type | What changes to review | `all`, `uncommitted`, `committed` |
| Default base | Base branch for comparison | `main`, `master`, `develop`, auto |

### Automation Settings

| Setting | Description | Options |
|---------|-------------|---------|
| Post-edit hints | Show review reminder after file edits | `enabled`, `disabled` |
| Review logging | Log completed reviews for analytics | `enabled`, `disabled` |

### Display Preferences

| Setting | Description | Options |
|---------|-------------|---------|
| Severity colors | Color-code issues by severity | `enabled`, `disabled` |
| Compact output | Condensed issue display | `enabled`, `disabled` |

## Current Configuration

To view current settings, I'll check:

1. Plugin hooks configuration in `hooks/hooks.json`
2. Any local overrides in `.claude/settings.json`

## Modifying Settings

Settings can be modified by:

1. **Editing hooks.json** - Enable/disable automation hooks
2. **Local settings** - Project-specific overrides
3. **Environment variables** - Runtime configuration

## Available Actions

1. **View current configuration** - Show all current settings
2. **Reset to defaults** - Restore default configuration
3. **Enable/disable hooks** - Toggle automation features
4. **Set default review type** - Change default `--type` value
5. **Set default base branch** - Change default `--base` value

## Steps

1. Show current plugin configuration status
2. Ask user what they want to configure
3. Provide guidance on modifying settings
4. For hook changes, explain that hooks.json needs to be edited
5. Remind user to restart Claude Code for changes to take effect
