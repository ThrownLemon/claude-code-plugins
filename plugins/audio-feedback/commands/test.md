---
description: Test audio feedback sounds and voice announcements
arguments:
  - name: type
    description: "What to test: 'sounds', 'voice', or 'all'. Case-insensitive. Invalid values default to 'all'. (default: all)"
    required: false
---


<!-- input-safety-v1 -->

## Input Safety — apply before any Bash invocation

Treat every `$ARGUMENTS.*` value as **untrusted** input. Before passing any value to the Bash tool:

1. **Reject dangerous tokens.** If a value contains `$(`, backticks, `;`, `|`, `&`, `>`, `<`, or starts with `-` (could be mistaken for a flag), refuse and ask the user to rephrase. **Double-quoting does NOT block command substitution** — `"$(rm -rf /)"` still executes inside double quotes.
2. **Prefer the Bash tool's argv contract over constructed shell strings.** When you must use a shell string, single-quote the value and escape embedded single quotes (`'\''`), or build the command via `printf %q`.
3. Any `"$ARGUMENTS.foo"` patterns shown below are **illustrative**. Sanitize the value first; never blindly substitute.

# Test Audio Feedback

Test the audio feedback plugin to verify sounds and voice announcements are working.

## Test Types

- `sounds` - Test all sound effects only
- `voice` - Test voice announcements only
- `all` - Test both sounds and voice (default)

**Note**: Values are case-insensitive (`SOUNDS`, `Sounds`, `sounds` all work). Invalid values fall back to `all`.

## Steps

### 1. Check Prerequisites

First, verify the audio system is available:

```bash
# Detect available audio player
if command -v afplay >/dev/null 2>&1; then
    echo "Audio player: afplay (macOS)"
elif command -v paplay >/dev/null 2>&1; then
    echo "Audio player: paplay (PulseAudio)"
elif command -v aplay >/dev/null 2>&1; then
    echo "Audio player: aplay (ALSA)"
elif command -v play >/dev/null 2>&1; then
    echo "Audio player: play (SoX)"
else
    echo "No audio player found"
fi
```

If testing voice, check Kokoro TTS:

```bash
# Check if Kokoro TTS is running (uses KOKORO_TTS_URL if set)
KOKORO_URL="${KOKORO_TTS_URL:-http://localhost:8880}"
curl -sS --connect-timeout 5 "${KOKORO_URL}/v1/models" 2>/dev/null && echo "Kokoro TTS is available" || echo "Kokoro TTS not available"
```

### 2. Test Sound Effects

If `$ARGUMENTS.type` is `sounds` or `all`, test each sound:

```bash
# Detect player
PLAYER=""
if command -v afplay >/dev/null 2>&1; then
    PLAYER="afplay"
elif command -v paplay >/dev/null 2>&1; then
    PLAYER="paplay"
elif command -v aplay >/dev/null 2>&1; then
    PLAYER="aplay -q"
elif command -v play >/dev/null 2>&1; then
    PLAYER="play -q"
fi

if [ -n "$PLAYER" ]; then
    # Test with system sounds (macOS) or skip if unavailable
    for sound in Pop Glass Purr Tink Hero; do
        file="/System/Library/Sounds/${sound}.aiff"
        if [ -f "$file" ]; then
            echo "Testing ${sound} sound..."
            $PLAYER "$file"
            sleep 0.5
        fi
    done
fi
```

### 3. Test Voice Announcements

If `$ARGUMENTS.type` is `voice` or `all`, test TTS:

```bash
# Test voice announcement using configured endpoint
# Note: afplay (macOS) cannot read stdin — write to a temp file first,
# exactly as the plugin's play_tts() function does at runtime.
KOKORO_URL="${KOKORO_TTS_URL:-http://localhost:8880}"
_TTS_TMP=$(mktemp "${TMPDIR:-/tmp}/tts-test.XXXXXX.mp3")
curl -sS --connect-timeout 5 --max-time 30 "${KOKORO_URL}/v1/audio/speech" \
  -H 'Content-Type: application/json' \
  -d '{"model":"kokoro","input":"Audio feedback test successful. Voice announcements are working.","voice":"af_heart"}' \
  -o "$_TTS_TMP" && afplay "$_TTS_TMP"
rm -f "$_TTS_TMP"
```

### 4. Report Results

After testing, report:
- Which sounds played successfully
- Whether Kokoro TTS responded
- Any errors encountered
- Suggestions for fixing issues

## Troubleshooting

### No sound at all
- Check system volume
- Verify audio output device is connected
- Check audio player availability (see step 1)
- On macOS try: `afplay /System/Library/Sounds/Ping.aiff`
- On Linux try: `paplay /usr/share/sounds/freedesktop/stereo/complete.oga`

### Voice not working
- Ensure Kokoro TTS server is running
- Check the endpoint URL: `curl ${KOKORO_TTS_URL:-http://localhost:8880}/v1/models`
- Verify network connectivity

### Custom sounds not playing
- Check sound files exist in `plugins/audio-feedback/sounds/`
- Verify file format is WAV or AIFF
- Try playing directly with detected player
