---
description: View CodeRabbit review history and statistics
arguments:
  - name: action
    description: "Action: show (default), clear, stats"
    required: false
  - name: limit
    description: "Number of entries to show (default: 10)"
    required: false
---

# CodeRabbit Review Log

View your CodeRabbit review session history.

## Configuration

The log file location respects the `CODERABBIT_LOG_FILE` environment variable:

```bash
LOG_FILE="${CODERABBIT_LOG_FILE:-$HOME/.claude/coderabbit-reviews.log}"
```

## Actions

### Show Recent Reviews (default)

Display recent review sessions:

```bash
LOG_FILE="${CODERABBIT_LOG_FILE:-$HOME/.claude/coderabbit-reviews.log}"
tail -n ${ARGUMENTS.limit || 10} "$LOG_FILE" 2>/dev/null || echo "No review history yet"
```

### Clear Log

Remove all review history:

```bash
LOG_FILE="${CODERABBIT_LOG_FILE:-$HOME/.claude/coderabbit-reviews.log}"
rm -f "$LOG_FILE" && echo "Review log cleared"
```

### Statistics

Show review statistics:

```bash
LOG_FILE="${CODERABBIT_LOG_FILE:-$HOME/.claude/coderabbit-reviews.log}"
if [ -f "$LOG_FILE" ]; then
  total=$(wc -l < "$LOG_FILE" | tr -d ' ')
  echo "Total reviews: $total"
  echo ""
  echo "Reviews by date:"
  cut -d'T' -f1 "$LOG_FILE" | sort | uniq -c | tail -7
else
  echo "No review history yet"
fi
```

## Steps

1. Check which action the user wants:
   - `show` or empty: Show recent reviews
   - `clear`: Clear the log file
   - `stats`: Show statistics

2. Execute the appropriate command

3. Present results in a formatted way

## Examples

```
/coderabbit:log
/coderabbit:log --action stats
/coderabbit:log --limit 20
/coderabbit:log --action clear
```
