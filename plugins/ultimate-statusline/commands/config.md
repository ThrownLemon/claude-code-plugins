---
description: Configure ultimate-statusline settings, widgets, and themes
arguments:
  - name: action
    description: Action to perform (show, set, reset, themes)
    required: false
  - name: key
    description: Configuration key to modify (e.g., theme, widgets.model_name.enabled)
    required: false
  - name: value
    description: Value to set
    required: false
---

# Ultimate Statusline Configuration

Manage your statusline configuration, enable/disable widgets, and switch themes.

## Actions

### Show Current Configuration (default)

```bash
/ultimate-statusline:config
/ultimate-statusline:config show
```

### Set a Configuration Value

```bash
/ultimate-statusline:config set theme gruvbox
/ultimate-statusline:config set widgets.burn_rate.enabled true
/ultimate-statusline:config set widgets.context_percent.bar_length 15
```

### Reset to Defaults

```bash
/ultimate-statusline:config reset
```

### List Available Themes

```bash
/ultimate-statusline:config themes
```

## Execution

Based on the action argument:

**show** (or no action):
1. Read the user config from `~/.claude/statusline-config.json`
2. Display the current configuration in a readable format
3. Highlight which widgets are enabled/disabled

**set**:
1. Read the current config
2. Update the specified key with the new value
3. Write the updated config back
4. Display the change

**reset**:
1. Copy the default config from the plugin to user config location
2. Confirm the reset

**themes**:
1. List all available themes from `${CLAUDE_PLUGIN_ROOT}/themes/`
2. Show which theme is currently active

## Configuration File Location

- User config: `~/.claude/statusline-config.json`
- Default config: `${CLAUDE_PLUGIN_ROOT}/config/default-config.json`
- Theme files: `${CLAUDE_PLUGIN_ROOT}/themes/`

## Example Widget Configuration

```json
{
  "widgets": {
    "context_percent": {
      "enabled": true,
      "show_bar": true,
      "bar_length": 10,
      "thresholds": {"low": 50, "mid": 75, "high": 90}
    }
  }
}
```
