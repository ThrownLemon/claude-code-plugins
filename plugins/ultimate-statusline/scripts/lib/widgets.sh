#!/bin/bash
# Widget implementations for ultimate-statusline
# Each widget is a function that takes JSON input and returns formatted output

_WIDGETS_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$_WIDGETS_SCRIPT_DIR/colors.sh"
source "$_WIDGETS_SCRIPT_DIR/config.sh"

# ============================================================================
# MODEL WIDGETS
# ============================================================================

# Model emoji based on model name
widget_model_emoji() {
  local input="$1"
  local config
  config=$(get_widget_config "model_emoji")
  local model
  model=$(echo "$input" | jq -r '.model.id // .model.display_name // ""' | tr '[:upper:]' '[:lower:]')

  local emoji=""
  if [[ "$model" == *"opus"* ]]; then
    emoji=$(echo "$config" | jq -r '.icons.opus // "🧠"')
  elif [[ "$model" == *"haiku"* ]]; then
    emoji=$(echo "$config" | jq -r '.icons.haiku // "⚡"')
  elif [[ "$model" == *"sonnet"* ]]; then
    emoji=$(echo "$config" | jq -r '.icons.sonnet // "🎵"')
  else
    emoji="🤖"
  fi

  printf '%s' "$emoji"
}

# Model name (short or full)
widget_model_name() {
  local input="$1"
  local config
  config=$(get_widget_config "model_name")
  local short
  short=$(echo "$config" | jq -r '.short // true')

  local name
  name=$(echo "$input" | jq -r '.model.display_name // .model.id // "Unknown"')

  if [[ "$short" == "true" ]]; then
    # Extract just the model family name (case-insensitive)
    local name_lower
    name_lower=$(echo "$name" | tr '[:upper:]' '[:lower:]')
    if [[ "$name_lower" == *"opus"* ]]; then
      printf '%s' "Opus"
    elif [[ "$name_lower" == *"sonnet"* ]]; then
      printf '%s' "Sonnet"
    elif [[ "$name_lower" == *"haiku"* ]]; then
      printf '%s' "Haiku"
    else
      printf '%s' "$name"
    fi
  else
    printf '%s' "$name"
  fi
}

# ============================================================================
# GIT WIDGETS
# ============================================================================

