#!/bin/bash
# OpenAI Sora video status check script
# Checks generation status and retrieves video when complete

set -e

VIDEO_ID=""
DOWNLOAD=false
OUTPUT_PATH=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --video-id)
            VIDEO_ID="$2"
            shift 2
            ;;
        --download)
            DOWNLOAD=true
            shift
            ;;
        --output)
            OUTPUT_PATH="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Validate required arguments
if [ -z "$VIDEO_ID" ]; then
    echo "Error: --video-id is required" >&2
    exit 1
fi

# Check API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY environment variable not set" >&2
    exit 1
fi

# API endpoint
API_BASE="https://api.openai.com/v1"

# Get video status
RESPONSE=$(curl -s -X GET \
    "${API_BASE}/videos/${VIDEO_ID}" \
    -H "Authorization: Bearer ${OPENAI_API_KEY}")

# Check for errors
if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    ERROR_MSG=$(echo "$RESPONSE" | jq -r '.error.message // "Unknown error"')
    echo "Error: $ERROR_MSG" >&2
    exit 1
fi

# Extract status information
STATUS=$(echo "$RESPONSE" | jq -r '.status // "unknown"')

case "$STATUS" in
    queued)
        echo "Status: QUEUED" >&2
        echo "Video is waiting to be processed..." >&2
        echo '{"status": "queued"}'
        ;;

    in_progress)
        PROGRESS=$(echo "$RESPONSE" | jq -r '.progress // "unknown"')
        echo "Status: IN_PROGRESS" >&2
        if [ "$PROGRESS" != "unknown" ] && [ "$PROGRESS" != "null" ]; then
            echo "Progress: ${PROGRESS}%" >&2
            echo '{"status": "in_progress", "progress": "'"$PROGRESS"'"}'
        else
            echo '{"status": "in_progress"}'
        fi
        ;;

    completed)
        echo "Status: COMPLETED" >&2

        # Extract video URL
        VIDEO_URL=$(echo "$RESPONSE" | jq -r '.output.url // .url // empty')

        if [ -n "$VIDEO_URL" ]; then
            echo "Video URL: $VIDEO_URL" >&2

            # Check if output includes audio
            HAS_AUDIO=$(echo "$RESPONSE" | jq -r '.output.has_audio // false')
            if [ "$HAS_AUDIO" = "true" ]; then
                echo "Audio: Included" >&2
            fi

            # Download if requested
            if [ "$DOWNLOAD" = true ]; then
                if [ -z "$OUTPUT_PATH" ]; then
                    OUTPUT_PATH="sora_$(date +%Y%m%d_%H%M%S).mp4"
                fi

                echo "Downloading video to: $OUTPUT_PATH" >&2
                curl -s -o "$OUTPUT_PATH" "$VIDEO_URL"
                echo "Download complete!" >&2

                echo '{"status": "completed", "videoUrl": "'"$VIDEO_URL"'", "savedTo": "'"$OUTPUT_PATH"'", "hasAudio": '"$HAS_AUDIO"'}'
            else
                echo '{"status": "completed", "videoUrl": "'"$VIDEO_URL"'", "hasAudio": '"$HAS_AUDIO"'}'
            fi
        else
            echo "Warning: No video URL in response" >&2
            echo "$RESPONSE" | jq '.'
        fi
        ;;

    failed)
        ERROR=$(echo "$RESPONSE" | jq -r '.error // "Unknown error"')
        FAILURE_REASON=$(echo "$RESPONSE" | jq -r '.failure_reason // empty')

        echo "Status: FAILED" >&2
        echo "Error: $ERROR" >&2
        if [ -n "$FAILURE_REASON" ]; then
            echo "Reason: $FAILURE_REASON" >&2
        fi

        echo '{"status": "failed", "error": "'"$ERROR"'", "reason": "'"$FAILURE_REASON"'"}'
        exit 1
        ;;

    *)
        echo "Status: $STATUS" >&2
        echo "$RESPONSE" | jq '.'
        ;;
esac
