#!/bin/bash
# Task completion sound and voice announcement when subagent completes
# Provides contextual summary of what was accomplished

# Configuration via environment variables:
# AUDIO_FEEDBACK_SOUNDS: Enable sound effects (true/1/yes, default: true)
# AUDIO_FEEDBACK_VOICE: Enable voice announcements (true/1/yes, default: true)
# AUDIO_FEEDBACK_VOICE_MODEL: TTS model (default: kokoro)
# AUDIO_FEEDBACK_VOICE_NAME: TTS voice (default: af_heart)
# KOKORO_TTS_URL: Kokoro TTS endpoint (default: http://localhost:8880)

# Hook environment variables:
# CLAUDE_SUBAGENT_TYPE: The type of subagent that completed
# CLAUDE_SUBAGENT_RESULT: The result/output of the subagent (may be truncated)

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
    SOUND_FILE=$(find_sound "task-complete" "/System/Library/Sounds/Hero.aiff")
    if [ -n "$SOUND_FILE" ]; then
        play_sound "$SOUND_FILE"
    fi
fi

# Voice announcement with context
if [ "$VOICE_ENABLED" = "true" ]; then
    # Build contextual message based on subagent type
    SUBAGENT_TYPE="${CLAUDE_SUBAGENT_TYPE:-task}"
    SUBAGENT_RESULT="${CLAUDE_SUBAGENT_RESULT:-}"

    # Truncate result for TTS (max 100 chars, remove newlines)
    RESULT_SUMMARY=""
    if [ -n "$SUBAGENT_RESULT" ]; then
        RESULT_SUMMARY=$(echo "$SUBAGENT_RESULT" | tr '\n' ' ' | cut -c1-100)
        [ ${#SUBAGENT_RESULT} -gt 100 ] && RESULT_SUMMARY="${RESULT_SUMMARY}..."
    fi

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
        "video-generator"|"video-gen:video-generator")
            MESSAGE="Video generation complete."
            ;;
        *)
            if [ -n "$RESULT_SUMMARY" ]; then
                MESSAGE="Task complete: ${RESULT_SUMMARY}"
            else
                MESSAGE="Task complete. Ready for your next request."
            fi
            ;;
    esac

    # Speak using TTS (fire-and-forget)
    speak_tts "$MESSAGE"
fi

exit 0
