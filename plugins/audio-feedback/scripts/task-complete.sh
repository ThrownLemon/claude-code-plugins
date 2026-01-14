#!/bin/bash
# Task completion sound and voice announcement when subagent completes
# Provides contextual summary of what was accomplished

# Configuration via environment variables:
# AUDIO_FEEDBACK_SOUNDS: Enable sound effects (default: true)
# AUDIO_FEEDBACK_VOICE: Enable voice announcements (default: true)
# AUDIO_FEEDBACK_VOICE_MODEL: TTS model (default: kokoro)
# AUDIO_FEEDBACK_VOICE_NAME: TTS voice (default: af_heart)
# KOKORO_TTS_URL: Kokoro TTS endpoint (default: http://localhost:8880)

# Hook environment variables:
# CLAUDE_SUBAGENT_TYPE: The type of subagent that completed
# CLAUDE_SUBAGENT_RESULT: The result/output of the subagent (may be truncated)

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
    if [ -f "${SOUNDS_DIR}/task-complete.wav" ]; then
        afplay "${SOUNDS_DIR}/task-complete.wav" &
    else
        # Fallback: use system sound (more prominent for task completion)
        afplay /System/Library/Sounds/Hero.aiff 2>/dev/null &
    fi
fi

# Voice announcement with context
if [ "$VOICE_ENABLED" = "true" ]; then
    # Build contextual message based on subagent type
    SUBAGENT_TYPE="${CLAUDE_SUBAGENT_TYPE:-task}"

    case "$SUBAGENT_TYPE" in
        "Explore")
            MESSAGE="Exploration complete. Found the information you needed."
            ;;
        "Plan")
            MESSAGE="Planning complete. Ready to review the implementation plan."
            ;;
        "Bash")
            MESSAGE="Command execution complete."
            ;;
        "cr-reviewer"|"coderabbit:cr-reviewer")
            MESSAGE="Code review complete. Check the results."
            ;;
        "cr-pr-manager"|"coderabbit:cr-pr-manager")
            MESSAGE="PR comment review complete."
            ;;
        *)
            MESSAGE="Task complete. Ready for your next request."
            ;;
    esac

    # Call Kokoro TTS and play audio (fire-and-forget)
    (curl -s "${KOKORO_URL}/v1/audio/speech" \
        -H 'Content-Type: application/json' \
        -d "{\"model\":\"${VOICE_MODEL}\",\"input\":\"${MESSAGE}\",\"voice\":\"${VOICE_NAME}\"}" \
        2>/dev/null | afplay - 2>/dev/null) &
fi

exit 0
