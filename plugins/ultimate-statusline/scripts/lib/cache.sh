#!/bin/bash
# Cache utilities for ultimate-statusline
# Caches expensive operations like API calls and git status

CACHE_DIR="${CLAUDE_STATUSLINE_CACHE:-$HOME/.cache/ultimate-statusline}"
_DEFAULT_CACHE_TTL="${CLAUDE_STATUSLINE_CACHE_TTL:-300}"  # 5 minutes default

# Validate TTL is numeric, return default if not
_validate_ttl() {
  local ttl="$1"
  if [[ "$ttl" =~ ^[0-9]+$ ]]; then
    echo "$ttl"
  else
    echo "$_DEFAULT_CACHE_TTL"
  fi
}

# Ensure cache directory exists
mkdir -p "$CACHE_DIR" 2>/dev/null

# Convert key to safe filename (prevent path traversal)
# Usage: _safe_key "my.key/name"
# Returns: hashed or sanitized filename
_safe_key() {
  local key="$1"
  # Reject empty keys
  if [[ -z "$key" ]]; then
    echo "_empty_"
    return
  fi
  # Sanitize: only allow alphanumeric, underscore, hyphen, dot
  # Replace unsafe characters with underscore
  echo "$key" | tr -c 'a-zA-Z0-9_.-' '_' | cut -c1-64
}

# Get cached value
# Usage: cache_get "key" [ttl]
# Returns: 0 if hit (prints value), 1 if miss/expired
cache_get() {
  local key="$1"
  local ttl="${2:-$_DEFAULT_CACHE_TTL}"
  ttl=$(_validate_ttl "$ttl")
  local safe_key
  safe_key=$(_safe_key "$key")
  local cache_file="$CACHE_DIR/$safe_key"

  if [[ ! -f "$cache_file" ]]; then
    return 1
  fi

  # Check if expired
  local mtime now age
  mtime=$(stat -f %m "$cache_file" 2>/dev/null || stat -c %Y "$cache_file" 2>/dev/null || echo "0")
  now=$(date +%s)
  # Handle case where stat failed
  if [[ -z "$mtime" || "$mtime" == "0" ]]; then
    rm -f "$cache_file"
    return 1
  fi
  age=$((now - mtime))

  if (( age > ttl )); then
    rm -f "$cache_file"
    return 1
  fi

  # Output cached content (even if empty)
  cat "$cache_file"
  return 0
}

# Set cached value (including empty strings)
# Usage: cache_set "key" "value"
cache_set() {
  local key="$1"
  local value="$2"
  local safe_key
  safe_key=$(_safe_key "$key")
  local cache_file="$CACHE_DIR/$safe_key"

  # Atomic write: write to temp file then move (prevents torn reads)
  local tmp_file
  tmp_file="${cache_file}.$$"
  printf '%s' "$value" > "$tmp_file" && mv "$tmp_file" "$cache_file"
}

# Clear all cache
cache_clear() {
  # Safety check: ensure CACHE_DIR is set and non-empty
  if [[ -z "$CACHE_DIR" || "$CACHE_DIR" == "/" ]]; then
    echo "Error: CACHE_DIR is not set or is root" >&2
    return 1
  fi
  rm -rf "${CACHE_DIR:?}"/*
}

# Cached command execution with custom TTL
# Usage: cached_command_ttl "cache_key" ttl_seconds command [args...]
# Example: cached_command_ttl "git_status" 30 git status --porcelain
cached_command_ttl() {
  local key="$1"
  local ttl="$2"
  shift 2

  # Validate TTL (no global mutation)
  ttl=$(_validate_ttl "$ttl")

  local cached
  if cached=$(cache_get "$key" "$ttl"); then
    printf '%s' "$cached"
    return 0
  fi

  # Execute command directly (no eval)
  local result
  result=$("$@" 2>/dev/null) || result=""

  # Cache the result (even if empty)
  cache_set "$key" "$result"

  printf '%s' "$result"
}

# Cached command execution with default TTL
# Usage: cached_command "cache_key" command [args...]
cached_command() {
  local key="$1"
  shift
  cached_command_ttl "$key" "$_DEFAULT_CACHE_TTL" "$@"
}

# Get cached ccusage data
get_ccusage_data() {
  cached_command "ccusage" ccusage --format json
}

# Get cached git status (30 second TTL)
get_cached_git_status() {
  cached_command_ttl "git_status" 30 git status --porcelain
}

# Get cached Claude Code version
get_cached_version() {
  # Long TTL for version (1 hour)
  local version
  version=$(cached_command_ttl "claude_version" 3600 claude --version)
  echo "$version" | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "?"
}
