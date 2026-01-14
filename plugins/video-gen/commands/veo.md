---
description: Generate a video using Google Veo (via Gemini API)
arguments:
  - name: prompt
    description: Text description of the video to generate
    required: true
  - name: duration
    description: "Video duration in seconds: 4, 6, or 8 (default: 6)"
    required: false
  - name: aspect
    description: "Aspect ratio: 16:9 or 9:16 (default: 16:9)"
    required: false
  - name: resolution
    description: "Video resolution: 720p, 1080p, or 4k (default: 1080p)"
    required: false
  - name: model
    description: "Veo model: veo-3.1-generate-preview, veo-3.1-fast-generate-preview, veo-2.0-generate-001"
    required: false
  - name: negative
    description: Negative prompt - things to avoid in the video
    required: false
  - name: image
    description: Path to image for first frame reference
    required: false
  - name: output
    description: Output file path (default: veo_<timestamp>.mp4)
    required: false
---

# Google Veo Video Generation

Generate videos using Google's Veo models via the Gemini API.

## What This Does

This command delegates to the `video-generator` subagent with Veo-specific options:

1. **Verify Setup**
   - Check GOOGLE_API_KEY environment variable
   - Validate model selection

2. **Submit Generation Request**
   - Send prompt and parameters to Veo API
   - Receive operation ID for tracking

3. **Poll for Completion**
   - Monitor long-running operation status
   - Report progress updates

4. **Download Video**
   - Retrieve completed video
   - Save to specified or default path

## Available Models

- **veo-3.1-generate-preview** - Latest model, best quality (default)
- **veo-3.1-fast-generate-preview** - Faster generation, good quality
- **veo-2.0-generate-001** - Previous generation, stable

## Parameters

- **prompt** (required): Detailed description of the video content
- **duration**: Length in seconds
  - `4` - Short clip
  - `6` - Standard (default)
  - `8` - Extended
- **aspect**: Aspect ratio
  - `16:9` - Landscape (default)
  - `9:16` - Portrait/vertical
- **resolution**: Video quality
  - `720p` - HD
  - `1080p` - Full HD (default)
  - `4k` - Ultra HD
- **model**: Specific Veo model to use
- **negative**: Things to exclude from generation
- **image**: First frame reference image (base64 or path)
- **output**: Save path for video file

## Examples

```
/video-gen:veo --prompt "A butterfly emerging from a cocoon in slow motion"
/video-gen:veo --prompt "Ocean waves at sunset" --duration 8 --resolution 4k
/video-gen:veo --prompt "Abstract geometric patterns" --negative "text, watermark"
/video-gen:veo --prompt "Continue this scene" --image ./frame.png --duration 4
```

## API Details

- Endpoint: `https://generativelanguage.googleapis.com/v1beta`
- Uses long-running operations pattern
- Polling interval: 5-10 seconds
- Typical generation time: 1-5 minutes

## Environment Variables

- `GOOGLE_API_KEY` - Required. Get from Google AI Studio.

Use the `video-generator` subagent with provider set to "veo". Pass the arguments:
- provider: "veo"
- prompt: $ARGUMENTS.prompt
- duration: $ARGUMENTS.duration or 6
- aspect: $ARGUMENTS.aspect or "16:9"
- resolution: $ARGUMENTS.resolution or "1080p"
- model: $ARGUMENTS.model or "veo-3.1-generate-preview"
- negative: $ARGUMENTS.negative or none
- image: $ARGUMENTS.image or none
- output: $ARGUMENTS.output or auto-generate filename