# Git branch name
widget_git_branch() {
  local input="$1"
  local config
  config=$(get_widget_config "git_branch")
  local icon
  icon=$(echo "$config" | jq -r '.icon // ""')
  local max_length
  max_length=$(echo "$config" | jq -r '.max_length // 20')

  local branch
  branch=$(git branch --show-current 2>/dev/null)
  if [[ -z "$branch" ]]; then
    return
  fi

  # Truncate if needed
  if (( ${#branch} > max_length )); then
    branch="${branch:0:$((max_length-1))}…"
  fi

  if [[ -n "$icon" ]]; then
    printf '%s %s' "$icon" "$branch"
  else
    printf '%s' "$branch"
  fi
}

# Git changes (added/modified/deleted)
widget_git_changes() {
  local input="$1"
  local config
  config=$(get_widget_config "git_changes")
  local show_clean
  show_clean=$(echo "$config" | jq -r '.show_clean // false')

  # Get git status
  local status
  status=$(git status --porcelain 2>/dev/null)
  if [[ -z "$status" ]]; then
    if [[ "$show_clean" == "true" ]]; then
      local clean_icon
      clean_icon=$(echo "$config" | jq -r '.icons.clean // "✓"')
      printf '%s' "$clean_icon"
    fi
    return
  fi

  local added
  local modified
  local deleted
  added=$(echo "$status" | grep -c '^A\|^??' 2>/dev/null || echo "0")
  modified=$(echo "$status" | grep -c '^M\| M' 2>/dev/null || echo "0")
  deleted=$(echo "$status" | grep -c '^D\| D' 2>/dev/null || echo "0")

  # Ensure numeric values
  added="${added//[^0-9]/}"
  modified="${modified//[^0-9]/}"
  deleted="${deleted//[^0-9]/}"
  added="${added:-0}"
  modified="${modified:-0}"
  deleted="${deleted:-0}"

  local add_icon
  local mod_icon
  local del_icon
  add_icon=$(echo "$config" | jq -r '.icons.added // "+"')
  mod_icon=$(echo "$config" | jq -r '.icons.modified // "~"')
  del_icon=$(echo "$config" | jq -r '.icons.deleted // "-"')

  local output=""
  [[ "$added" -gt 0 ]] && output+="${add_icon}${added}"
  [[ "$modified" -gt 0 ]] && output+="${mod_icon}${modified}"
  [[ "$deleted" -gt 0 ]] && output+="${del_icon}${deleted}"

  printf '%s' "$output"
}

# Git worktree name
widget_git_worktree() {
  local toplevel worktree
  toplevel=$(git rev-parse --show-toplevel 2>/dev/null)
  if [[ -n "$toplevel" ]]; then
    worktree=$(basename "$toplevel")
    printf '%s' "$worktree"
  fi
}

# Commits today
widget_commits_today() {
  local input="$1"
  local config
  config=$(get_widget_config "commits_today")
  local icon
  icon=$(echo "$config" | jq -r '.icon // ""')

  local count
  count=$(git log --oneline --since="midnight" 2>/dev/null | wc -l | tr -d ' ')

  if [[ -n "$icon" ]]; then
    printf '%s %s' "$icon" "$count"
  else
    printf '%s commits' "$count"
  fi
}

# ============================================================================
# CONTEXT WIDGETS
# ============================================================================

# Context percentage with optional progress bar
widget_context_percent() {
  local input="$1"
  local config
  config=$(get_widget_config "context_percent")
  local theme
  theme=$(load_theme)

  local input_tokens
  local output_tokens
  local context_size
  input_tokens=$(echo "$input" | jq -r '.context_window.total_input_tokens // 0')
  output_tokens=$(echo "$input" | jq -r '.context_window.total_output_tokens // 0')
  context_size=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')

  local total=$((input_tokens + output_tokens))
  # Guard against division by zero
  local percent=0
  if (( context_size > 0 )); then
    percent=$((total * 100 / context_size))
  fi

  local show_bar
  local bar_length
  show_bar=$(echo "$config" | jq -r '.show_bar // true')
  bar_length=$(echo "$config" | jq -r '.bar_length // 10')

  # Get threshold colors
  local low mid high
  low=$(echo "$config" | jq -r '.thresholds.low // 50')
  mid=$(echo "$config" | jq -r '.thresholds.mid // 75')
  high=$(echo "$config" | jq -r '.thresholds.high // 90')

  # Apply threshold coloring
  local color=""
  if (( percent >= high )); then
    color=$(echo "$theme" | jq -r '.colors.context_high.fg // "red"')
  elif (( percent >= mid )); then
    color=$(echo "$theme" | jq -r '.colors.context_mid.fg // "yellow"')
  else
    color=$(echo "$theme" | jq -r '.colors.context_low.fg // "green"')
  fi

  local output="${percent}%"

  if [[ "$show_bar" == "true" ]]; then
    local empty_char fill_char
    empty_char=$(echo "$config" | jq -r '.bar_chars[0] // "░"')
    fill_char=$(echo "$config" | jq -r '.bar_chars[1] // "█"')
    local bar
    bar=$(progress_bar "$percent" "$bar_length" "$empty_char" "$fill_char")
    output="$output $bar"
  fi

  colorize "$output" "$color"
}

# Context length (tokens used)
widget_context_length() {
  local input="$1"
  local config
  config=$(get_widget_config "context_length")
  local format
  format=$(echo "$config" | jq -r '.format // "short"')

  local input_tokens output_tokens context_size
  input_tokens=$(echo "$input" | jq -r '.context_window.total_input_tokens // 0')
  output_tokens=$(echo "$input" | jq -r '.context_window.total_output_tokens // 0')
  context_size=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')

  local total=$((input_tokens + output_tokens))

  if [[ "$format" == "short" ]]; then
    printf '%s/%s' "$(format_number "$total")" "$(format_number "$context_size")"
  else
    printf '%s/%s tokens' "$total" "$context_size"
  fi
}

# Context usable (remaining)
widget_context_usable() {
  local input="$1"

  local input_tokens output_tokens context_size
  input_tokens=$(echo "$input" | jq -r '.context_window.total_input_tokens // 0')
  output_tokens=$(echo "$input" | jq -r '.context_window.total_output_tokens // 0')
  context_size=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')

  local total=$((input_tokens + output_tokens))
  local remaining=$((context_size - total))
  # Guard against division by zero
  local percent=100
  if (( context_size > 0 )); then
    percent=$((remaining * 100 / context_size))
  fi

  printf '%s%% free' "$percent"
}

# ============================================================================
# TOKEN WIDGETS
# ============================================================================

widget_tokens_input() {
  local input="$1"
  local tokens
  tokens=$(echo "$input" | jq -r '.context_window.total_input_tokens // 0')
  printf '↓%s' "$(format_number "$tokens")"
}

widget_tokens_output() {
  local input="$1"
  local tokens
  tokens=$(echo "$input" | jq -r '.context_window.total_output_tokens // 0')
  printf '↑%s' "$(format_number "$tokens")"
}

widget_tokens_cached() {
  local input="$1"
  local tokens
  tokens=$(echo "$input" | jq -r '.context_window.cached_tokens // 0')
  printf '⚡%s' "$(format_number "$tokens")"
}

widget_tokens_total() {
  local input="$1"
  local input_tokens output_tokens
  input_tokens=$(echo "$input" | jq -r '.context_window.total_input_tokens // 0')
  output_tokens=$(echo "$input" | jq -r '.context_window.total_output_tokens // 0')
  local total=$((input_tokens + output_tokens))
  printf '%s tok' "$(format_number "$total")"
}

# ============================================================================
# COST WIDGETS
# ============================================================================

# Session cost
widget_session_cost() {
  local input="$1"
  local config
  config=$(get_widget_config "session_cost")
  local decimals icon
  decimals=$(echo "$config" | jq -r '.decimals // 2')
  icon=$(echo "$config" | jq -r '.icon // "$"')

  local cost
  cost=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')

  # Validate decimals is a number to prevent printf format issues
  if ! [[ "$decimals" =~ ^[0-9]+$ ]]; then
    decimals=2
  fi

  printf "%s%.${decimals}f" "$icon" "$cost"
}

# Daily cost (requires ccusage)
widget_daily_cost() {
  local config
  config=$(get_widget_config "daily_cost")
  local icon
  icon=$(echo "$config" | jq -r '.icon // "📅"')

  local cost="N/A"
  if command -v ccusage &>/dev/null; then
    cost=$(ccusage --format json 2>/dev/null | jq -r '.daily // "N/A"' 2>/dev/null) || cost="N/A"
  fi

  printf '%s %s' "$icon" "$cost"
}

# Weekly cost (requires ccusage)
widget_weekly_cost() {
  local config
  config=$(get_widget_config "weekly_cost")
  local icon
  icon=$(echo "$config" | jq -r '.icon // "📆"')

  local cost="N/A"
  if command -v ccusage &>/dev/null; then
    cost=$(ccusage --format json 2>/dev/null | jq -r '.weekly // "N/A"' 2>/dev/null) || cost="N/A"
  fi

  printf '%s %s' "$icon" "$cost"
}

# Monthly cost (requires ccusage)
widget_monthly_cost() {
  local config
  config=$(get_widget_config "monthly_cost")
  local icon
  icon=$(echo "$config" | jq -r '.icon // "🗓"')

  local cost="N/A"
  if command -v ccusage &>/dev/null; then
    cost=$(ccusage --format json 2>/dev/null | jq -r '.monthly // "N/A"' 2>/dev/null) || cost="N/A"
  fi

  printf '%s %s' "$icon" "$cost"
}

# Burn rate (cost per hour) - uses awk instead of bc for portability
widget_burn_rate() {
  local input="$1"
  local config
  config=$(get_widget_config "burn_rate")
  local icon
  icon=$(echo "$config" | jq -r '.icon // "🔥"')

  local cost duration_ms
  cost=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')
  duration_ms=$(echo "$input" | jq -r '.cost.total_duration_ms // 0')

  if (( duration_ms > 0 )); then
    # Use awk for portable floating-point math (no bc dependency)
    local rate
    rate=$(awk -v cost="$cost" -v ms="$duration_ms" 'BEGIN { hours = ms / 3600000; if (hours > 0) printf "%.2f", cost / hours; else print "0.00" }')
    printf '%s $%s/hr' "$icon" "$rate"
  else
    printf '%s $0.00/hr' "$icon"
  fi
}

# Budget alert - uses awk for float comparison (no bc dependency)
widget_budget_alert() {
  local input="$1"
  local config
  config=$(get_widget_config "budget_alert")
  local icon
  icon=$(echo "$config" | jq -r '.icon // "⚠️"')

  local cost session_threshold
  cost=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')
  session_threshold=$(echo "$config" | jq -r '.thresholds.session // 10')

  # Use float_gte from colors.sh for portable float comparison
  if float_gte "$cost" "$session_threshold"; then
    colorize "$icon BUDGET" "red" "" "true"
  fi
}

# ============================================================================
# TIME WIDGETS
# ============================================================================

# Session clock (elapsed time)
widget_session_clock() {
  local input="$1"
  local config
  config=$(get_widget_config "session_clock")
  local format icon
  format=$(echo "$config" | jq -r '.format // "short"')
  icon=$(echo "$config" | jq -r '.icon // "⏱"')

  local duration_ms
  duration_ms=$(echo "$input" | jq -r '.cost.total_duration_ms // 0')
  local formatted
  formatted=$(format_duration "$duration_ms" "$format")

  printf '%s %s' "$icon" "$formatted"
}

# Block timer (5-hour window)
widget_block_timer() {
  local input="$1"
  local config
  config=$(get_widget_config "block_timer")
  local window_hours show_progress
  window_hours=$(echo "$config" | jq -r '.window_hours // 5')
  show_progress=$(echo "$config" | jq -r '.show_progress // true')

  local duration_ms
  duration_ms=$(echo "$input" | jq -r '.cost.total_duration_ms // 0')
  local window_ms=$((window_hours * 3600000))

  # Guard against division by zero
  if (( window_ms <= 0 )); then
    printf '%s' "?"
    return
  fi

  local remaining_ms=$((window_ms - (duration_ms % window_ms)))

  local formatted
  formatted=$(format_duration "$remaining_ms" "short")

  if [[ "$show_progress" == "true" ]]; then
    local elapsed=$((duration_ms % window_ms))
    local percent=$((elapsed * 100 / window_ms))
    local bar
    bar=$(progress_bar "$percent" 5 "░" "█")
    printf '%s %s' "$bar" "$formatted"
  else
    printf '%s remaining' "$formatted"
  fi
}

# Reset timer (countdown to reset)
widget_reset_timer() {
  local input="$1"
  # This would need external data about when the rate limit resets
  # For now, show time until next 5-hour boundary
  widget_block_timer "$input"
}

# ============================================================================
# SYSTEM WIDGETS
# ============================================================================

# MCP server status
widget_mcp_status() {
  local input="$1"
  local config
  config=$(get_widget_config "mcp_status")
  local show_count show_names ok_icon error_icon unknown_icon
  show_count=$(echo "$config" | jq -r '.show_count // true')
  show_names=$(echo "$config" | jq -r '.show_names // false')
  ok_icon=$(echo "$config" | jq -r '.icons.ok // "🟢"')
  error_icon=$(echo "$config" | jq -r '.icons.error // "🔴"')
  unknown_icon=$(echo "$config" | jq -r '.icons.unknown // "🟡"')

  # Try to get MCP status from input
  local servers
  servers=$(echo "$input" | jq -r '.mcp_servers // empty')

  if [[ -z "$servers" || "$servers" == "null" ]]; then
    # Fallback: check if MCP config exists
    local mcp_config="$HOME/.claude/.mcp.json"
    if [[ -f "$mcp_config" ]]; then
      local server_count
      server_count=$(jq '.mcpServers | length' "$mcp_config" 2>/dev/null) || server_count=0
      if (( server_count > 0 )); then
        printf '%s MCP' "$unknown_icon"
      fi
    fi
    return
  fi

  local total connected
  total=$(echo "$servers" | jq 'length')
  connected=$(echo "$servers" | jq '[.[] | select(.status == "connected")] | length')

  if (( connected == total )); then
    if [[ "$show_count" == "true" ]]; then
      printf '%s %s/%s' "$ok_icon" "$connected" "$total"
    else
      printf '%s MCP' "$ok_icon"
    fi
  else
    if [[ "$show_count" == "true" ]]; then
      printf '%s %s/%s' "$error_icon" "$connected" "$total"
    else
      printf '%s MCP' "$error_icon"
    fi
  fi
}

# Tmux info
widget_tmux_info() {
  local config
  config=$(get_widget_config "tmux_info")
  local show_window
  show_window=$(echo "$config" | jq -r '.show_window // true')

  if [[ -z "$TMUX" ]]; then
    return
  fi

  local session
  session=$(tmux display-message -p '#S' 2>/dev/null)
  if [[ "$show_window" == "true" ]]; then
    local window
    window=$(tmux display-message -p '#W' 2>/dev/null)
    printf '%s:%s' "$session" "$window"
  else
    printf '%s' "$session"
  fi
}

# Current directory with max_segments support
widget_directory() {
  local input="$1"
  local config
  config=$(get_widget_config "directory")
  local style max_segments icon
  style=$(echo "$config" | jq -r '.style // "basename"')
  max_segments=$(echo "$config" | jq -r '.max_segments // 2')
  icon=$(echo "$config" | jq -r '.icon // ""')

  local dir
  dir=$(echo "$input" | jq -r '.workspace.current_dir // ""')
  if [[ -z "$dir" ]]; then
    dir=$(pwd)
  fi

  # Replace home with ~
  local normalized="${dir/#$HOME/~}"
  local output=""

  case "$style" in
    "basename")
      output=$(basename "$dir")
      ;;
    "full")
      # Apply max_segments truncation
      if [[ "$max_segments" -gt 0 ]]; then
        # Use mapfile to handle paths with spaces correctly
        local -a parts
        local saved_ifs="$IFS"
        IFS='/' read -ra parts <<< "$normalized"
        IFS="$saved_ifs"
        local count=${#parts[@]}
        if (( count > max_segments )); then
          # Keep last max_segments parts, prefix with …
          local start=$((count - max_segments))
          output="…"
          for ((i=start; i<count; i++)); do
            output+="/${parts[$i]}"
          done
        else
          output="$normalized"
        fi
      else
        output="$normalized"
      fi
      ;;
    "fish")
      # Fish-style abbreviation with max_segments
      local abbreviated
      abbreviated=$(echo "$normalized" | sed 's|\([^/]\)[^/]*/|\1/|g')
      if [[ "$max_segments" -gt 0 ]]; then
        # Use read -ra for proper handling of paths with spaces
        local -a parts
        local saved_ifs="$IFS"
        IFS='/' read -ra parts <<< "$abbreviated"
        IFS="$saved_ifs"
        local count=${#parts[@]}
        if (( count > max_segments )); then
          local start=$((count - max_segments))
          output="…"
          for ((i=start; i<count; i++)); do
            output+="/${parts[$i]}"
          done
        else
          output="$abbreviated"
        fi
      else
        output="$abbreviated"
      fi
      ;;
    *)
      output=$(basename "$dir")
      ;;
  esac

  if [[ -n "$icon" ]]; then
    printf '%s %s' "$icon" "$output"
  else
    printf '%s' "$output"
  fi
}

# Claude Code version
widget_version() {
  local config
  config=$(get_widget_config "version")
  local icon
  icon=$(echo "$config" | jq -r '.icon // "v"')

  local version
  version=$(claude --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+') || version="?"
  printf '%s%s' "$icon" "$version"
}

# Output style
widget_output_style() {
  local input="$1"
  local style
  style=$(echo "$input" | jq -r '.output_style // "default"')
  printf '%s' "$style"
}

# ============================================================================
# METRICS WIDGETS
# ============================================================================

# Response time
widget_response_time() {
  local input="$1"
  local config
  config=$(get_widget_config "response_time")
  local format
  format=$(echo "$config" | jq -r '.format // "ms"')

  local duration_ms
  duration_ms=$(echo "$input" | jq -r '.cost.total_duration_ms // 0')

  if [[ "$format" == "ms" ]]; then
    printf '%sms' "$duration_ms"
  else
    local seconds=$((duration_ms / 1000))
    printf '%ss' "$seconds"
  fi
}

# Lines changed (would need git diff data)
widget_lines_changed() {
  local config
  config=$(get_widget_config "lines_changed")
  local add_icon del_icon
  add_icon=$(echo "$config" | jq -r '.icons.added // "+"')
  del_icon=$(echo "$config" | jq -r '.icons.removed // "-"')

  local stats
  stats=$(git diff --stat 2>/dev/null | tail -1)
  local added removed
  added=$(echo "$stats" | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+') || added=0
  removed=$(echo "$stats" | grep -oE '[0-9]+ deletion' | grep -oE '[0-9]+') || removed=0

  printf '%s%s %s%s' "$add_icon" "$added" "$del_icon" "$removed"
}

# Message count
widget_message_count() {
  local input="$1"
  local count
  count=$(echo "$input" | jq -r '.message_count // "?"')
  printf '%s msgs' "$count"
}

# ============================================================================
# CUSTOM WIDGETS
# ============================================================================

# Custom text
widget_custom_text() {
  local config
  config=$(get_widget_config "custom_text")
  local text
  text=$(echo "$config" | jq -r '.text // ""')
  printf '%s' "$text"
}

# Custom command - SECURITY: Only allows whitelisted commands
# WARNING: Custom commands are disabled by default for security.
# To enable, explicitly whitelist commands in config.
#
# Default whitelist: date, uptime, whoami, hostname, pwd, echo
# Configure additional commands via config: allowed_commands: ["cmd1", "cmd2"]
widget_custom_command() {
  local config
  config=$(get_widget_config "custom_command")
  local command
  command=$(echo "$config" | jq -r '.command // ""')

  if [[ -z "$command" ]]; then
    return
  fi

  # Default whitelist of safe, read-only commands
  local -a default_whitelist=("date" "uptime" "whoami" "hostname" "pwd" "echo" "basename" "dirname")

  # Get user-configured additional commands (if any)
  local -a user_whitelist
  mapfile -t user_whitelist < <(echo "$config" | jq -r '.allowed_commands // [] | .[]' 2>/dev/null)

  # Combine whitelists
  local -a whitelist=("${default_whitelist[@]}" "${user_whitelist[@]}")

  # Security: Only allow simple commands without shell metacharacters
  # Reject commands with dangerous patterns
  if [[ "$command" =~ [\;\|\&\$\`\(\)\<\>\!\~\#] ]]; then
    printf '%s' "[unsafe cmd]"
    return
  fi

  # Parse command into array (first word is the command, rest are args)
  local -a cmd_parts
  read -ra cmd_parts <<< "$command"

  if [[ ${#cmd_parts[@]} -eq 0 ]]; then
    return
  fi

  local cmd_name="${cmd_parts[0]}"

  # SECURITY: Check if command is in whitelist
  local allowed=false
  for allowed_cmd in "${whitelist[@]}"; do
    if [[ "$cmd_name" == "$allowed_cmd" ]]; then
      allowed=true
      break
    fi
  done

  if [[ "$allowed" != "true" ]]; then
    printf '%s' "[cmd not allowed]"
    return
  fi

  # Check if command exists
  if ! command -v "$cmd_name" &>/dev/null; then
    printf '%s' "[cmd not found]"
    return
  fi

  # Execute without eval - directly invoke the command
  "${cmd_parts[@]}" 2>/dev/null || printf '%s' ""
}

# Separator
widget_separator() {
  get_separator
}

# ============================================================================
# WIDGET DISPATCHER
# ============================================================================

# Render a single widget
# Usage: render_widget "widget_name" "$input"
render_widget() {
  local widget="$1"
  local input="$2"

  # Check if widget is enabled
  if ! is_widget_enabled "$widget"; then
    return
  fi

  # Dispatch to widget function
  case "$widget" in
    model_emoji) widget_model_emoji "$input" ;;
    model_name) widget_model_name "$input" ;;
    git_branch) widget_git_branch "$input" ;;
    git_changes) widget_git_changes "$input" ;;
    git_worktree) widget_git_worktree "$input" ;;
    commits_today) widget_commits_today "$input" ;;
    context_percent) widget_context_percent "$input" ;;
    context_length) widget_context_length "$input" ;;
    context_usable) widget_context_usable "$input" ;;
    tokens_input) widget_tokens_input "$input" ;;
    tokens_output) widget_tokens_output "$input" ;;
    tokens_cached) widget_tokens_cached "$input" ;;
    tokens_total) widget_tokens_total "$input" ;;
    session_cost) widget_session_cost "$input" ;;
    daily_cost) widget_daily_cost "$input" ;;
    weekly_cost) widget_weekly_cost "$input" ;;
    monthly_cost) widget_monthly_cost "$input" ;;
    burn_rate) widget_burn_rate "$input" ;;
    budget_alert) widget_budget_alert "$input" ;;
    session_clock) widget_session_clock "$input" ;;
    block_timer) widget_block_timer "$input" ;;
    reset_timer) widget_reset_timer "$input" ;;
    mcp_status) widget_mcp_status "$input" ;;
    tmux_info) widget_tmux_info "$input" ;;
    directory) widget_directory "$input" ;;
    version) widget_version "$input" ;;
    output_style) widget_output_style "$input" ;;
    response_time) widget_response_time "$input" ;;
    lines_changed) widget_lines_changed "$input" ;;
    message_count) widget_message_count "$input" ;;
    custom_text) widget_custom_text "$input" ;;
    custom_command) widget_custom_command "$input" ;;
    separator) widget_separator ;;
    *) ;;
  esac
}

# Render a line of widgets
# Usage: render_line '["widget1", "widget2"]' "$input"
render_line() {
  local widgets="$1"
  local input="$2"
  local separator
  separator=$(get_separator)

  local output=""
  local first=true
  local prev_widget=""

  # Parse widget array
  local count
  count=$(echo "$widgets" | jq 'length')
  for ((i=0; i<count; i++)); do
    local widget
    widget=$(echo "$widgets" | jq -r ".[$i]")
    local rendered
    rendered=$(render_widget "$widget" "$input")

    if [[ -n "$rendered" ]]; then
      if [[ "$first" == "true" ]]; then
        output="$rendered"
        first=false
      elif [[ "$widget" == "separator" ]]; then
        # Separator widget renders itself
        output+="$rendered"
      elif [[ "$prev_widget" == "separator" ]]; then
        # Previous was separator, don't add another
        output+="$rendered"
      else
        # Normal widget after normal widget - add separator
        output+="$separator$rendered"
      fi
    fi
    prev_widget="$widget"
  done

  printf '%s' "$output"
}
