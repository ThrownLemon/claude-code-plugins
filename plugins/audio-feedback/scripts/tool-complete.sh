#!/bin/bash
# Quick sound for tool completions
# Plays a subtle sound when any tool completes

# Configuration via environment variables:
# AUDIO_FEEDBACK_SOUNDS: Enable sound effects (default: true)
# AUDIO_FEEDBACK_VOICE: Enable voice announcements (default: false for tool completions)
# AUDIO_FEEDBACK_TOOL_SOUND: Specific setting for tool sounds (default: true)

SOUNDS_ENABLED="${AUDIO_FEEDBACK_SOUNDS:-true}"
TOOL_SOUND_ENABLED="${AUDIO_FEEDBACK_TOOL_SOUND:-true}"

# Get script directory for sound file paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOUNDS_DIR="${SCRIPT_DIR}/../sounds"

# Exit if sounds disabled
if [ "$SOUNDS_ENABLED" != "true" ] || [ "$TOOL_SOUND_ENABLED" != "true" ]; then
    exit 0
fi

# Play sound effect in background (fire-and-forget)
if [ -f "${SOUNDS_DIR}/tool-complete.wav" ]; then
    afplay "${SOUNDS_DIR}/tool-complete.wav" &
else
    # Fallback: use system sound
    afplay /System/Library/Sounds/Pop.aiff 2>/dev/null &
fi

exit 0
