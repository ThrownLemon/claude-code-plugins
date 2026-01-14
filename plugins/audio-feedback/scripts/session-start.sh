#!/bin/bash
# Session start - play welcome sound and optional voice announcement
# Triggered when a Claude Code session begins

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

# Play sound effect
if [ "$SOUNDS_ENABLED" = "true" ]; then
    if [ -f "${SOUNDS_DIR}/session-start.wav" ]; then
        afplay "${SOUNDS_DIR}/session-start.wav" &
    else
        # Fallback: use system sound
        afplay /System/Library/Sounds/Glass.aiff 2>/dev/null &
    fi
fi

# Voice announcement
if [ "$VOICE_ENABLED" = "true" ]; then
    # Get current working directory name for context
    PROJECT_NAME=$(basename "$(pwd)")

    # Build contextual message
    MESSAGE="Claude Code session started. Working on ${PROJECT_NAME}. Ready to help."

    # Call Kokoro TTS and play audio (fire-and-forget)
    (curl -s "${KOKORO_URL}/v1/audio/speech" \
        -H 'Content-Type: application/json' \
        -d "{\"model\":\"${VOICE_MODEL}\",\"input\":\"${MESSAGE}\",\"voice\":\"${VOICE_NAME}\"}" \
        2>/dev/null | afplay - 2>/dev/null) &
fi

exit 0
