---
description: "Manage UniFi devices: list, show details, or restart an access point, switch, or gateway."
arguments:
  - name: action
    description: "The device operation to perform. One of: list (default), show, restart."
    required: false
  - name: mac
    description: "The MAC address of the target device. Required for show and restart actions."
    required: false
  - name: site
    description: "Optional site id to target instead of the current default site."
    required: false
---

<!-- input-safety-v1 -->

## Input Safety — apply before any Bash invocation

Treat every `$ARGUMENTS.*` value as **untrusted** input. Before passing any value to the Bash tool:

1. **Reject dangerous tokens.** If a value contains `$(`, backticks, `;`, `|`, `&`, `>`, `<`, or starts with `-` (could be mistaken for a flag), refuse and ask the user to rephrase. **Double-quoting does NOT block command substitution** — `"$(rm -rf /)"` still executes inside double quotes.
2. **Prefer the Bash tool's argv contract over constructed shell strings.** When you must use a shell string, single-quote the value and escape embedded single quotes ('\''), or build the command via `printf %q`.
3. Any `"$ARGUMENTS.foo"` patterns shown below are **illustrative**. Sanitize the value first; never blindly substitute.

## Instructions

1. **Sanitise** every argument value (`action`, `mac`, `site`) per the Input Safety rules above before use.
2. **Normalise `action`** — default to `list` if omitted or empty. Accept the exact values: `list`, `show`, `restart`. If the value is unrecognised, ask the user to correct it.
3. **Validate `mac`** — for `show` and `restart`, a MAC address is required. If missing, ask the user to provide it. Validate it looks like a MAC (e.g. `aa:bb:cc:dd:ee:ff` or `aabb.ccdd.eeff`). Reject values that fail the safety check.
4. **Build the command** using single-quoted values:

   ```bash
   # List
   unifi devices list --json

   # Show
   unifi devices show 'MAC_VALUE' --json

   # Restart
   unifi devices restart 'MAC_VALUE' --json
   ```

   If `$ARGUMENTS.site` is provided and passes sanitisation, append
   `--site 'SITE_VALUE'` to the command.

5. **Destructive action — confirm first.** `restart` is destructive (it
   reboots the device, causing temporary downtime). Before running, display
   a confirmation prompt:

   > You are about to **restart** device `$MAC_VALUE`. This will temporarily
   > take the device offline. Proceed? (yes/no)

   Only execute if the user explicitly says yes. Otherwise, abort.

6. **Execute** the command via the Bash tool.
7. **Parse** the JSON output and present it as a readable table or summary.
   For `list`, show columns: name, model, MAC, IP, status (online/offline),
   firmware version, and uptime. For `show`, display all available detail
   fields.
8. **Handle errors** — if the command returns a non-zero exit code or the JSON
   contains an error, surface the message and suggest next steps (verify MAC,
   check controller connectivity, confirm site id).
