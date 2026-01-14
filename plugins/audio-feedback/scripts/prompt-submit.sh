#!/bin/bash
# Input acknowledgment sound when user submits a prompt
# Quick audible feedback that input was received

# Configuration via environment variables:
# AUDIO_FEEDBACK_SOUNDS: Enable sound effects (true/1/yes, default: true)
# AUDIO_FEEDBACK_PROMPT_SOUND: Specific setting for prompt sounds (true/1/yes, default: true)

# Get script directory and source shared library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOUNDS_DIR="${SCRIPT_DIR}/../sounds"
source "${SCRIPT_DIR}/lib/audio.sh"

# Load and normalize configuration
SOUNDS_ENABLED=$(normalize_bool "${AUDIO_FEEDBACK_SOUNDS:-true}")
PROMPT_SOUND_ENABLED=$(normalize_bool "${AUDIO_FEEDBACK_PROMPT_SOUND:-true}")

# Exit if sounds disabled
if [ "$SOUNDS_ENABLED" != "true" ] || [ "$PROMPT_SOUND_ENABLED" != "true" ]; then
    exit 0
fi

# Play sound effect in background (fire-and-forget)
SOUND_FILE=$(find_sound "prompt-submit" "/System/Library/Sounds/Tink.aiff")
if [ -n "$SOUND_FILE" ]; then
    play_sound "$SOUND_FILE"
fi

exit 0
