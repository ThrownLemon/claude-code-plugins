#!/bin/bash
# Google Veo operation status check script
# Polls long-running operation and retrieves video when complete

set -e

OPERATION_ID=""
DOWNLOAD=false
OUTPUT_PATH=""

# Usage function
usage() {
    cat >&2 <<EOF
Usage: $(basename "$0") --operation-id ID [options]

Required:
  --operation-id ID  Operation ID returned from generation request
                     Format: models/{model}/operations/{operation-id}

Options:
  --download         Download video when complete
  --output PATH      Output file path (default: veo_TIMESTAMP.mp4)
  --help             Show this help message

Environment:
  GOOGLE_API_KEY     Required. Get from https://aistudio.google.com/app/apikey
EOF
    exit "${1:-1}"
}

# Parse arguments with validation
while [[ $# -gt 0 ]]; do
    case $1 in
        --operation-id)
            if [[ -z "$2" || "$2" == -* ]]; then
                echo "Error: --operation-id requires a value" >&2
                usage 1
            fi
            OPERATION_ID="$2"
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
if [ -z "$OPERATION_ID" ]; then
    echo "Error: --operation-id is required" >&2
    usage 1
fi

# Check API key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "Error: GOOGLE_API_KEY environment variable not set" >&2
    exit 1
fi

# API endpoint
API_BASE="https://generativelanguage.googleapis.com/v1beta"

# Get operation status
RESPONSE=$(curl -sS --connect-timeout 30 --max-time 60 -X GET \
    "${API_BASE}/${OPERATION_ID}" \
    -H "x-goog-api-key: ${GOOGLE_API_KEY}")

# Check for errors
if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    ERROR_MSG=$(echo "$RESPONSE" | jq -r '.error.message // "Unknown error"')
    echo "Error: $ERROR_MSG" >&2
    jq -n --arg error "$ERROR_MSG" '{"status": "error", "error": $error}'
    exit 1
fi

# Extract status information
DONE=$(echo "$RESPONSE" | jq -r '.done // false')
METADATA=$(echo "$RESPONSE" | jq -r '.metadata // {}')

# Check if operation is complete
if [ "$DONE" = "true" ]; then
    # Check for failure in response
    if echo "$RESPONSE" | jq -e '.response.error' > /dev/null 2>&1; then
        ERROR_MSG=$(echo "$RESPONSE" | jq -r '.response.error.message // "Generation failed"')
        echo "Status: FAILED" >&2
        echo "Error: $ERROR_MSG" >&2
        jq -n --arg error "$ERROR_MSG" '{"status": "failed", "error": $error}'
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
            if ! curl -fSL --connect-timeout 30 --max-time 300 -o "$OUTPUT_PATH" "$VIDEO_URI"; then
                rm -f "$OUTPUT_PATH"
                echo "Error: Download failed" >&2
                jq -n --arg uri "$VIDEO_URI" '{"status": "succeeded", "videoUri": $uri, "error": "download_failed"}'
                exit 1
            fi

            # Verify file was created and has content
            if [ ! -s "$OUTPUT_PATH" ]; then
                rm -f "$OUTPUT_PATH"
                echo "Error: Downloaded file is empty" >&2
                jq -n --arg uri "$VIDEO_URI" '{"status": "succeeded", "videoUri": $uri, "error": "empty_file"}'
                exit 1
            fi

            echo "Download complete!" >&2
            echo "Video saved to: $OUTPUT_PATH" >&2

            jq -n --arg uri "$VIDEO_URI" --arg path "$OUTPUT_PATH" \
                '{"status": "succeeded", "videoUri": $uri, "savedTo": $path}'
        else
            jq -n --arg uri "$VIDEO_URI" '{"status": "succeeded", "videoUri": $uri}'
        fi
    else
        echo "Status: SUCCEEDED (no video URL in response)" >&2
        echo "Full response:" >&2
        echo "$RESPONSE" | jq '.' >&2
        jq -n '{"status": "succeeded", "error": "missing_video_uri"}'
    fi
else
    # Still running - extract progress if available
    STATE=$(echo "$METADATA" | jq -r '.state // "RUNNING"')
    PROGRESS=$(echo "$METADATA" | jq -r '.progressPercent // null')

    echo "Status: $STATE" >&2
    if [ "$PROGRESS" != "null" ]; then
        echo "Progress: ${PROGRESS}%" >&2
        jq -n --arg state "$STATE" --arg progress "$PROGRESS" \
            '{"status": ($state | ascii_downcase), "progress": ($progress | tonumber)}'
    else
        jq -n --arg state "$STATE" '{"status": ($state | ascii_downcase)}'
    fi
fi
