#!/bin/bash
# Input acknowledgment sound when user submits a prompt
# Quick audible feedback that input was received

# Configuration via environment variables:
# AUDIO_FEEDBACK_SOUNDS: Enable sound effects (default: true)
# AUDIO_FEEDBACK_PROMPT_SOUND: Specific setting for prompt sounds (default: true)

SOUNDS_ENABLED="${AUDIO_FEEDBACK_SOUNDS:-true}"
PROMPT_SOUND_ENABLED="${AUDIO_FEEDBACK_PROMPT_SOUND:-true}"

# Get script directory for sound file paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOUNDS_DIR="${SCRIPT_DIR}/../sounds"

# Exit if sounds disabled
if [ "$SOUNDS_ENABLED" != "true" ] || [ "$PROMPT_SOUND_ENABLED" != "true" ]; then
    exit 0
fi

# Detect available audio player
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

# Find sound file (supports .wav and .aiff/.aif)
find_sound() {
    local base_name="$1"
    local fallback="$2"

    if [ -f "${SOUNDS_DIR}/${base_name}.wav" ]; then
        echo "${SOUNDS_DIR}/${base_name}.wav"
        return 0
    fi
    if [ -f "${SOUNDS_DIR}/${base_name}.aiff" ]; then
        echo "${SOUNDS_DIR}/${base_name}.aiff"
        return 0
    fi
    if [ -f "${SOUNDS_DIR}/${base_name}.aif" ]; then
        echo "${SOUNDS_DIR}/${base_name}.aif"
        return 0
    fi
    if [ -n "$fallback" ] && [ -f "$fallback" ]; then
        echo "$fallback"
        return 0
    fi
    return 1
}

# Play audio file with detected player
play_sound() {
    local file="$1"
    local player
    player=$(detect_player)

    if [ -z "$player" ] || [ -z "$file" ]; then
        return 0
    fi

    case "$player" in
        afplay)  afplay "$file" >/dev/null 2>&1 & ;;
        paplay)  paplay "$file" >/dev/null 2>&1 & ;;
        aplay)   aplay -q "$file" >/dev/null 2>&1 & ;;
        play)    play -q "$file" >/dev/null 2>&1 & ;;
    esac
}

# Play sound effect in background (fire-and-forget)
SOUND_FILE=$(find_sound "prompt-submit" "/System/Library/Sounds/Tink.aiff")
if [ -n "$SOUND_FILE" ]; then
    play_sound "$SOUND_FILE"
fi

exit 0
