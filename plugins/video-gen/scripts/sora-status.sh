#!/bin/bash
# OpenAI Sora video status check script
# Checks generation status and retrieves video when complete

set -e

VIDEO_ID=""
DOWNLOAD=false
OUTPUT_PATH=""

# Usage function
usage() {
    cat >&2 <<EOF
Usage: $(basename "$0") --video-id ID [options]

Required:
  --video-id ID      Video ID returned from generation request

Options:
  --download         Download video when complete
  --output PATH      Output file path (default: sora_TIMESTAMP.mp4)
  --help             Show this help message

Environment:
  OPENAI_API_KEY     Required. Get from https://platform.openai.com/api-keys
EOF
    exit "${1:-1}"
}

# Parse arguments with validation
while [[ $# -gt 0 ]]; do
    case $1 in
        --video-id)
            if [[ -z "$2" || "$2" == -* ]]; then
                echo "Error: --video-id requires a value" >&2
                usage 1
            fi
            VIDEO_ID="$2"
            shift 2
            ;;
        --download)
            DOWNLOAD=true
            shift
            ;;
        --output)
            if [[ -z "$2" || "$2" == -* ]]; then
                echo "Error: --output requires a value" >&2
                usage 1
            fi
            OUTPUT_PATH="$2"
            shift 2
            ;;
        --help|-h)
            usage 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage 1
            ;;
    esac
done

# Validate required arguments
if [ -z "$VIDEO_ID" ]; then
    echo "Error: --video-id is required" >&2
    usage 1
fi

# Check API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY environment variable not set" >&2
    exit 1
fi

# API endpoint
API_BASE="https://api.openai.com/v1"

# Get video status
RESPONSE=$(curl -sS --connect-timeout 30 --max-time 60 -X GET \
    "${API_BASE}/videos/${VIDEO_ID}" \
    -H "Authorization: Bearer ${OPENAI_API_KEY}")

# Check for errors
if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    ERROR_MSG=$(echo "$RESPONSE" | jq -r '.error.message // "Unknown error"')
    echo "Error: $ERROR_MSG" >&2
    jq -n --arg error "$ERROR_MSG" '{"status": "error", "error": $error}'
    exit 1
fi

# Extract status information
STATUS=$(echo "$RESPONSE" | jq -r '.status // "unknown"')

case "$STATUS" in
    queued)
        echo "Status: QUEUED" >&2
        echo "Video is waiting to be processed..." >&2
        jq -n '{"status": "queued"}'
        ;;

    preprocessing)
        echo "Status: PREPROCESSING" >&2
        echo "Video is being prepared for generation..." >&2
        jq -n '{"status": "preprocessing"}'
        ;;

    processing|in_progress)
        PROGRESS=$(echo "$RESPONSE" | jq -r '.progress // null')
        echo "Status: PROCESSING" >&2
        if [ "$PROGRESS" != "null" ]; then
            echo "Progress: ${PROGRESS}%" >&2
            # Use try/catch to safely handle non-numeric progress values
            jq -n --arg progress "$PROGRESS" '{"status": "processing", "progress": (try ($progress | tonumber) catch null)}'
        else
            jq -n '{"status": "processing"}'
        fi
        ;;

    completed)
        echo "Status: COMPLETED" >&2

        # Get video content URL from /content endpoint
        CONTENT_RESPONSE=$(curl -sS --connect-timeout 30 --max-time 60 -X GET \
            "${API_BASE}/videos/${VIDEO_ID}/content" \
            -H "Authorization: Bearer ${OPENAI_API_KEY}")

        # Check for errors in content response
        if echo "$CONTENT_RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
            ERROR_MSG=$(echo "$CONTENT_RESPONSE" | jq -r '.error.message // "Failed to get video content"')
            echo "Error getting video content: $ERROR_MSG" >&2
            jq -n --arg error "$ERROR_MSG" '{"status": "completed", "error": $error}'
            exit 1
        fi

        # Extract video URL - may be direct URL or download_url field
        VIDEO_URL=$(echo "$CONTENT_RESPONSE" | jq -r '.download_url // .url // empty')

        if [ -z "$VIDEO_URL" ]; then
            echo "Warning: No video URL in response" >&2
            jq -n '{"status": "failed", "error": "missing_video_url"}'
            exit 1
        fi

        echo "Video URL: $VIDEO_URL" >&2

        # Check if output includes audio
        HAS_AUDIO=$(echo "$RESPONSE" | jq -r '.has_audio // false')
        if [ "$HAS_AUDIO" = "true" ]; then
            echo "Audio: Included" >&2
        fi

        # Download if requested
        if [ "$DOWNLOAD" = true ]; then
            if [ -z "$OUTPUT_PATH" ]; then
                OUTPUT_PATH="sora_$(date +%Y%m%d_%H%M%S).mp4"
            fi

            echo "Downloading video to: $OUTPUT_PATH" >&2
            if ! curl -fSL --connect-timeout 30 --max-time 300 -o "$OUTPUT_PATH" "$VIDEO_URL"; then
                rm -f "$OUTPUT_PATH"
                echo "Error: Download failed" >&2
                jq -n --arg url "$VIDEO_URL" '{"status": "completed", "videoUrl": $url, "error": "download_failed"}'
                exit 1
            fi
            echo "Download complete!" >&2

            jq -n --arg url "$VIDEO_URL" --arg path "$OUTPUT_PATH" --argjson audio "$HAS_AUDIO" \
                '{"status": "completed", "videoUrl": $url, "savedTo": $path, "hasAudio": $audio}'
        else
            jq -n --arg url "$VIDEO_URL" --argjson audio "$HAS_AUDIO" \
                '{"status": "completed", "videoUrl": $url, "hasAudio": $audio}'
        fi
        ;;

    failed)
        ERROR=$(echo "$RESPONSE" | jq -r '.error // "Unknown error"')
        FAILURE_REASON=$(echo "$RESPONSE" | jq -r '.failure_reason // null')

        echo "Status: FAILED" >&2
        echo "Error: $ERROR" >&2
        if [ "$FAILURE_REASON" != "null" ]; then
            echo "Reason: $FAILURE_REASON" >&2
        fi

        jq -n --arg error "$ERROR" --arg reason "$FAILURE_REASON" \
            'if $reason == "null" then {"status": "failed", "error": $error} else {"status": "failed", "error": $error, "reason": $reason} end'
        exit 1
        ;;

    canceled)
        echo "Status: CANCELED" >&2
        echo "Video generation was canceled" >&2
        jq -n '{"status": "canceled"}'
        ;;

    *)
        echo "Status: $STATUS" >&2
        jq -n --arg status "$STATUS" '{"status": $status}'
        ;;
esac
