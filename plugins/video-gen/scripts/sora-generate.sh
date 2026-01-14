#!/bin/bash
# OpenAI Sora video generation script
# Uses OpenAI API to generate videos

set -e

# Default values
PROMPT=""
DURATION=8
ASPECT="16:9"
MODEL="sora-2"
IMAGE_PATH=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --prompt)
            PROMPT="$2"
            shift 2
            ;;
        --duration)
            DURATION="$2"
            shift 2
            ;;
        --aspect)
            ASPECT="$2"
            shift 2
            ;;
        --model)
            MODEL="$2"
            shift 2
            ;;
        --image)
            IMAGE_PATH="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Validate required arguments
if [ -z "$PROMPT" ]; then
    echo "Error: --prompt is required" >&2
    exit 1
fi

# Check API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY environment variable not set" >&2
    echo "Get your API key from: https://platform.openai.com/api-keys" >&2
    exit 1
fi

# API endpoint
API_BASE="https://api.openai.com/v1"

# Build the request payload
REQUEST_BODY=$(cat <<EOF
{
  "model": "${MODEL}",
  "prompt": $(echo "$PROMPT" | jq -Rs .),
  "duration": ${DURATION},
  "aspect_ratio": "${ASPECT}"
}
EOF
)

# Add image reference if specified
if [ -n "$IMAGE_PATH" ] && [ -f "$IMAGE_PATH" ]; then
    # Read and base64 encode the image
    IMAGE_B64=$(base64 -i "$IMAGE_PATH" | tr -d '\n')
    MIME_TYPE=$(file --mime-type -b "$IMAGE_PATH")

    REQUEST_BODY=$(echo "$REQUEST_BODY" | jq --arg img "data:${MIME_TYPE};base64,${IMAGE_B64}" \
        '.input_reference = $img')
elif [ -n "$IMAGE_PATH" ]; then
    # Assume it's a URL
    REQUEST_BODY=$(echo "$REQUEST_BODY" | jq --arg img "$IMAGE_PATH" \
        '.input_reference = $img')
fi

# Submit generation request
echo "Submitting video generation request to Sora..." >&2
echo "Model: $MODEL" >&2
echo "Duration: ${DURATION}s" >&2
echo "Aspect: $ASPECT" >&2

RESPONSE=$(curl -s -X POST \
    "${API_BASE}/videos" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${OPENAI_API_KEY}" \
    -d "$REQUEST_BODY")

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
