#!/bin/bash
# Log review completion for analytics and tracking
# Called when the cr-reviewer subagent completes via SubagentStop hook

# Configuration
LOG_FILE="${CODERABBIT_LOG_FILE:-$HOME/.claude/coderabbit-reviews.log}"
LOG_DIR="$(dirname "$LOG_FILE")"

# Read JSON input from stdin (SubagentStop event data)
# Capture cat output, fallback to empty JSON if empty or failed
INPUT=$(cat 2>/dev/null)
if [ -z "$INPUT" ]; then
    INPUT="{}"
fi

# Try to extract useful info from the event (single jq invocation for efficiency)
# SubagentStop events may have different field names depending on version
read -r AGENT_TYPE AGENT_NAME <<< "$(echo "$INPUT" | jq -r '[
    (.agent_type // .agentType // .type // ""),
    (.agent_name // .agentName // .name // "")
] | @tsv' 2>/dev/null)"

# Log if we matched the cr-reviewer agent (check multiple possible field values)
SHOULD_LOG=false
if [ "$AGENT_TYPE" = "cr-reviewer" ] || [ "$AGENT_TYPE" = "coderabbit:cr-reviewer" ]; then
    SHOULD_LOG=true
elif [ "$AGENT_NAME" = "cr-reviewer" ] || [ "$AGENT_NAME" = "coderabbit:cr-reviewer" ]; then
    SHOULD_LOG=true
fi

if [ "$SHOULD_LOG" = true ]; then
    # Ensure log directory exists
    if ! mkdir -p "$LOG_DIR" 2>/dev/null; then
        # Can't create directory, fail silently
        exit 0
    fi

    # Get current working directory for context
    CWD="${PWD:-unknown}"

    # Append completion record with more context
    echo "$(date -Iseconds) | dir=$CWD | CodeRabbit review completed" >> "$LOG_FILE" 2>/dev/null
fi

# Always exit 0 to not block the agent
exit 0
