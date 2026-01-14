#!/bin/bash
# OpenAI Sora video generation script
# Uses OpenAI API to generate videos with multipart/form-data

set -e

# Default values
PROMPT=""
DURATION=8
ASPECT="16:9"
MODEL="sora-2"
IMAGE_PATH=""

# Usage function
usage() {
    cat >&2 <<EOF
Usage: $(basename "$0") --prompt "description" [options]

Required:
  --prompt TEXT      Video description prompt

Options:
  --duration NUM     Duration in seconds: 4, 8, or 12 (default: 8)
  --aspect RATIO     Aspect ratio: 16:9, 9:16, or 1:1 (default: 16:9)
  --model MODEL      Model: sora-2 or sora-2-pro (default: sora-2)
  --image PATH       Reference image (file path or URL)
  --help             Show this help message

Environment:
  OPENAI_API_KEY     Required. Get from https://platform.openai.com/api-keys
EOF
    exit "${1:-1}"
}

# Parse arguments with validation
while [[ $# -gt 0 ]]; do
    case $1 in
        --prompt)
            if [[ -z "$2" || "$2" == -* ]]; then
                echo "Error: --prompt requires a value" >&2
                usage 1
            fi
            PROMPT="$2"
            shift 2
            ;;
        --duration)
            if [[ -z "$2" || "$2" == -* ]]; then
                echo "Error: --duration requires a value" >&2
                usage 1
            fi
            DURATION="$2"
            shift 2
            ;;
        --aspect)
            if [[ -z "$2" || "$2" == -* ]]; then
                echo "Error: --aspect requires a value" >&2
                usage 1
            fi
            ASPECT="$2"
            shift 2
            ;;
        --model)
            if [[ -z "$2" || "$2" == -* ]]; then
                echo "Error: --model requires a value" >&2
                usage 1
            fi
            MODEL="$2"
            shift 2
            ;;
        --image)
            if [[ -z "$2" || "$2" == -* ]]; then
                echo "Error: --image requires a value" >&2
                usage 1
            fi
            IMAGE_PATH="$2"
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
if [ -z "$PROMPT" ]; then
    echo "Error: --prompt is required" >&2
    usage 1
fi

# Validate duration (must be 4, 8, or 12)
case "$DURATION" in
    4|8|12) ;;
    *)
        echo "Error: --duration must be 4, 8, or 12 (got: $DURATION)" >&2
        exit 1
        ;;
esac

# Validate model
case "$MODEL" in
    sora-2|sora-2-pro) ;;
    *)
        echo "Error: --model must be sora-2 or sora-2-pro (got: $MODEL)" >&2
        exit 1
        ;;
esac

# Map aspect ratio to size dimensions
case "$ASPECT" in
    16:9) SIZE="1920x1080" ;;
    9:16) SIZE="1080x1920" ;;
    1:1)  SIZE="1080x1080" ;;
    *)
        echo "Error: --aspect must be 16:9, 9:16, or 1:1 (got: $ASPECT)" >&2
        exit 1
        ;;
esac

# Check API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY environment variable not set" >&2
    echo "Get your API key from: https://platform.openai.com/api-keys" >&2
    exit 1
fi

# API endpoint
API_BASE="https://api.openai.com/v1"

# Build curl arguments for multipart/form-data
CURL_ARGS=(
    -X POST
    "${API_BASE}/videos"
    -H "Authorization: Bearer ${OPENAI_API_KEY}"
    -F "model=${MODEL}"
    -F "prompt=${PROMPT}"
    -F "seconds=${DURATION}"
    -F "size=${SIZE}"
)

# Handle image reference if specified
TEMP_IMAGE=""
if [ -n "$IMAGE_PATH" ]; then
    if [ -f "$IMAGE_PATH" ]; then
        # Local file - upload directly
        CURL_ARGS+=(-F "input_reference=@${IMAGE_PATH}")
    elif [[ "$IMAGE_PATH" =~ ^https?:// ]]; then
        # URL - download to temp file first
        TEMP_IMAGE=$(mktemp -t sora_input.XXXXXX)
        echo "Downloading reference image..." >&2
        if ! curl -fsSL --connect-timeout 10 --max-time 60 -o "$TEMP_IMAGE" "$IMAGE_PATH"; then
            rm -f "$TEMP_IMAGE"
            echo "Error: Failed to download reference image from URL" >&2
            exit 1
        fi
        CURL_ARGS+=(-F "input_reference=@${TEMP_IMAGE}")
    else
        echo "Error: Image path is not a valid file or URL: $IMAGE_PATH" >&2
        exit 1
    fi
fi

# Cleanup function for temp files
cleanup() {
    if [ -n "$TEMP_IMAGE" ] && [ -f "$TEMP_IMAGE" ]; then
        rm -f "$TEMP_IMAGE"
    fi
}
trap cleanup EXIT

# Submit generation request
echo "Submitting video generation request to Sora..." >&2
echo "Model: $MODEL" >&2
echo "Duration: ${DURATION}s" >&2
echo "Size: $SIZE (aspect: $ASPECT)" >&2

RESPONSE=$(curl -sS --connect-timeout 30 --max-time 120 "${CURL_ARGS[@]}")

# Check for errors
if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    ERROR_MSG=$(echo "$RESPONSE" | jq -r '.error.message // "Unknown error"')
    ERROR_TYPE=$(echo "$RESPONSE" | jq -r '.error.type // "unknown"')
    echo "Error: API request failed" >&2
    echo "Type: $ERROR_TYPE" >&2
    echo "Message: $ERROR_MSG" >&2
    exit 1
fi

# Extract video ID
VIDEO_ID=$(echo "$RESPONSE" | jq -r '.id // empty')

if [ -z "$VIDEO_ID" ]; then
    echo "Error: No video ID returned" >&2
    echo "Response: $RESPONSE" >&2
    exit 1
fi

# Get initial status
STATUS=$(echo "$RESPONSE" | jq -r '.status // "queued"')

echo "Generation started successfully!" >&2
echo "Video ID: $VIDEO_ID" >&2
echo "Initial status: $STATUS" >&2

# Output the video ID for polling
echo "$VIDEO_ID"
