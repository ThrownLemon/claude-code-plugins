#!/bin/bash
# Ultimate Statusline Installer
# Sets up the statusline for Claude Code

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Paths
USER_CONFIG="$HOME/.claude/statusline-config.json"
DEFAULT_CONFIG="$PLUGIN_ROOT/config/default-config.json"
SETTINGS_FILE="$HOME/.claude/settings.json"
STATUSLINE_SCRIPT="$PLUGIN_ROOT/scripts/statusline.sh"

# Parse arguments
THEME="${1:-default}"

echo -e "${BLUE}=== Ultimate Statusline Installer ===${NC}"
echo ""

# Step 1: Check dependencies
echo -e "${BLUE}Checking dependencies...${NC}"

# Check for jq
if ! command -v jq &>/dev/null; then
  echo -e "${RED}ERROR: jq is required but not installed${NC}"
  echo "Install with:"
  echo "  macOS: brew install jq"
  echo "  Linux: apt install jq"
  echo "  Windows: choco install jq"
  exit 1
fi
echo -e "${GREEN}✓ jq found${NC}"

# Note: bc is no longer required - using awk for calculations

# Check for ccusage (optional)
if command -v ccusage &>/dev/null; then
  echo -e "${GREEN}✓ ccusage found (daily/weekly/monthly costs available)${NC}"
else
  echo -e "${YELLOW}⚠ ccusage not found (optional: npm install -g ccusage)${NC}"
fi

echo ""

# Step 2: Create user configuration
echo -e "${BLUE}Setting up configuration...${NC}"

mkdir -p "$HOME/.claude"

# Verify default config exists
if [[ ! -f "$DEFAULT_CONFIG" ]]; then
  echo -e "${RED}ERROR: Default config not found at $DEFAULT_CONFIG${NC}"
  exit 1
fi

if [[ -f "$USER_CONFIG" ]]; then
  echo -e "${YELLOW}User config exists at $USER_CONFIG${NC}"
  # Check if running in interactive mode (TTY available)
  if [[ -t 0 ]]; then
    read -p "Overwrite with defaults? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      cp "$DEFAULT_CONFIG" "$USER_CONFIG"
      echo -e "${GREEN}Configuration reset to defaults${NC}"
    else
      echo -e "${BLUE}Keeping existing configuration${NC}"
    fi
  else
    echo -e "${BLUE}Non-interactive mode: keeping existing configuration${NC}"
  fi
else
  cp "$DEFAULT_CONFIG" "$USER_CONFIG"
  echo -e "${GREEN}Created configuration at $USER_CONFIG${NC}"
fi

# Apply theme if specified
if [[ "$THEME" != "default" ]]; then
  if [[ -f "$PLUGIN_ROOT/themes/${THEME}.json" ]]; then
    if jq --arg theme "$THEME" '.theme = $theme' "$USER_CONFIG" > "$USER_CONFIG.tmp"; then
      mv "$USER_CONFIG.tmp" "$USER_CONFIG"
      echo -e "${GREEN}✓ Applied theme: $THEME${NC}"
    else
      rm -f "$USER_CONFIG.tmp"
      echo -e "${YELLOW}⚠ Failed to apply theme, using default${NC}"
    fi
  else
    echo -e "${YELLOW}⚠ Theme '$THEME' not found, using default${NC}"
  fi
fi

echo ""

# Step 3: Make scripts executable
echo -e "${BLUE}Making scripts executable...${NC}"
chmod +x "$STATUSLINE_SCRIPT"
chmod +x "$PLUGIN_ROOT/scripts/lib/"*.sh 2>/dev/null || true
echo -e "${GREEN}✓ Scripts are executable${NC}"

echo ""

# Step 4: Update Claude Code settings
echo -e "${BLUE}Updating Claude Code settings...${NC}"

if [[ -f "$SETTINGS_FILE" ]]; then
  # Check if statusLine already exists
  if jq -e '.statusLine' "$SETTINGS_FILE" &>/dev/null; then
    echo -e "${YELLOW}statusLine already configured in settings.json${NC}"
    # Check if running in interactive mode (TTY available)
    if [[ -t 0 ]]; then
      read -p "Update to use ultimate-statusline? [Y/n] " -n 1 -r
      echo
      if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        jq --arg script "$STATUSLINE_SCRIPT" '.statusLine = {"type": "command", "command": $script, "padding": 0}' "$SETTINGS_FILE" > "$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
        echo -e "${GREEN}Updated statusLine configuration${NC}"
      else
        echo -e "${BLUE}Keeping existing statusLine configuration${NC}"
      fi
    else
      # Non-interactive: update by default
      jq --arg script "$STATUSLINE_SCRIPT" '.statusLine = {"type": "command", "command": $script, "padding": 0}' "$SETTINGS_FILE" > "$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
      echo -e "${GREEN}Updated statusLine configuration${NC}"
    fi
  else
    jq --arg script "$STATUSLINE_SCRIPT" '.statusLine = {"type": "command", "command": $script, "padding": 0}' "$SETTINGS_FILE" > "$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
    echo -e "${GREEN}Added statusLine to settings.json${NC}"
  fi
else
  # Use jq to safely construct JSON (handles special chars in paths)
  jq -n --arg script "$STATUSLINE_SCRIPT" '{"statusLine": {"type": "command", "command": $script, "padding": 0}}' > "$SETTINGS_FILE"
  echo -e "${GREEN}Created settings.json with statusLine${NC}"
fi

echo ""

# Step 5: Test the statusline
echo -e "${BLUE}Testing statusline...${NC}"

TEST_INPUT='{"model":{"id":"claude-opus-4-5-20251101","display_name":"Opus 4.5"},"context_window":{"total_input_tokens":45000,"total_output_tokens":8000,"context_window_size":200000},"cost":{"total_cost_usd":2.34,"total_duration_ms":3600000},"workspace":{"current_dir":"'$HOME'/test-project"}}'

echo -e "${BLUE}Sample output:${NC}"
echo "$TEST_INPUT" | "$STATUSLINE_SCRIPT"

echo ""
echo -e "${GREEN}=== Installation Complete ===${NC}"
echo ""
echo "Next steps:"
echo "  1. Restart Claude Code to apply the new statusline"
echo "  2. Run /ultimate-statusline:config to customize widgets"
echo "  3. Run /ultimate-statusline:preview to test themes"
echo ""
echo "Available themes: default, gruvbox, nord, tokyo-night, rose-pine, powerline"
echo ""
