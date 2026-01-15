#!/bin/bash
# Ultimate Statusline for Claude Code
# Combines the best features from ccstatusline, claude-powerline, and more
#
# Usage: This script reads JSON from stdin (provided by Claude Code)
#        and outputs a formatted statusline string
#
# Configuration:
#   - User config: ~/.claude/statusline-config.json
#   - Theme: ~/.claude/statusline-theme.json or built-in themes
#
# Environment variables:
#   - CLAUDE_STATUSLINE_CONFIG: Path to config file
#   - CLAUDE_STATUSLINE_THEME: Path to theme file

set -eo pipefail

# Get script directory and load libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/colors.sh"
source "$SCRIPT_DIR/lib/config.sh"
source "$SCRIPT_DIR/lib/widgets.sh"

# Read JSON input from stdin
INPUT=$(cat)

# Validate input
if [[ -z "$INPUT" ]] || ! echo "$INPUT" | jq empty 2>/dev/null; then
  # Return a minimal statusline if no valid input
  echo "Ultimate Statusline"
  exit 0
fi

# Load configuration
CONFIG=$(load_config)
THEME=$(load_theme)

# Get layout
LAYOUT=$(echo "$CONFIG" | jq -c '.layout // [["model_name"]]')

# Render each line
LINE_COUNT=$(echo "$LAYOUT" | jq 'length')
OUTPUT=""

for ((line=0; line<LINE_COUNT; line++)); do
  WIDGETS=$(echo "$LAYOUT" | jq -c ".[$line]")
  RENDERED=$(render_line "$WIDGETS" "$INPUT")

  if [[ -n "$RENDERED" ]]; then
    if [[ -n "$OUTPUT" ]]; then
      OUTPUT+=$'\n'
    fi
    OUTPUT+="$RENDERED"
  fi
done

# Output the final statusline (use printf for proper newline handling)
printf '%s\n' "$OUTPUT"
