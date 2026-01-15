#!/bin/bash
# Color utilities for ultimate-statusline
# Provides ANSI color codes and theme support
# Compatible with bash 3.x (macOS default)

# Reset - use ANSI-C quoting for proper escape interpretation
RESET=$'\033[0m'

# Text styles
BOLD=$'\033[1m'
DIM=$'\033[2m'
ITALIC=$'\033[3m'
UNDERLINE=$'\033[4m'

# Get foreground color code
# Usage: fg_color "green"
fg_color() {
  local color="$1"
  case "$color" in
    black) printf '%s' $'\033[30m' ;;
    red) printf '%s' $'\033[31m' ;;
    green) printf '%s' $'\033[32m' ;;
    yellow) printf '%s' $'\033[33m' ;;
    blue) printf '%s' $'\033[34m' ;;
    magenta) printf '%s' $'\033[35m' ;;
    cyan) printf '%s' $'\033[36m' ;;
    white) printf '%s' $'\033[37m' ;;
    gray) printf '%s' $'\033[90m' ;;
    bright_red) printf '%s' $'\033[91m' ;;
    bright_green) printf '%s' $'\033[92m' ;;
    bright_yellow) printf '%s' $'\033[93m' ;;
    bright_blue) printf '%s' $'\033[94m' ;;
    bright_magenta) printf '%s' $'\033[95m' ;;
    bright_cyan) printf '%s' $'\033[96m' ;;
    bright_white) printf '%s' $'\033[97m' ;;
    *) ;;
  esac
}

# Get background color code
# Usage: bg_color "blue"
bg_color() {
  local color="$1"
  case "$color" in
    black) printf '%s' $'\033[40m' ;;
    red) printf '%s' $'\033[41m' ;;
    green) printf '%s' $'\033[42m' ;;
    yellow) printf '%s' $'\033[43m' ;;
    blue) printf '%s' $'\033[44m' ;;
    magenta) printf '%s' $'\033[45m' ;;
    cyan) printf '%s' $'\033[46m' ;;
    white) printf '%s' $'\033[47m' ;;
    gray) printf '%s' $'\033[100m' ;;
    *) ;;
  esac
}

# Apply color to text
# Usage: colorize "text" "fg_color" ["bg_color"] ["bold"]
colorize() {
  local text="$1"
  local fg="${2:-}"
  local bg="${3:-}"
  local bold="${4:-}"

  local code=""
  if [[ -n "$bold" && "$bold" != "false" ]]; then
    code="$BOLD"
  fi
  if [[ -n "$fg" ]]; then
    code="${code}$(fg_color "$fg")"
  fi
  if [[ -n "$bg" ]]; then
    code="${code}$(bg_color "$bg")"
  fi

  printf '%s%s%s' "$code" "$text" "$RESET"
}

# Apply theme color from config
# Usage: theme_color "widget_name" "text" "$THEME_JSON"
theme_color() {
  local widget="$1"
  local text="$2"
  local theme_json="${3:-}"

  if [[ -z "$theme_json" ]]; then
    printf '%s' "$text"
    return
  fi

  # Use --arg for safe variable interpolation
  local fg
  local bg
  local bold
  fg=$(echo "$theme_json" | jq -r --arg w "$widget" '.colors[$w].fg // empty' 2>/dev/null) || fg=""
  bg=$(echo "$theme_json" | jq -r --arg w "$widget" '.colors[$w].bg // empty' 2>/dev/null) || bg=""
  bold=$(echo "$theme_json" | jq -r --arg w "$widget" '.colors[$w].bold // empty' 2>/dev/null) || bold=""

  if [[ -n "$fg" ]]; then
    colorize "$text" "$fg" "$bg" "$bold"
  else
    printf '%s' "$text"
  fi
}

# Progress bar generator
# Usage: progress_bar 75 10 "░" "█"
progress_bar() {
  local percent="$1"
  local length="${2:-10}"
  local empty_char="${3:-░}"
  local fill_char="${4:-█}"

  # Ensure percent is within bounds
  if (( percent < 0 )); then
    percent=0
  elif (( percent > 100 )); then
    percent=100
  fi

  local filled=$((percent * length / 100))
  local empty=$((length - filled))

  local bar=""
  for ((i=0; i<filled; i++)); do
    bar="${bar}${fill_char}"
  done
  for ((i=0; i<empty; i++)); do
    bar="${bar}${empty_char}"
  done

  printf '%s' "$bar"
}

# Threshold-based coloring (supports floats)
# Usage: threshold_color 75 50 75 90 "green" "yellow" "red"
threshold_color() {
  local value="$1"
  local low="$2"
  local mid="$3"
  local high="$4"
  local low_color="${5:-green}"
  local mid_color="${6:-yellow}"
  local high_color="${7:-red}"

  # Use float_gte for float-safe comparison
  if float_gte "$value" "$high"; then
    fg_color "$high_color"
  elif float_gte "$value" "$mid"; then
    fg_color "$mid_color"
  else
    fg_color "$low_color"
  fi
}

# Format number with K/M suffix
# Usage: format_number 12345 -> "12.3K"
format_number() {
  local num="$1"

  if (( num >= 1000000 )); then
    # Use awk for floating point on bash 3
    echo "$num" | awk '{printf "%.1fM", $1/1000000}'
  elif (( num >= 1000 )); then
    echo "$num" | awk '{printf "%.1fK", $1/1000}'
  else
    echo "$num"
  fi
}

# Format duration in human readable
# Usage: format_duration 3661000 -> "1h 1m"
format_duration() {
  local ms="$1"
  local format="${2:-short}"

  local seconds=$((ms / 1000))
  local minutes=$((seconds / 60))
  local hours=$((minutes / 60))
  local remaining_minutes=$((minutes % 60))
  local remaining_seconds=$((seconds % 60))

  if [[ "$format" == "short" ]]; then
    if (( hours > 0 )); then
      printf "%dh %dm" "$hours" "$remaining_minutes"
    elif (( minutes > 0 )); then
      printf "%dm %ds" "$minutes" "$remaining_seconds"
    else
      printf "%ds" "$seconds"
    fi
  else
    if (( hours > 0 )); then
      printf "%d hours %d minutes" "$hours" "$remaining_minutes"
    elif (( minutes > 0 )); then
      printf "%d minutes" "$minutes"
    else
      printf "%d seconds" "$seconds"
    fi
  fi
}

# Safe float comparison using awk (no bc dependency)
# Usage: float_gte 2.5 1.0 -> returns 0 (true) or 1 (false)
float_gte() {
  local a="$1"
  local b="$2"
  awk -v a="$a" -v b="$b" 'BEGIN { exit !(a >= b) }'
}

# Safe float division using awk (no bc dependency)
# Usage: float_div 10 3 2 -> "3.33" (10/3 with 2 decimal places)
float_div() {
  local numerator="$1"
  local denominator="$2"
  local decimals="${3:-2}"
  awk -v n="$numerator" -v d="$denominator" -v dec="$decimals" 'BEGIN { printf "%.*f", dec, (d != 0 ? n/d : 0) }'
}
