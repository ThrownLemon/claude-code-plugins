---
description: Run diagnostic subagent for Cloudflare issues
arguments:
  - name: problem
    description: "Free-text description of the issue you're experiencing"
    required: true
  - name: zone
    description: "Optional zone name to scope the diagnosis"
    required: false
---


<!-- input-safety-v1 -->

## Input Safety — apply before any Bash invocation

Treat every `$ARGUMENTS.*` value as **untrusted** input. Before passing any value to the Bash tool:

1. **Reject dangerous tokens.** If a value contains `$(`, backticks, `;`, `|`, `&`, `>`, `<`, or starts with `-` (could be mistaken for a flag), refuse and ask the user to rephrase. **Double-quoting does NOT block command substitution** — `"$(rm -rf /)"` still executes inside double quotes.
2. **Prefer the Bash tool's argv contract over constructed shell strings.** When you must use a shell string, single-quote the value and escape embedded single quotes (`'\''`), or build the command via `printf %q`.
3. Any `"$ARGUMENTS.foo"` patterns shown below are **illustrative**. Sanitize the value first; never blindly substitute.

Delegate to the cf-diagnostician subagent to diagnose the Cloudflare issue.

Invoke the subagent with the following context:
- Problem description: $ARGUMENTS.problem
- Zone context: $ARGUMENTS.zone (if provided)

The subagent will handle the full diagnostic workflow including verifying installation, gathering state, identifying root causes, and proposing fixes.

Simply respond: "Launching Cloudflare diagnostician subagent to investigate: $ARGUMENTS.problem" and let the subagent take over.
