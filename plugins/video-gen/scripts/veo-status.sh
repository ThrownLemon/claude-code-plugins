#!/bin/bash
# Google Veo operation status check script
# Polls long-running operation and retrieves video when complete

set -e

OPERATION_ID=""
DOWNLOAD=false
OUTPUT_PATH=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --operation-id)
            OPERATION_ID="$2"
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
if [ -z "$OPERATION_ID" ]; then
    echo "Error: --operation-id is required" >&2
    exit 1
fi

# Check API key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "Error: GOOGLE_API_KEY environment variable not set" >&2
    exit 1
fi

# API endpoint
API_BASE="https://generativelanguage.googleapis.com/v1beta"

# Get operation status
RESPONSE=$(curl -s -X GET \
    "${API_BASE}/${OPERATION_ID}" \
    -H "x-goog-api-key: ${GOOGLE_API_KEY}")

# Check for errors
if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    ERROR_MSG=$(echo "$RESPONSE" | jq -r '.error.message // "Unknown error"')
    echo "Error: $ERROR_MSG" >&2
    exit 1
fi

# Extract status information
DONE=$(echo "$RESPONSE" | jq -r '.done // false')
METADATA=$(echo "$RESPONSE" | jq -r '.metadata // {}')

# Check if operation is complete
if [ "$DONE" = "true" ]; then
    # Check for success or failure
    if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
        ERROR_MSG=$(echo "$RESPONSE" | jq -r '.error.message // "Generation failed"')
        echo "Status: FAILED" >&2
        echo "Error: $ERROR_MSG" >&2
        echo '{"status": "FAILED", "error": "'"$ERROR_MSG"'"}'
        exit 1
    fi

    # Extract video result
    RESULT=$(echo "$RESPONSE" | jq -r '.response // {}')
    VIDEO_URI=$(echo "$RESULT" | jq -r '.generatedVideos[0].video.uri // empty')

    if [ -n "$VIDEO_URI" ]; then
        echo "Status: SUCCEEDED" >&2
        echo "Video URL: $VIDEO_URI" >&2

        # Download if requested
        if [ "$DOWNLOAD" = true ]; then
            if [ -z "$OUTPUT_PATH" ]; then
                OUTPUT_PATH="veo_$(date +%Y%m%d_%H%M%S).mp4"
            fi

            echo "Downloading video to: $OUTPUT_PATH" >&2
            curl -s -o "$OUTPUT_PATH" "$VIDEO_URI"
            echo "Download complete!" >&2

            echo '{"status": "SUCCEEDED", "videoUri": "'"$VIDEO_URI"'", "savedTo": "'"$OUTPUT_PATH"'"}'
        else
            echo '{"status": "SUCCEEDED", "videoUri": "'"$VIDEO_URI"'"}'
        fi
    else
        echo "Status: SUCCEEDED (no video URL in response)" >&2
        echo "$RESPONSE" | jq '.'
    fi
else
    # Still running - extract progress if available
    STATE=$(echo "$METADATA" | jq -r '.state // "RUNNING"')
    PROGRESS=$(echo "$METADATA" | jq -r '.progressPercent // "unknown"')

    echo "Status: $STATE" >&2
    if [ "$PROGRESS" != "unknown" ] && [ "$PROGRESS" != "null" ]; then
        echo "Progress: ${PROGRESS}%" >&2
    fi

    echo '{"status": "'"$STATE"'", "progress": "'"$PROGRESS"'"}'
fi
