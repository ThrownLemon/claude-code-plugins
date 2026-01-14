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

# Usage function
usage() {
    cat >&2 <<EOF
Usage: $(basename "$0") --prompt "description" [options]

Required:
  --prompt TEXT      Video description prompt

Options:
  --duration NUM     Duration in seconds: 4, 6, or 8 (default: 6)
  --aspect RATIO     Aspect ratio: 16:9 or 9:16 (default: 16:9)
  --resolution RES   Resolution: 720p, 1080p, or 4k (default: 1080p)
  --model MODEL      Model name (default: veo-3.1-generate-preview)
  --negative TEXT    Negative prompt (elements to exclude)
  --image PATH       Reference image file path
  --help             Show this help message

Models:
  veo-3.1-generate-preview      Latest with audio (preview)
  veo-3.1-fast-generate-preview Fast variant with audio (preview)
  veo-2.0-generate-001          Stable, silent video

Environment:
  GOOGLE_API_KEY     Required. Get from https://aistudio.google.com/app/apikey

Dependencies:
  curl, jq, base64, file (for image handling)
EOF
    exit "${1:-1}"
}

# Check required dependencies
check_dependencies() {
    local missing=()
    for cmd in curl jq; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing+=("$cmd")
        fi
    done
    if [ ${#missing[@]} -gt 0 ]; then
        echo "Error: Missing required dependencies: ${missing[*]}" >&2
        echo "Please install them and try again." >&2
        exit 1
    fi
}

check_dependencies

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
        --resolution)
            if [[ -z "$2" || "$2" == -* ]]; then
                echo "Error: --resolution requires a value" >&2
                usage 1
            fi
            RESOLUTION="$2"
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
        --negative)
            if [[ -z "$2" || "$2" == -* ]]; then
                echo "Error: --negative requires a value" >&2
                usage 1
            fi
            NEGATIVE_PROMPT="$2"
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

# Validate duration (must be 4, 6, or 8)
case "$DURATION" in
    4|6|8) ;;
    *)
        echo "Error: --duration must be 4, 6, or 8 (got: $DURATION)" >&2
        exit 1
        ;;
esac

# Validate aspect ratio
case "$ASPECT" in
    16:9|9:16) ;;
    *)
        echo "Error: --aspect must be 16:9 or 9:16 (got: $ASPECT)" >&2
        exit 1
        ;;
esac

# Check API key (support both GOOGLE_API_KEY and GEMINI_API_KEY)
if [ -z "$GOOGLE_API_KEY" ]; then
    if [ -n "$GEMINI_API_KEY" ]; then
        GOOGLE_API_KEY="$GEMINI_API_KEY"
    else
        echo "Error: GOOGLE_API_KEY or GEMINI_API_KEY environment variable not set" >&2
        echo "Get your API key from: https://aistudio.google.com/app/apikey" >&2
        exit 1
    fi
fi

# API endpoint
API_BASE="https://generativelanguage.googleapis.com/v1beta"

# Map resolution to Veo format
case "$RESOLUTION" in
    720p) VEO_RESOLUTION="720p" ;;
    1080p) VEO_RESOLUTION="1080p" ;;
    4k|4K) VEO_RESOLUTION="4k" ;;
    *)
        echo "Warning: Unknown resolution '$RESOLUTION', using 1080p" >&2
        VEO_RESOLUTION="1080p"
        ;;
esac

# Build generation config using correct Veo REST API schema
# Structure: { instances: [{ prompt, negativePrompt? }], parameters: { aspectRatio, resolution, durationSeconds } }
INSTANCE=$(jq -n --arg prompt "$PROMPT" '{ "prompt": $prompt }')

# Add negative prompt to instance if specified
if [ -n "$NEGATIVE_PROMPT" ]; then
    INSTANCE=$(echo "$INSTANCE" | jq --arg neg "$NEGATIVE_PROMPT" '. + { negativePrompt: $neg }')
fi

# Add image reference to instance if specified
if [ -n "$IMAGE_PATH" ]; then
    # Check for additional dependencies needed for image handling
    for cmd in base64 file; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            echo "Error: '$cmd' command required for image handling" >&2
            exit 1
        fi
    done

    if [ -f "$IMAGE_PATH" ]; then
        # Read and base64 encode the image (portable: use stdin redirection)
        IMAGE_B64=$(base64 < "$IMAGE_PATH" | tr -d '\n')
        MIME_TYPE=$(file --mime-type -b "$IMAGE_PATH")

        INSTANCE=$(echo "$INSTANCE" | jq --arg img "$IMAGE_B64" --arg mime "$MIME_TYPE" \
            '. + { image: { mimeType: $mime, bytesBase64Encoded: $img } }')
    else
        echo "Error: Image file not found: $IMAGE_PATH" >&2
        exit 1
    fi
fi

# Build final request body (durationSeconds must be a number)
GEN_CONFIG=$(jq -n \
    --argjson instance "$INSTANCE" \
    --arg aspect "$ASPECT" \
    --arg resolution "$VEO_RESOLUTION" \
    --argjson duration "$DURATION" \
    '{
        "instances": [$instance],
        "parameters": {
            "aspectRatio": $aspect,
            "resolution": $resolution,
            "durationSeconds": $duration
        }
    }')

# Submit generation request
echo "Submitting video generation request to Veo..." >&2
echo "Model: $MODEL" >&2
echo "Duration: ${DURATION}s" >&2
echo "Aspect: $ASPECT" >&2
echo "Resolution: $VEO_RESOLUTION" >&2

RESPONSE=$(curl -sS --connect-timeout 30 --max-time 120 -X POST \
    "${API_BASE}/models/${MODEL}:predictLongRunning" \
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
