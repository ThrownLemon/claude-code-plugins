---
description: Generate a video using OpenAI Sora
arguments:
  - name: prompt
    description: Text description of the video to generate
    required: true
  - name: duration
    description: "Video duration in seconds: 4, 8, or 12 (default: 8)"
    required: false
  - name: aspect
    description: "Aspect ratio: 16:9, 9:16, or 1:1 (default: 16:9)"
    required: false
  - name: model
    description: "Sora model: sora-2 or sora-2-pro (default: sora-2)"
    required: false
  - name: image
    description: Path to reference image for style/content guidance
    required: false
  - name: output
    description: Output file path (default: sora_<timestamp>.mp4)
    required: false
---

# OpenAI Sora Video Generation

Generate videos using OpenAI's Sora models.

## What This Does

This command delegates to the `video-generator` subagent with Sora-specific options:

1. **Verify Setup**
   - Check OPENAI_API_KEY environment variable
   - Validate model and parameters

2. **Submit Generation Request**
   - POST multipart/form-data to /v1/videos endpoint
   - Fields: `model`, `prompt`, `seconds`, `size`, `input_reference` (optional)
   - Receive video ID for tracking

3. **Poll for Completion**
   - GET /v1/videos/{id} for status
   - Status progression: `queued` -> `preprocessing` -> `processing` -> `completed`

4. **Download Video**
   - GET /v1/videos/{id}/content for download URL
   - Save to specified or default path
   - Note: Download URLs are time-limited, download immediately

## Available Models

- **sora-2** - Standard model, fast generation (default)
  - Snapshots: `sora-2-2025-10-06`, `sora-2-2025-12-08`
- **sora-2-pro** - Professional quality, longer wait times
  - Snapshots: `sora-2-pro-2025-10-06`

## Parameters

- **prompt** (required): Detailed description of the video content
- **duration**: Length in seconds (maps to API `seconds` field)
  - `4` - Short clip
  - `8` - Standard (default)
  - `12` - Extended (Sora exclusive)
- **aspect**: Aspect ratio (maps to API `size` field)
  - `16:9` - Landscape 1920x1080 (default)
  - `9:16` - Portrait 1080x1920
  - `1:1` - Square 1080x1080
- **model**: Sora model to use
- **image**: Reference image for guidance (uploaded as `input_reference`)
- **output**: Save path for video file

## Examples

```
/video-gen:sora --prompt "A cat walking on a tightrope over a cityscape"
/video-gen:sora --prompt "Futuristic car commercial" --duration 12 --model sora-2-pro
/video-gen:sora --prompt "Stylized animation" --image ./reference.png --aspect 9:16
```

## API Details

- Base URL: `https://api.openai.com/v1`
- **Create**: POST `/videos` (multipart/form-data)
  - `model`: sora-2 or sora-2-pro
  - `prompt`: Text description
  - `seconds`: 4, 8, or 12
  - `size`: e.g., "1920x1080"
  - `input_reference`: Optional image file
- **Status**: GET `/videos/{id}`
- **Download**: GET `/videos/{id}/content` (returns time-limited URL)

## Generation Status

- **queued** - Request accepted, waiting to start
- **preprocessing** - Preparing for generation
- **processing** - Video being generated
- **completed** - Video ready for download via /content endpoint
- **failed** - Generation failed (error details provided)
- **canceled** - Generation was canceled

## Webhook Events (for integrations)

- `video.completed` - Video generation finished successfully
- `video.failed` - Video generation failed

## Environment Variables

- `OPENAI_API_KEY` - Required. Get from OpenAI platform.

Use the `video-generator` subagent with provider set to "sora". Pass the arguments:
- provider: "sora"
- prompt: $ARGUMENTS.prompt
- duration: $ARGUMENTS.duration or 8
- aspect: $ARGUMENTS.aspect or "16:9"
- model: $ARGUMENTS.model or "sora-2"
- image: $ARGUMENTS.image or none
- output: $ARGUMENTS.output or auto-generate filename
