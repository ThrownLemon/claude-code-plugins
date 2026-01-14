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

# Play sound effect in background (fire-and-forget)
if [ -f "${SOUNDS_DIR}/prompt-submit.wav" ]; then
    afplay "${SOUNDS_DIR}/prompt-submit.wav" &
else
    # Fallback: use system sound
    afplay /System/Library/Sounds/Tink.aiff 2>/dev/null &
fi

exit 0
