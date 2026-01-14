---
name: multi-review
description: Full project code review using multiple AI CLIs (Claude, Gemini, Codex). Use when user wants comprehensive multi-perspective code review.
triggers:
  - "multi ai review"
  - "multi-ai review"
  - "review with multiple ais"
  - "compare ai reviews"
  - "get opinions from multiple ais"
  - "run parallel review"
  - "claude gemini codex review"
  - "consensus review"
  - "multi-perspective review"
  - "cross-check my code"
  - "what do different ais think"
  - "full project review"
  - "comprehensive code review"
  - "review with all ais"
  - "ai consensus on code"
---

# Multi-AI Code Review Skill

When the user wants a comprehensive code review using multiple AI perspectives, delegate to the `review-coordinator` subagent.

## When to Use

Use this skill when the user:
- Asks for a "multi-AI" or "multi-perspective" review
- Wants to compare what different AI tools think about their code
- Asks for "consensus" or "cross-checking"
- Mentions Claude + Gemini + Codex reviewing together
- Wants a "comprehensive" or "full project" review
- Asks what different AIs think about their code

## Default Behavior

- **CLIs**: All three (claude, gemini, codex)
- **Focus**: Comprehensive (all categories)
- **Timeout**: 10 minutes per CLI

## What the Subagent Does

The `review-coordinator` subagent will:

1. **Validate Prerequisites**
   - Check which CLIs are installed
   - Report any missing CLIs with install instructions
   - Continue with available CLIs

2. **Execute Parallel Reviews**
   - Run all available CLIs simultaneously
   - Monitor for completion or timeout
   - Handle failures gracefully

3. **Aggregate Results**
   - Parse findings from each CLI
   - Match similar issues using fuzzy matching
   - Categorize by agreement level

4. **Present Comparison Report**
   - **Consensus** findings (all agree) - highest confidence
   - **Majority** findings (2+ agree) - likely valid
   - **Unique** findings (1 found) - needs human judgment

## Example User Requests

- "Run a multi-AI review of this codebase"
- "What do Claude, Gemini, and Codex think about my code?"
- "Get a consensus review of my project"
- "Compare AI opinions on this code"
- "Do a comprehensive code review"
- "Cross-check my code with multiple AIs"

Use the `review-coordinator` subagent to handle the review workflow.
