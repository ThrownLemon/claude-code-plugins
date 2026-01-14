#!/bin/bash
# Session start - play welcome sound and optional voice announcement
# Triggered when a Claude Code session begins

# Configuration via environment variables:
# AUDIO_FEEDBACK_SOUNDS: Enable sound effects (true/1/yes, default: true)
# AUDIO_FEEDBACK_VOICE: Enable voice announcements (true/1/yes, default: true)
# AUDIO_FEEDBACK_VOICE_MODEL: TTS model (default: kokoro)
# AUDIO_FEEDBACK_VOICE_NAME: TTS voice (default: af_heart)
# KOKORO_TTS_URL: Kokoro TTS endpoint (default: http://localhost:8880)

# Get script directory and source shared library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOUNDS_DIR="${SCRIPT_DIR}/../sounds"
source "${SCRIPT_DIR}/lib/audio.sh"

# Load and normalize configuration
SOUNDS_ENABLED=$(normalize_bool "${AUDIO_FEEDBACK_SOUNDS:-true}")
VOICE_ENABLED=$(normalize_bool "${AUDIO_FEEDBACK_VOICE:-true}")
VOICE_MODEL="${AUDIO_FEEDBACK_VOICE_MODEL:-kokoro}"
VOICE_NAME="${AUDIO_FEEDBACK_VOICE_NAME:-af_heart}"
KOKORO_URL="${KOKORO_TTS_URL:-http://localhost:8880}"

# Play sound effect
if [ "$SOUNDS_ENABLED" = "true" ]; then
    SOUND_FILE=$(find_sound "session-start" "/System/Library/Sounds/Glass.aiff")
    if [ -n "$SOUND_FILE" ]; then
        play_sound "$SOUND_FILE"
    fi
fi

# Voice announcement
if [ "$VOICE_ENABLED" = "true" ]; then
    # Get current working directory name for context
    PROJECT_NAME=$(basename "$(pwd)")

    # Build contextual message
    MESSAGE="Claude Code session started. Working on ${PROJECT_NAME}. Ready to help."

    # Speak using TTS (fire-and-forget)
    speak_tts "$MESSAGE"
fi

exit 0
