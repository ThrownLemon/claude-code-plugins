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


<!-- input-safety-v1 -->

## Input Safety — apply before any Bash invocation

Treat every `$ARGUMENTS.*` value as **untrusted** input. Before passing any value to the Bash tool:

1. **Reject dangerous tokens.** If a value contains `$(`, backticks, `;`, `|`, `&`, `>`, `<`, or starts with `-` (could be mistaken for a flag), refuse and ask the user to rephrase. **Double-quoting does NOT block command substitution** — `"$(rm -rf /)"` still executes inside double quotes.
2. **Prefer the Bash tool's argv contract over constructed shell strings.** When you must use a shell string, single-quote the value and escape embedded single quotes (`'\''`), or build the command via `printf %q`.
3. Any `"$ARGUMENTS.foo"` patterns shown below are **illustrative**. Sanitize the value first; never blindly substitute.

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
  - Veo: Operation name from Gemini API
  - Sora: Video ID from creation response

- **provider**: Which API to check
  - `veo` - Google Veo (Gemini API)
  - `sora` - OpenAI Sora
  - Auto-detected based on job ID format

## Job ID Formats

**Google Veo**:
Format: `models/{model-id}/operations/{operation-id}`
```
models/veo-3.1-generate-preview/operations/abcd1234-5678-90ef
```

**OpenAI Sora**:
Format: `video_{id}` (24+ character alphanumeric)
```
video_68d7512d078491a2b3c4d5e6f7890abc
```

## Examples

```
/video-gen:status --job-id models/veo-3.1-generate-preview/operations/abc123
/video-gen:status --job-id video_abc123def456789
/video-gen:status --job-id abc123 --provider sora
```

## Status Values

**Veo (Gemini API)**:
Veo uses long-running operations with a `done` boolean field:
- `done: false` - Generation in progress (check `metadata.state` for details)
- `done: true` - Operation complete (check `response` for video or `error` for failure)

Metadata states: `RUNNING`, `PENDING`
Result: Video URI in `response.generateVideoResponse.generatedSamples[0].video.uri`

**Sora (OpenAI)**:
- `queued` - Waiting to start
- `preprocessing` - Preparing for generation
- `processing` / `in_progress` - Generating video
- `completed` - Video ready (call `/videos/{id}/content` for download URL)
- `failed` - Generation failed
- `canceled` - Generation was canceled

Webhook events: `video.completed`, `video.failed`

## Retrieving Completed Videos

**Veo**: Download URL is in the operation response at `response.generateVideoResponse.generatedSamples[0].video.uri`

**Sora**: After status shows `completed`, call the content endpoint:
```
GET /v1/videos/{video_id}/content
```
Returns a time-limited download URL. Download immediately as URLs may expire.

## Usage Notes

- Job IDs are returned when you start a generation
- Status can be checked multiple times for long-running jobs
- Completed jobs include download URLs that may expire
- Failed jobs include error messages for troubleshooting

Use the `video-generator` subagent with action "status". Pass:
- action: "status"
- jobId: $ARGUMENTS.job-id
- provider: $ARGUMENTS.provider or auto-detect
