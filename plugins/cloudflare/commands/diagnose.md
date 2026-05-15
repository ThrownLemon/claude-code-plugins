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

Delegate to the cf-diagnostician subagent to diagnose the Cloudflare issue.

Invoke the subagent with the following context:
- Problem description: $ARGUMENTS.problem
- Zone context: $ARGUMENTS.zone (if provided)

The subagent will handle the full diagnostic workflow including verifying installation, gathering state, identifying root causes, and proposing fixes.

Simply respond: "Launching Cloudflare diagnostician subagent to investigate: $ARGUMENTS.problem" and let the subagent take over.
