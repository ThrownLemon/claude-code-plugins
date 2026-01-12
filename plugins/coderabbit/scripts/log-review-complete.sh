#!/bin/bash
# Log review completion for analytics and tracking
# Called when the cr-reviewer subagent completes

# Read JSON input from stdin
INPUT=$(cat)

# Extract agent type from the input
AGENT_TYPE=$(echo "$INPUT" | jq -r '.agent_type // empty' 2>/dev/null)

# Only log for cr-reviewer agent
if [ "$AGENT_TYPE" = "cr-reviewer" ]; then
    # Ensure log directory exists
    mkdir -p ~/.claude

    # Append completion record
    echo "$(date -Iseconds): CodeRabbit review session completed" >> ~/.claude/coderabbit-reviews.log
fi

# Always exit 0 to not block
exit 0
