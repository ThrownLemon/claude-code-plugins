---
description: Check the progress of a multi-AI review
arguments:
  - name: review
    description: "Review ID (default: latest)"
    required: false
---

# Multi-AI Review Status

Check the progress of a running or completed multi-AI code review.

## What This Shows

- Review ID and start time
- Per-CLI status (pending, running, complete, failed, timeout)
- Overall completion
- Any errors encountered

## Examples

```bash
# Check latest review
/multi-ai-review:status

# Check specific review
/multi-ai-review:status --review review-1736889600
```

## Steps

1. Look up the review metadata
2. Check status of each CLI
3. Report progress and any issues
4. If complete, note that report is ready

To run this command:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/review_runner.py status --review "$REVIEW_ID" --json
```

If no review ID provided, list recent reviews:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/review_runner.py list --json
```

Then show the most recent one's status.
