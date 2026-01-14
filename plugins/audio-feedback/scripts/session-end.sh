#!/bin/bash
# Session end - play farewell sound and optional voice announcement
# Triggered when a Claude Code session ends

# Configuration via environment variables:
# AUDIO_FEEDBACK_SOUNDS: Enable sound effects (default: true)
# AUDIO_FEEDBACK_VOICE: Enable voice announcements (default: true)
# AUDIO_FEEDBACK_VOICE_MODEL: TTS model (default: kokoro)
# AUDIO_FEEDBACK_VOICE_NAME: TTS voice (default: af_heart)
# KOKORO_TTS_URL: Kokoro TTS endpoint (default: http://localhost:8880)

SOUNDS_ENABLED="${AUDIO_FEEDBACK_SOUNDS:-true}"
VOICE_ENABLED="${AUDIO_FEEDBACK_VOICE:-true}"
VOICE_MODEL="${AUDIO_FEEDBACK_VOICE_MODEL:-kokoro}"
VOICE_NAME="${AUDIO_FEEDBACK_VOICE_NAME:-af_heart}"
KOKORO_URL="${KOKORO_TTS_URL:-http://localhost:8880}"

# Get script directory for sound file paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOUNDS_DIR="${SCRIPT_DIR}/../sounds"

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

# Play TTS audio from stdin
play_tts() {
    local player
    player=$(detect_player)

    if [ -z "$player" ]; then
        cat >/dev/null
        return 0
    fi

    case "$player" in
        afplay)  afplay - >/dev/null 2>&1 ;;
        paplay)  paplay >/dev/null 2>&1 ;;
        aplay)   aplay -q >/dev/null 2>&1 ;;
        play)    play -t mp3 - >/dev/null 2>&1 ;;
    esac
}

# Play sound effect
if [ "$SOUNDS_ENABLED" = "true" ]; then
    SOUND_FILE=$(find_sound "session-end" "/System/Library/Sounds/Purr.aiff")
    if [ -n "$SOUND_FILE" ]; then
        play_sound "$SOUND_FILE"
    fi
fi

# Voice announcement
if [ "$VOICE_ENABLED" = "true" ]; then
    MESSAGE="Session ended. Goodbye!"

    (curl -sS --connect-timeout 5 --max-time 30 "${KOKORO_URL}/v1/audio/speech" \
        -H 'Content-Type: application/json' \
        -d "{\"model\":\"${VOICE_MODEL}\",\"input\":\"${MESSAGE}\",\"voice\":\"${VOICE_NAME}\"}" \
        2>/dev/null | play_tts) &
fi

exit 0
