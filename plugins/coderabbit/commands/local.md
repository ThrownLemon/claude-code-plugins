---
description: Review local code changes using CodeRabbit CLI before creating a PR
arguments:
  - name: type
    description: "Review type: uncommitted, committed, or all (default: all)"
    required: false
  - name: base
    description: Base branch to compare against (default: auto-detect)
    required: false
---

# CodeRabbit Local Code Review

Review your local code changes using the CodeRabbit CLI before creating a pull request.

## What This Does

This command delegates to the `cr-reviewer` subagent which will:

1. **Check Prerequisites**
   - Verify CodeRabbit CLI is installed (`coderabbit` or `cr`)
   - Check authentication status
   - Guide through setup if needed

2. **Run Code Review**
   - Execute `coderabbit --prompt-only` with specified options
   - Parse and categorize findings by severity

3. **Present Results**
   - Show summary of issues found
   - Group by severity (critical, major, minor, trivial)
   - Include file paths and line numbers

4. **Interactive Fix Loop**
   - Offer to apply suggested fixes
   - Re-run review after fixes to verify
   - Continue until all issues resolved or user stops

## Arguments

- **type**: Review scope
  - `uncommitted` - Only unstaged/staged changes
  - `committed` - Only committed changes not yet pushed
  - `all` - Both (default)

- **base**: Base branch for comparison
  - Auto-detects from `origin/HEAD` if not specified
  - Common values: `main`, `master`, `develop`

## Examples

```
/coderabbit:local
/coderabbit:local --type uncommitted
/coderabbit:local --base develop
/coderabbit:local --type committed --base main
```

## Rate Limiting

CodeRabbit free tier has usage limits. If rate limited, the subagent will:
- Inform you of the limit
- Suggest alternatives (smaller changeset, wait, manual review)
- Offer to retry after the limit resets

Use the `cr-reviewer` subagent to perform the review. Pass the arguments:
- type: $ARGUMENTS.type or "all"
- base: $ARGUMENTS.base or auto-detect from git
