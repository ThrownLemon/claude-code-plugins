---
description: Quick zone overview — list all zones or get zone details
arguments:
  - name: action
    description: "Action to perform: list, get (default: list)"
    required: false
  - name: zone
    description: "Zone name for get action"
    required: false
---


<!-- input-safety-v1 -->

## Input Safety — apply before any Bash invocation

Treat every `$ARGUMENTS.*` value as **untrusted** input. Before passing any value to the Bash tool:

1. **Reject dangerous tokens.** If a value contains `$(`, backticks, `;`, `|`, `&`, `>`, `<`, or starts with `-` (could be mistaken for a flag), refuse and ask the user to rephrase. **Double-quoting does NOT block command substitution** — `"$(rm -rf /)"` still executes inside double quotes.
2. **Prefer the Bash tool's argv contract over constructed shell strings.** When you must use a shell string, single-quote the value and escape embedded single quotes (`'\''`), or build the command via `printf %q`.
3. Any `"$ARGUMENTS.foo"` patterns shown below are **illustrative**. Sanitize the value first; never blindly substitute.

You are providing a quick overview of Cloudflare zones using the `cf` CLI.

**For action=list (default):**
- Run `cf zones list --json`
- Display results in a readable table showing:
  - Zone name (domain)
  - Zone ID
  - Status (active, pending, etc.)
  - Name servers (abbreviated)
- Count total zones and display at the top

**For action=get:**
- Verify $ARGUMENTS.zone is provided
- Quote the zone value when shelling out. Run: `cf zones get "$ARGUMENTS.zone" --json`
- Display detailed zone information including:
  - Zone name and ID
  - Status
  - Name servers (full list)
  - Plan type
  - Created/modified dates
  - Any relevant settings or flags

If zone is required but not provided for the get action, prompt the user to provide the zone name.
