---
description: Run a full project code review using multiple AI CLIs in parallel
arguments:
  - name: clis
    description: "Comma-separated CLIs to use (default: claude,gemini,codex)"
    required: false
  - name: focus
    description: "Review focus: all, security, quality, architecture, performance (default: all)"
    required: false
  - name: exclude
    description: "Glob patterns to exclude (e.g., 'node_modules/**,dist/**')"
    required: false
  - name: timeout
    description: "Timeout in minutes per CLI (default: 10)"
    required: false
---

# Multi-AI Code Review Scan

Run a comprehensive code review of the entire project using multiple AI CLIs in parallel, then compare their findings.

## What This Does

1. **Validates Prerequisites** - Checks which CLIs are installed
2. **Analyzes Project** - Identifies project structure and files
3. **Runs Parallel Reviews** - Executes Claude, Gemini, and Codex reviews simultaneously
4. **Aggregates Findings** - Matches similar issues across reviewers
5. **Generates Comparison** - Shows consensus, majority, and unique findings

## Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--clis` | `claude,gemini,codex` | Which CLIs to use (any combination) |
| `--focus` | `all` | Review focus area |
| `--exclude` | `.gitignore patterns` | Additional patterns to exclude |
| `--timeout` | `10` | Minutes per CLI (max: 30) |

### Focus Areas

- **all** - Comprehensive review (security, quality, architecture, performance, best practices)
- **security** - Security vulnerabilities, injection risks, auth issues
- **quality** - Code readability, maintainability, DRY violations
- **architecture** - Design patterns, coupling, cohesion
- **performance** - Efficiency, memory, database queries

## Examples

```bash
# Full review with all CLIs
/multi-ai-review:scan

# Security-focused review
/multi-ai-review:scan --focus security

# Use only Claude and Gemini
/multi-ai-review:scan --clis claude,gemini

# Exclude test files, longer timeout
/multi-ai-review:scan --exclude "test/**,__tests__/**" --timeout 15
```

## Output

The report shows findings grouped by agreement:

- **Consensus** - All CLIs agree (highest confidence)
- **Majority** - 2+ CLIs agree (likely valid)
- **Unique** - Only 1 CLI found (needs human review)

Use the `review-coordinator` subagent to perform the review.
