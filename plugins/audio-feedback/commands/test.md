---
description: Test audio feedback sounds and voice announcements
arguments:
  - name: type
    description: "What to test: 'sounds', 'voice', or 'all' (default: all)"
    required: false
---

# Test Audio Feedback

Test the audio feedback plugin to verify sounds and voice announcements are working.

## Test Types

- `sounds` - Test all sound effects only
- `voice` - Test voice announcements only
- `all` - Test both sounds and voice (default)

## Steps

### 1. Check Prerequisites

First, verify the audio system is available:

```bash
# Check if afplay is available (should be on macOS)
which afplay
```

If testing voice, check Kokoro TTS:

```bash
# Check if Kokoro TTS is running
curl -s http://localhost:8880/v1/models 2>/dev/null && echo "Kokoro TTS is available" || echo "Kokoro TTS not available"
```

### 2. Test Sound Effects

If `$ARGUMENTS.type` is `sounds` or `all`, test each sound:

```bash
# Test tool completion sound
echo "Testing tool completion sound..."
afplay /System/Library/Sounds/Pop.aiff

# Test session start sound
echo "Testing session start sound..."
afplay /System/Library/Sounds/Glass.aiff

# Test session end sound
echo "Testing session end sound..."
afplay /System/Library/Sounds/Purr.aiff

# Test prompt submit sound
echo "Testing prompt submit sound..."
afplay /System/Library/Sounds/Tink.aiff

# Test task completion sound
echo "Testing task completion sound..."
afplay /System/Library/Sounds/Hero.aiff
```

### 3. Test Voice Announcements

If `$ARGUMENTS.type` is `voice` or `all`, test TTS:

```bash
# Test voice announcement
curl -s http://localhost:8880/v1/audio/speech \
  -H 'Content-Type: application/json' \
  -d '{"model":"kokoro","input":"Audio feedback test successful. Voice announcements are working.","voice":"af_heart"}' \
  | afplay -
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
- Try: `afplay /System/Library/Sounds/Ping.aiff`

### Voice not working
- Ensure Kokoro TTS server is running
- Check the endpoint URL: `curl http://localhost:8880/v1/models`
- Verify network connectivity

### Custom sounds not playing
- Check sound files exist in `plugins/audio-feedback/sounds/`
- Verify file format is WAV or AIFF
- Try playing directly: `afplay plugins/audio-feedback/sounds/tool-complete.wav`
