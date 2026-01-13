#!/bin/bash
# Gently notify that a review might be helpful after file edits
# This is a non-blocking hook - it just prints a hint to stderr

# Configuration via environment variables:
# CODERABBIT_HINT_FREQUENCY: Show hint every N edits (default: 5, set to 0 to disable)
HINT_FREQUENCY="${CODERABBIT_HINT_FREQUENCY:-5}"

# Validate HINT_FREQUENCY is a positive integer, fallback to default if not
case "$HINT_FREQUENCY" in
    ''|*[!0-9]*)
        # Non-numeric or empty, use default
        HINT_FREQUENCY=5
        ;;
esac

# If frequency is 0, disable hints entirely
if [ "$HINT_FREQUENCY" -eq 0 ]; then
    exit 0
fi

# Show hint based on configured frequency (1 in N chance)
RANDOM_NUM=$((RANDOM % HINT_FREQUENCY))
if [ "$RANDOM_NUM" -eq 0 ]; then
    echo "" >&2
    echo "💡 Tip: Run /coderabbit:local to review your changes" >&2
fi

# Always exit 0 to not block the edit
exit 0
