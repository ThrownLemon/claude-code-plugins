---
description: Install ultimate-statusline and configure Claude Code to use it
arguments:
  - name: theme
    description: Initial theme to use (default, gruvbox, nord, tokyo-night, rose-pine, powerline)
    required: false
---

# Install Ultimate Statusline

Set up ultimate-statusline as your Claude Code statusline.

## What This Does

1. Creates user configuration at `~/.claude/statusline-config.json`
2. Updates `~/.claude/settings.json` to use the statusline script
3. Verifies dependencies (jq)

## Execution

### Step 1: Check Dependencies

```bash
# Check for jq
if ! command -v jq &>/dev/null; then
  echo "Warning: jq is required for ultimate-statusline"
  echo "Install with: brew install jq (macOS) or apt install jq (Linux)"
fi

# Check for bc (usually pre-installed)
if ! command -v bc &>/dev/null; then
  echo "Warning: bc is recommended for calculations"
fi

# Optional: Check for ccusage
if command -v ccusage &>/dev/null; then
  echo "ccusage found - daily/weekly/monthly cost widgets available"
else
  echo "ccusage not found - install with: npm install -g ccusage"
fi
```

### Step 2: Create User Configuration

```bash
# Copy default config if user config doesn't exist
USER_CONFIG="$HOME/.claude/statusline-config.json"
DEFAULT_CONFIG="${CLAUDE_PLUGIN_ROOT}/config/default-config.json"

if [[ ! -f "$USER_CONFIG" ]]; then
  mkdir -p "$HOME/.claude"
  cp "$DEFAULT_CONFIG" "$USER_CONFIG"
  echo "Created configuration at $USER_CONFIG"
fi

# Apply theme if specified
if [[ -n "$THEME" ]]; then
  jq ".theme = \"$THEME\"" "$USER_CONFIG" > "$USER_CONFIG.tmp" && mv "$USER_CONFIG.tmp" "$USER_CONFIG"
  echo "Applied theme: $THEME"
fi
```

### Step 3: Update Claude Code Settings

```bash
SETTINGS_FILE="$HOME/.claude/settings.json"
STATUSLINE_SCRIPT="${CLAUDE_PLUGIN_ROOT}/scripts/statusline.sh"

# Make script executable
chmod +x "$STATUSLINE_SCRIPT"

# Update or create settings.json
if [[ -f "$SETTINGS_FILE" ]]; then
  # Merge with existing settings
  jq --arg script "$STATUSLINE_SCRIPT" '.statusLine = {"type": "command", "command": $script, "padding": 0}' "$SETTINGS_FILE" > "$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
else
  # Create new settings file
  mkdir -p "$HOME/.claude"
  echo "{\"statusLine\": {\"type\": \"command\", \"command\": \"$STATUSLINE_SCRIPT\", \"padding\": 0}}" | jq . > "$SETTINGS_FILE"
fi

echo "Updated Claude Code settings"
```

### Step 4: Verify Installation

```bash
# Test the statusline script
echo '{"model":{"display_name":"Test"},"context_window":{"total_input_tokens":1000,"total_output_tokens":500,"context_window_size":200000},"cost":{"total_cost_usd":0.5}}' | "$STATUSLINE_SCRIPT"
```

## Post-Installation

1. **Restart Claude Code** to apply the new statusline
2. Run `/ultimate-statusline:config` to customize widgets
3. Run `/ultimate-statusline:preview` to test different themes

## Uninstall

To remove the statusline:

```bash
# Remove from settings
jq 'del(.statusLine)' ~/.claude/settings.json > ~/.claude/settings.json.tmp && mv ~/.claude/settings.json.tmp ~/.claude/settings.json

# Optionally remove user config
rm ~/.claude/statusline-config.json
```
