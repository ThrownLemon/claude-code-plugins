#!/bin/bash
# Google Veo video generation script
# Uses Gemini API to generate videos via long-running operations

set -e

# Default values
PROMPT=""
DURATION=6
ASPECT="16:9"
RESOLUTION="1080p"
MODEL="veo-3.1-generate-preview"
NEGATIVE_PROMPT=""
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
        --resolution)
            RESOLUTION="$2"
            shift 2
            ;;
        --model)
            MODEL="$2"
            shift 2
            ;;
        --negative)
            NEGATIVE_PROMPT="$2"
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
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "Error: GOOGLE_API_KEY environment variable not set" >&2
    echo "Get your API key from: https://aistudio.google.com/app/apikey" >&2
    exit 1
fi

# API endpoint
API_BASE="https://generativelanguage.googleapis.com/v1beta"

# Build the request payload
# Map resolution to Veo format
case "$RESOLUTION" in
    720p) VEO_RESOLUTION="720p" ;;
    1080p) VEO_RESOLUTION="1080p" ;;
    4k|4K) VEO_RESOLUTION="4k" ;;
    *) VEO_RESOLUTION="1080p" ;;
esac

# Build generation config
GEN_CONFIG=$(cat <<EOF
{
  "model": "models/${MODEL}",
  "generationConfig": {
    "videoDuration": "${DURATION}s",
    "aspectRatio": "${ASPECT}",
    "resolution": "${VEO_RESOLUTION}"
  },
  "prompt": {
    "text": $(echo "$PROMPT" | jq -Rs .)
  }
}
EOF
)

# Add negative prompt if specified
if [ -n "$NEGATIVE_PROMPT" ]; then
    GEN_CONFIG=$(echo "$GEN_CONFIG" | jq --arg neg "$NEGATIVE_PROMPT" '. + {negativePrompt: $neg}')
fi

# Add image reference if specified
if [ -n "$IMAGE_PATH" ] && [ -f "$IMAGE_PATH" ]; then
    # Read and base64 encode the image
    IMAGE_B64=$(base64 -i "$IMAGE_PATH" | tr -d '\n')
    MIME_TYPE=$(file --mime-type -b "$IMAGE_PATH")

    GEN_CONFIG=$(echo "$GEN_CONFIG" | jq --arg img "$IMAGE_B64" --arg mime "$MIME_TYPE" \
        '.image = {mimeType: $mime, data: $img}')
fi

# Submit generation request
echo "Submitting video generation request to Veo..." >&2
echo "Model: $MODEL" >&2
echo "Duration: ${DURATION}s" >&2
echo "Aspect: $ASPECT" >&2
echo "Resolution: $VEO_RESOLUTION" >&2

RESPONSE=$(curl -s -X POST \
    "${API_BASE}/models/${MODEL}:generateVideo" \
    -H "Content-Type: application/json" \
    -H "x-goog-api-key: ${GOOGLE_API_KEY}" \
    -d "$GEN_CONFIG")

# Check for errors
if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    ERROR_MSG=$(echo "$RESPONSE" | jq -r '.error.message // "Unknown error"')
    ERROR_CODE=$(echo "$RESPONSE" | jq -r '.error.code // "unknown"')
    echo "Error: API request failed" >&2
    echo "Code: $ERROR_CODE" >&2
    echo "Message: $ERROR_MSG" >&2
    exit 1
fi

# Extract operation name
OPERATION_NAME=$(echo "$RESPONSE" | jq -r '.name // empty')

if [ -z "$OPERATION_NAME" ]; then
    echo "Error: No operation ID returned" >&2
    echo "Response: $RESPONSE" >&2
    exit 1
fi

echo "Generation started successfully!" >&2
echo "Operation ID: $OPERATION_NAME" >&2

# Output the operation ID for polling
echo "$OPERATION_NAME"
