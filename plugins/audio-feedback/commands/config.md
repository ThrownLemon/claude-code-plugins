---
description: Configure audio feedback plugin settings
---

# Audio Feedback Plugin Configuration

View and modify audio feedback settings for sound effects and voice announcements.

## Configuration Options

### Sound Effects

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| All sounds | `AUDIO_FEEDBACK_SOUNDS` | `true` | Master toggle for all sound effects |
| Tool sounds | `AUDIO_FEEDBACK_TOOL_SOUND` | `true` | Sound on tool completion |
| Prompt sounds | `AUDIO_FEEDBACK_PROMPT_SOUND` | `true` | Sound on prompt submission |

### Voice Announcements

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| Voice enabled | `AUDIO_FEEDBACK_VOICE` | `true` | Master toggle for voice announcements |
| Voice model | `AUDIO_FEEDBACK_VOICE_MODEL` | `kokoro` | TTS model name |
| Voice name | `AUDIO_FEEDBACK_VOICE_NAME` | `af_heart` | TTS voice selection |
| TTS endpoint | `KOKORO_TTS_URL` | `http://localhost:8880` | Kokoro TTS server URL |

## Events and Feedback

| Event | Sound | Voice | Control Variables |
|-------|-------|-------|-------------------|
| SessionStart | Yes | Yes | `AUDIO_FEEDBACK_SOUNDS`, `AUDIO_FEEDBACK_VOICE` |
| SessionEnd | Yes | Yes | `AUDIO_FEEDBACK_SOUNDS`, `AUDIO_FEEDBACK_VOICE` |
| UserPromptSubmit | Yes | No | `AUDIO_FEEDBACK_SOUNDS`, `AUDIO_FEEDBACK_PROMPT_SOUND` |
| PostToolUse | Yes | No | `AUDIO_FEEDBACK_SOUNDS`, `AUDIO_FEEDBACK_TOOL_SOUND` |
| SubagentStop | Yes | Yes | `AUDIO_FEEDBACK_SOUNDS`, `AUDIO_FEEDBACK_VOICE` |

**Note**: SessionStart, SessionEnd, and SubagentStop events only respect the master toggles (`AUDIO_FEEDBACK_SOUNDS` and `AUDIO_FEEDBACK_VOICE`). They cannot be toggled individually.

## Configuring Settings

Settings are controlled via environment variables. To modify:

### Option 1: Shell Environment
```bash
export AUDIO_FEEDBACK_SOUNDS=true
export AUDIO_FEEDBACK_VOICE=true
export AUDIO_FEEDBACK_VOICE_NAME=af_heart
export KOKORO_TTS_URL=http://localhost:8880
```

### Option 2: Project .env File
Create or edit `.env` in your project root:
```
AUDIO_FEEDBACK_SOUNDS=true
AUDIO_FEEDBACK_VOICE=true
AUDIO_FEEDBACK_VOICE_NAME=af_heart
KOKORO_TTS_URL=http://localhost:8880
```

### Option 3: Shell RC File
Add exports to `~/.zshrc` or `~/.bashrc` for persistent settings.

## Custom Sounds

Place custom sound files in the plugin's `sounds/` directory:
- `tool-complete.wav` or `tool-complete.aiff` - Tool completion
- `session-start.wav` or `session-start.aiff` - Session start
- `session-end.wav` or `session-end.aiff` - Session end
- `prompt-submit.wav` or `prompt-submit.aiff` - Prompt submission
- `task-complete.wav` or `task-complete.aiff` - Task completion

The plugin checks for `.wav` first, then `.aiff`/`.aif`. If custom sounds aren't present, system sounds are used as fallback (macOS only).

## Available Kokoro Voices

Common voice options for `AUDIO_FEEDBACK_VOICE_NAME`:
- `af_heart` - Female, warm (default)
- `af_bella` - Female, professional
- `am_adam` - Male, neutral
- `am_michael` - Male, authoritative

Check your Kokoro TTS server for all available voices.

## Platform Support

The plugin automatically detects available audio players:
- **macOS**: `afplay` (built-in)
- **Linux**: `paplay` (PulseAudio), `aplay` (ALSA), or `play` (SoX)

If no audio player is found, the plugin silently skips playback without errors.

## Requirements

- **Sound effects**: Audio player available on system (see Platform Support)
- **Voice announcements**: Kokoro TTS server running at the configured endpoint

## Steps

1. Display current configuration status
2. Check if Kokoro TTS is available
3. Show available voice options if TTS is running
4. Guide user on how to modify settings
