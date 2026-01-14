---
description: Generate a video using AI with smart model routing (Google Veo or OpenAI Sora)
arguments:
  - name: prompt
    description: Text description of the video to generate
    required: true
  - name: duration
    description: "Video duration in seconds (Veo: 4,6,8 | Sora: 4,8,12)"
    required: false
  - name: aspect
    description: "Aspect ratio (16:9 or 9:16)"
    required: false
  - name: model
    description: "Specific model: veo-3.1, veo-3.1-fast, veo-2.0, sora-2, sora-2-pro"
    required: false
  - name: resolution
    description: "Video resolution (Veo only: 720p, 1080p, 4k)"
    required: false
  - name: output
    description: Output file path (default: video_<timestamp>.mp4)
    required: false
---

# AI Video Generation

Generate videos from text prompts using either Google Veo or OpenAI Sora with smart model routing.

## What This Does

This command delegates to the `video-generator` subagent which will:

1. **Check API Keys**
   - Verify GOOGLE_API_KEY for Veo
   - Verify OPENAI_API_KEY for Sora
   - Guide through setup if needed

2. **Select Model**
   - If model specified, use that provider
   - Otherwise, pick based on availability and request parameters
   - Prefer Veo for 4K resolution requests
   - Prefer Sora for 12-second duration requests

3. **Generate Video**
   - Submit generation request to selected API
   - Poll for completion status
   - Download and save video file

4. **Show Progress**
   - Display generation status updates
   - Report completion time and output path

## Model Selection Guide

**Google Veo** (requires GOOGLE_API_KEY):
- `veo-3.1` - Latest quality model, up to 8 seconds
- `veo-3.1-fast` - Faster generation, good quality
- `veo-2.0` - Previous generation, stable

**OpenAI Sora** (requires OPENAI_API_KEY):
- `sora-2` - Standard model, up to 12 seconds
- `sora-2-pro` - Higher quality, longer wait times

## Arguments

- **prompt** (required): Description of the video content
- **duration**: Video length in seconds
  - Veo: 4, 6, or 8 seconds
  - Sora: 4, 8, or 12 seconds
- **aspect**: Aspect ratio
  - `16:9` - Landscape (default)
  - `9:16` - Portrait/vertical
- **model**: Specific model to use
- **resolution**: Video resolution (Veo only)
  - `720p`, `1080p`, `4k`
- **output**: Save path for the video file

## Examples

```
/video-gen:generate --prompt "A golden retriever playing in autumn leaves"
/video-gen:generate --prompt "Cityscape at sunset" --duration 8 --aspect 16:9
/video-gen:generate --prompt "Abstract flowing colors" --model veo-3.1 --resolution 4k
/video-gen:generate --prompt "Dancing robot" --model sora-2-pro --duration 12
```

## Environment Variables

- `GOOGLE_API_KEY` - Required for Google Veo models
- `OPENAI_API_KEY` - Required for OpenAI Sora models

Use the `video-generator` subagent to perform the generation. Pass the arguments:
- prompt: $ARGUMENTS.prompt
- duration: $ARGUMENTS.duration or auto-select
- aspect: $ARGUMENTS.aspect or "16:9"
- model: $ARGUMENTS.model or auto-select
- resolution: $ARGUMENTS.resolution or "1080p"
- output: $ARGUMENTS.output or auto-generate filename
