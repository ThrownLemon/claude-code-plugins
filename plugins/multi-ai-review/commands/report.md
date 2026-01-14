---
description: View or regenerate a multi-AI review report
arguments:
  - name: review
    description: "Review ID (default: latest)"
    required: false
  - name: format
    description: "Output format: markdown, json (default: markdown)"
    required: false
  - name: section
    description: "Show only: all, consensus, majority, unique (default: all)"
    required: false
---

# Multi-AI Review Report

View or regenerate a comparison report from a completed review.

## Report Sections

### Consensus (All CLIs Agree)
Issues identified by ALL reviewers - **highest confidence** findings that should definitely be addressed.

### Majority (2+ CLIs Agree)
Issues identified by at least two reviewers - **likely valid** findings worth investigating.

### Unique Findings
Issues only one CLI found. May indicate:
- Specialized insight that others missed
- False positive
- Style preference specific to one AI
- **Needs human judgment**

## Examples

```bash
# View latest report
/multi-ai-review:report

# View specific review
/multi-ai-review:report --review review-1736889600

# Get JSON output
/multi-ai-review:report --format json

# Show only consensus findings
/multi-ai-review:report --section consensus

# Show only unique findings
/multi-ai-review:report --section unique
```

## Output Format

The report shows:

1. **Summary table** - Counts by agreement level and severity
2. **Consensus findings** - Full details with all CLI perspectives
3. **Majority findings** - Details with agreeing CLIs' notes
4. **Unique findings** - Brief list grouped by CLI

Each finding includes:
- Severity emoji (🔴 critical, 🟠 major, 🟡 minor, 🔵 trivial)
- File and line number
- Description from each CLI that found it
- Suggested fixes if available

Use the `report-generator` subagent to generate and display the report.
