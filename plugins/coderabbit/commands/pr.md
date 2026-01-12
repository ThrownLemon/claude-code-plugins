---
description: View and manage all PR review comments - CodeRabbit, other bots, and human reviewers
arguments:
  - name: pr
    description: PR number (optional, auto-detects current branch PR)
    required: false
  - name: filter
    description: "Filter by reviewer or severity (e.g., coderabbit, critical)"
    required: false
---

# CodeRabbit PR Comment Manager

View and manage all review comments on your pull request from all sources.

## What This Does

This command delegates to the `cr-pr-manager` subagent which will:

1. **Identify PR**
   - Auto-detect from current branch if PR number not specified
   - Extract repo info from git remote

2. **Fetch ALL Comments**
   - CodeRabbit comments via MCP tools
   - GitHub review comments (captures other bots)
   - GitHub reviews (human reviewers)

3. **Categorize by Reviewer**
   - **CodeRabbit** - AI-powered review bot
   - **Other Bots** - SonarCloud, Codacy, Snyk, etc.
   - **Human Reviewers** - Team members

4. **Present Comments**
   - Group by reviewer, then by severity/file
   - Show file path, line numbers, comment text
   - Include resolution status

5. **Interactive Actions**
   - View full comment details
   - Apply suggested fixes (CodeRabbit)
   - Mark as resolved
   - Reply to comments
   - Filter by reviewer/file/severity

## Arguments

- **pr**: PR number to manage
  - Auto-detects if on a branch with an open PR
  - Specify to target a different PR

- **filter**: Filter comments
  - By reviewer: `coderabbit`, `human`, `bot`
  - By severity: `critical`, `major`, `minor`
  - By file: partial path match

## Examples

```
/coderabbit:pr
/coderabbit:pr --pr 123
/coderabbit:pr --filter coderabbit
/coderabbit:pr --pr 456 --filter critical
```

## Comment Sources

This command fetches from multiple sources to give you a complete picture:

| Source | API | Content |
|--------|-----|---------|
| CodeRabbit | MCP | AI review comments with fix suggestions |
| GitHub Reviews | MCP | Human reviewer comments and approvals |
| GitHub Comments | MCP | Other bot comments (Snyk, SonarCloud, etc.) |

Use the `cr-pr-manager` subagent to manage PR comments. Pass the arguments:
- pr: $ARGUMENTS.pr or auto-detect
- filter: $ARGUMENTS.filter or none
