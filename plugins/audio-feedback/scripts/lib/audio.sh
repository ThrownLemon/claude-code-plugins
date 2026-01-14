#!/bin/bash
# Shared audio library for audio-feedback plugin
# Source this file to use common audio functions

# JSON escape helper - escapes quotes, backslashes, and newlines
json_escape() {
    local str="$1"
    str="${str//\\/\\\\}"      # Escape backslashes
    str="${str//\"/\\\"}"      # Escape quotes
    str="${str//$'\n'/\\n}"    # Escape newlines
    str="${str//$'\r'/\\r}"    # Escape carriage returns
    str="${str//$'\t'/\\t}"    # Escape tabs
    echo "$str"
}

# Normalize boolean values (true/1/yes -> true, false/0/no -> false)
normalize_bool() {
    local val="${1,,}"  # Lowercase
    case "$val" in
        true|1|yes|on) echo "true" ;;
        false|0|no|off|"") echo "false" ;;
        *) echo "false" ;;
    esac
}

# Detect available audio player
# Returns: player command name or empty string
detect_player() {
    if command -v afplay >/dev/null 2>&1; then
        echo "afplay"
    elif command -v paplay >/dev/null 2>&1; then
        echo "paplay"
    elif command -v aplay >/dev/null 2>&1; then
        echo "aplay"
    elif command -v play >/dev/null 2>&1; then
        echo "play"
    else
        echo ""
    fi
}

# Find sound file (supports .wav, .aiff, .aif)
# Args: $1 = base_name (without extension), $2 = fallback path (optional)
# Returns: path to sound file or empty string
find_sound() {
    local base_name="$1"
    local fallback="$2"

    # SOUNDS_DIR must be set by the sourcing script
    if [ -z "$SOUNDS_DIR" ]; then
        [ -n "$fallback" ] && [ -f "$fallback" ] && echo "$fallback"
        return 1
    fi

    # Check for wav first
    if [ -f "${SOUNDS_DIR}/${base_name}.wav" ]; then
        echo "${SOUNDS_DIR}/${base_name}.wav"
        return 0
    fi
    # Check for aiff
    if [ -f "${SOUNDS_DIR}/${base_name}.aiff" ]; then
        echo "${SOUNDS_DIR}/${base_name}.aiff"
        return 0
    fi
    # Check for aif
    if [ -f "${SOUNDS_DIR}/${base_name}.aif" ]; then
        echo "${SOUNDS_DIR}/${base_name}.aif"
        return 0
    fi
    # Return fallback if provided
    if [ -n "$fallback" ] && [ -f "$fallback" ]; then
        echo "$fallback"
        return 0
    fi
    return 1
}

# Play audio file with detected player (background, fire-and-forget)
# Args: $1 = file path
play_sound() {
    local file="$1"
    local player
    player=$(detect_player)

    if [ -z "$player" ] || [ -z "$file" ] || [ ! -f "$file" ]; then
        return 0  # Silent exit if no player or file
    fi

    case "$player" in
        afplay)  afplay "$file" >/dev/null 2>&1 & ;;
        paplay)  paplay "$file" >/dev/null 2>&1 & ;;
        aplay)   aplay -q "$file" >/dev/null 2>&1 & ;;
        play)    play -q "$file" >/dev/null 2>&1 & ;;
    esac
}

# Play TTS audio from stdin (blocking for pipeline)
# Expects audio data piped to stdin
play_tts() {
    local player
    player=$(detect_player)

    if [ -z "$player" ]; then
        cat >/dev/null  # Drain stdin
        return 0
    fi

    case "$player" in
        afplay)  afplay - >/dev/null 2>&1 ;;
        paplay)  paplay >/dev/null 2>&1 ;;
        aplay)   aplay -q >/dev/null 2>&1 ;;
        play)    play -t mp3 - >/dev/null 2>&1 ;;
    esac
}

# Speak text using Kokoro TTS (fire-and-forget background)
# Args: $1 = message text
# Uses: KOKORO_URL, VOICE_MODEL, VOICE_NAME from environment
speak_tts() {
    local message="$1"
    local url="${KOKORO_URL:-http://localhost:8880}"
    local model="${VOICE_MODEL:-kokoro}"
    local voice="${VOICE_NAME:-af_heart}"

    # JSON-escape the message
    local escaped_message
    escaped_message=$(json_escape "$message")

    # Call TTS and play (fire-and-forget)
    (curl -sS --connect-timeout 5 --max-time 30 "${url}/v1/audio/speech" \
        -H 'Content-Type: application/json' \
        -d "{\"model\":\"${model}\",\"input\":\"${escaped_message}\",\"voice\":\"${voice}\"}" \
        2>/dev/null | play_tts) &
}

# Check if sound playback should be debounced
# Args: $1 = lock name (e.g., "tool-complete")
# Returns: 0 if should play, 1 if should skip (debounced)
should_play_sound() {
    local lock_name="$1"
    local lock_file="/tmp/audio-feedback-${lock_name}.lock"
    local debounce_ms=100  # 100ms debounce

    # Check if lock exists and is recent
    if [ -f "$lock_file" ]; then
        local lock_age
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS: use stat -f
            lock_age=$(( $(date +%s) - $(stat -f %m "$lock_file" 2>/dev/null || echo 0) ))
        else
            # Linux: use stat -c
            lock_age=$(( $(date +%s) - $(stat -c %Y "$lock_file" 2>/dev/null || echo 0) ))
        fi

        # If lock is less than 1 second old, debounce
        if [ "$lock_age" -lt 1 ]; then
            return 1  # Skip (debounced)
        fi
    fi

    # Update lock file
    touch "$lock_file" 2>/dev/null
    return 0  # Should play
}
