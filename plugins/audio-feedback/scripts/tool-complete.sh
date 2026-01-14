#!/bin/bash
# Quick sound for tool completions
# Plays a subtle sound when any tool completes

# Configuration via environment variables:
# AUDIO_FEEDBACK_SOUNDS: Enable sound effects (true/1/yes, default: true)
# AUDIO_FEEDBACK_TOOL_SOUND: Specific setting for tool sounds (true/1/yes, default: true)

# Get script directory and source shared library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOUNDS_DIR="${SCRIPT_DIR}/../sounds"
source "${SCRIPT_DIR}/lib/audio.sh"

# Load and normalize configuration
SOUNDS_ENABLED=$(normalize_bool "${AUDIO_FEEDBACK_SOUNDS:-true}")
TOOL_SOUND_ENABLED=$(normalize_bool "${AUDIO_FEEDBACK_TOOL_SOUND:-true}")

# Exit if sounds disabled
if [ "$SOUNDS_ENABLED" != "true" ] || [ "$TOOL_SOUND_ENABLED" != "true" ]; then
    exit 0
fi

# Debounce to prevent too many sounds in rapid succession
if ! should_play_sound "tool-complete"; then
    exit 0
fi

# Play sound effect in background (fire-and-forget)
SOUND_FILE=$(find_sound "tool-complete" "/System/Library/Sounds/Pop.aiff")
if [ -n "$SOUND_FILE" ]; then
    play_sound "$SOUND_FILE"
fi

exit 0
