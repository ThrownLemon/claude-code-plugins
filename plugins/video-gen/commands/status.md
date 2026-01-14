---
description: Check the status of a video generation job
arguments:
  - name: job-id
    description: Job/operation ID to check status for
    required: true
  - name: provider
    description: "Provider: veo or sora (auto-detected from job ID format if not specified)"
    required: false
---

# Video Generation Status

Check the status of an ongoing or completed video generation job.

## What This Does

This command checks the status of a video generation job and reports:

1. **Current Status**
   - Queued/pending
   - In progress (with estimated time if available)
   - Completed (with download URL)
   - Failed (with error details)

2. **Progress Information**
   - Time elapsed since submission
   - Estimated completion time (if available)

3. **On Completion**
   - Provide download URL or file path
   - Offer to download if not already saved

## Parameters

- **job-id** (required): The job or operation ID
  - Veo: Long operation name from Gemini API
  - Sora: Video ID from creation response

- **provider**: Which API to check
  - `veo` - Google Veo (Gemini API)
  - `sora` - OpenAI Sora
  - Auto-detected based on job ID format

## Job ID Formats

**Google Veo**:
```
operations/generate-video-xxxxxxxxxxxxx
```

**OpenAI Sora**:
```
vid_xxxxxxxxxxxxxxxxxxxx
```

## Examples

```
/video-gen:status --job-id operations/generate-video-abc123def456
/video-gen:status --job-id vid_abc123def456789
/video-gen:status --job-id abc123 --provider sora
```

## Status Values

**Veo (Gemini API)**:
- `RUNNING` - Generation in progress
- `SUCCEEDED` - Video ready
- `FAILED` - Generation failed
- `CANCELLED` - Operation cancelled

**Sora (OpenAI)**:
- `queued` - Waiting to start
- `in_progress` - Generating
- `completed` - Video ready
- `failed` - Generation failed

## Usage Notes

- Job IDs are returned when you start a generation
- Status can be checked multiple times for long-running jobs
- Completed jobs include download URLs that may expire
- Failed jobs include error messages for troubleshooting

Use the `video-generator` subagent with action "status". Pass:
- action: "status"
- jobId: $ARGUMENTS.job-id
- provider: $ARGUMENTS.provider or auto-detect
