---
description: Review tournament solutions and create combined branch
arguments:
  - name: tournament
    description: Tournament ID (default: most recent)
    required: false
  - name: format
    description: "Report format: markdown or json (default: markdown)"
    required: false
---

# Tournament Review

Review completed tournament solutions and create a combined branch with the best parts.

## What This Does

1. **Gather solutions** from all tournament workers
2. **Read DONE.md** summaries from each worker
3. **Compare git diffs** between solutions
4. **Generate review report** for AI analysis
5. **Help create combined branch** with selected changes

## Prerequisites

All workers must have completed their work and created `DONE.md` files.

Check status first:
```bash
/fork-terminal:status --tournament <tournament-id>
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--tournament` | Tournament ID | most recent |
| `--format` | `markdown` or `json` | `markdown` |

## Examples

```bash
# Review most recent tournament
/fork-terminal:review

# Review specific tournament
/fork-terminal:review --tournament tournament-1736889600

# Get JSON output for programmatic analysis
/fork-terminal:review --format json
```

## Execution

### Step 1: Generate Review Report

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/tournament_review.py report \
  --tournament "<tournament-id>" \
  [--format markdown|json]
```

### Step 2: Analyze Solutions

Read the review report and analyze:
- Each worker's approach (from DONE.md)
- Files modified by each solution
- Commit counts and code changes

### Step 3: Create Combined Branch (Optional)

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/tournament_review.py combine \
  --tournament "<tournament-id>" \
  [--branch "<branch-name>"]
```

## Review Report Format

The markdown report includes:

```markdown
# Tournament Review

## Task: implement user authentication

Base branch: main
Competing CLIs: claude, gemini, codex

---

## Solution from CLAUDE (Worker 1)

**Branch**: `tournament/auth-claude-1`
**Commits**: 5
**Files changed**: 8

### DONE.md Summary:
[Worker's summary of their approach]

### Git Diff Stats:
[Summary of changes]

### Files Modified:
- `src/auth/login.ts`
- `src/auth/middleware.ts`
...

---

## Solution from GEMINI (Worker 2)
...

---

## Review Questions

1. Which solution has the best overall approach?
2. What are the strengths of each solution?
3. What parts from each solution should be combined?
4. Are there any issues or concerns with any solution?
```

## Workflow After Review

1. **Read the review report** to understand each solution
2. **Compare approaches** and identify the best parts
3. **Create combined branch** using:
   - Cherry-pick specific commits
   - Checkout files from specific workers
   - Manual merge of code
4. **Clean up** tournament worktrees with `/fork-terminal:remove`

## Get Specific File Diffs

To see the full diff for a specific file:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/tournament_review.py diff \
  --tournament "<tournament-id>" \
  --worker <worker-id> \
  --file "<file-path>"
```

## Related Commands

- `/fork-terminal:status` - Check tournament progress
- `/fork-terminal:list` - List all worktrees
- `/fork-terminal:remove` - Clean up worktrees
