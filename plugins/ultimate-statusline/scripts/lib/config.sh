#!/bin/bash
# Configuration utilities for ultimate-statusline
# Handles loading and merging config files

_CONFIG_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "$_CONFIG_SCRIPT_DIR/../.." && pwd)"

# Default paths
DEFAULT_CONFIG="$PLUGIN_ROOT/config/default-config.json"
USER_CONFIG="${CLAUDE_STATUSLINE_CONFIG:-$HOME/.claude/statusline-config.json}"
USER_THEME="${CLAUDE_STATUSLINE_THEME:-$HOME/.claude/statusline-theme.json}"
THEMES_DIR="$PLUGIN_ROOT/themes"

# Cache for loaded config
_CONFIG_CACHE=""
_THEME_CACHE=""

# Load and merge configuration
# Returns merged JSON config
load_config() {
  if [[ -n "$_CONFIG_CACHE" ]]; then
    echo "$_CONFIG_CACHE"
    return
  fi

  local config=""

  # Start with default config
  if [[ -f "$DEFAULT_CONFIG" ]]; then
    config=$(cat "$DEFAULT_CONFIG")
  else
    # Minimal fallback
    config='{"layout":[["model_name"]],"widgets":{},"theme":"default"}'
  fi

  # Merge user config if exists
  if [[ -f "$USER_CONFIG" ]]; then
    local user_config=$(cat "$USER_CONFIG")
    # Deep merge using jq
    config=$(echo "$config" | jq --argjson user "$user_config" '
      def deep_merge(a; b):
        a as $a | b as $b |
        if ($a | type) == "object" and ($b | type) == "object" then
          ($a | keys) + ($b | keys) | unique |
          map(. as $k | {($k): deep_merge($a[$k]; $b[$k])}) |
          add
        elif $b == null then $a
        else $b
        end;
      deep_merge(.; $user)
    ')
  fi

  _CONFIG_CACHE="$config"
  echo "$config"
}

# Load theme
# Usage: load_theme [theme_name]
load_theme() {
  local theme_name="${1:-}"

  if [[ -n "$_THEME_CACHE" && -z "$theme_name" ]]; then
    echo "$_THEME_CACHE"
    return
  fi

  # Get theme name from config if not specified
  if [[ -z "$theme_name" ]]; then
    theme_name=$(load_config | jq -r '.theme // "default"')
  fi

  local theme=""
  local theme_file="$THEMES_DIR/${theme_name}.json"

  # Try theme file
  if [[ -f "$theme_file" ]]; then
    theme=$(cat "$theme_file")
  # Try user theme file
  elif [[ -f "$USER_THEME" ]]; then
    theme=$(cat "$USER_THEME")
  else
    # Default theme
    theme='{
      "name": "default",
      "colors": {
        "model": {"fg": "cyan", "bold": true},
        "git_clean": {"fg": "green"},
        "git_dirty": {"fg": "yellow"},
        "git_branch": {"fg": "magenta"},
        "context_low": {"fg": "green"},
        "context_mid": {"fg": "yellow"},
        "context_high": {"fg": "red"},
        "cost": {"fg": "magenta"},
        "time": {"fg": "blue"},
        "mcp_ok": {"fg": "green"},
        "mcp_error": {"fg": "red"},
        "separator": {"fg": "gray"},
        "directory": {"fg": "blue"}
      },
      "powerline": {
        "separator": "",
        "separator_thin": ""
      }
    }'
  fi

  _THEME_CACHE="$theme"
  echo "$theme"
}

# Get widget config
# Usage: get_widget_config "model_name"
get_widget_config() {
  local widget="$1"
  local config
  config=$(load_config)
  # Use --arg for safe variable interpolation
  echo "$config" | jq --arg w "$widget" '.widgets[$w] // {}'
}

# Check if widget is enabled
# Usage: is_widget_enabled "model_name"
is_widget_enabled() {
  local widget="$1"
  local enabled
  # Use --arg for safe variable interpolation
  enabled=$(load_config | jq -r --arg w "$widget" '.widgets[$w].enabled // true')
  [[ "$enabled" == "true" ]]
}

# Get layout
# Usage: get_layout
get_layout() {
  load_config | jq -r '.layout // [["model_name"]]'
}

# Get separator
# Usage: get_separator
get_separator() {
  local config=$(load_config)
  local powerline=$(echo "$config" | jq -r '.powerline // false')

  if [[ "$powerline" == "true" ]]; then
    echo "$config" | jq -r '.widgets.separator.powerline // ""'
  else
    echo "$config" | jq -r '.widgets.separator.char // " │ "'
  fi
}

# Clear config cache (useful for testing)
clear_config_cache() {
  _CONFIG_CACHE=""
  _THEME_CACHE=""
}
