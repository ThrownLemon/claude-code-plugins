# Audio Feedback Sound Files

Place custom `.wav` sound files in this directory to use instead of system sounds.

## Expected Sound Files

| File | Event | Description | Suggested Duration |
|------|-------|-------------|-------------------|
| `tool-complete.wav` | PostToolUse | Quick subtle sound for tool completions | < 0.5s |
| `session-start.wav` | SessionStart | Welcome sound when session begins | < 1s |
| `session-end.wav` | SessionEnd | Farewell sound when session ends | < 1s |
| `prompt-submit.wav` | UserPromptSubmit | Acknowledgment sound for user input | < 0.3s |
| `task-complete.wav` | SubagentStop | Prominent sound for task completion | < 1s |

## System Sound Fallbacks

If custom sounds are not present, the plugin falls back to macOS system sounds:

| Event | System Sound |
|-------|-------------|
| Tool completion | `/System/Library/Sounds/Pop.aiff` |
| Session start | `/System/Library/Sounds/Glass.aiff` |
| Session end | `/System/Library/Sounds/Purr.aiff` |
| Prompt submit | `/System/Library/Sounds/Tink.aiff` |
| Task complete | `/System/Library/Sounds/Hero.aiff` |

## Sound File Requirements

- Format: WAV (recommended) or AIFF
- Sample rate: 44.1kHz or 48kHz
- Bit depth: 16-bit
- Channels: Mono or Stereo
- Keep files small for fast playback

## Customization

1. Create or download your preferred sound files
2. Name them according to the table above
3. Place them in this directory
4. Restart Claude Code for changes to take effect

No configuration changes needed - the scripts automatically detect custom sounds.
