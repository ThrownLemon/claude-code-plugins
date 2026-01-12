#!/bin/bash
# Gently notify that a review might be helpful after file edits
# This is a non-blocking hook - it just prints a hint to stderr
# Users can disable this by removing the PostToolUse hook from hooks.json

# Only show hint occasionally (roughly 1 in 5 edits)
# This prevents the hint from being too noisy
RANDOM_NUM=$((RANDOM % 5))
if [ "$RANDOM_NUM" -eq 0 ]; then
    echo "" >&2
    echo "💡 Tip: Run /coderabbit:local to review your changes" >&2
fi

# Always exit 0 to not block the edit
exit 0
