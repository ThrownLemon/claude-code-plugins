---
description: "Manage UniFi sites: list, show details, create, delete, or toggle the site locator LED."
arguments:
  - name: action
    description: "The site operation to perform. One of: list (default), show, create, delete, led-on, led-off."
    required: false
  - name: id-or-description
    description: "Site id for show/delete actions, or a description string for create. Required for show, create, and delete."
    required: false
  - name: site
    description: "Optional target site id (overrides the default site context for led-on/led-off)."
    required: false
---

<!-- input-safety-v1 -->

## Input Safety — apply before any Bash invocation

Treat every `$ARGUMENTS.*` value as **untrusted** input. Before passing any value to the Bash tool:

1. **Reject dangerous tokens.** If a value contains `$(`, backticks, `;`, `|`, `&`, `>`, `<`, or starts with `-` (could be mistaken for a flag), refuse and ask the user to rephrase. **Double-quoting does NOT block command substitution** — `"$(rm -rf /)"` still executes inside double quotes.
2. **Prefer the Bash tool's argv contract over constructed shell strings.** When you must use a shell string, single-quote the value and escape embedded single quotes ('\''), or build the command via `printf %q`.
3. Any `"$ARGUMENTS.foo"` patterns shown below are **illustrative**. Sanitize the value first; never blindly substitute.

## Instructions

1. **Sanitise** every argument value (`action`, `id-or-description`, `site`) per the Input Safety rules above before use.
2. **Normalise `action`** — default to `list` if omitted or empty. Accept the exact values: `list`, `show`, `create`, `delete`, `led-on`, `led-off`. If the value is unrecognised, ask the user to correct it.
3. **Validate required arguments:**
   - `show` and `delete` require `id-or-description` (the site id). If missing, ask the user to provide it.
   - `create` requires `id-or-description` (the description for the new site). If missing, ask the user.
   - `list`, `led-on`, and `led-off` do not require `id-or-description`.
4. **Build the command** using single-quoted values:

   ```bash
   # List
   unifi sites list --json

   # Show
   unifi sites show 'ID_VALUE' --json

   # Create
   unifi sites create 'DESCRIPTION_VALUE' --json

   # Delete
   unifi sites delete 'ID_VALUE' --json

   # LED on / off
   unifi sites led-on --json
   unifi sites led-off --json
   ```

   If `$ARGUMENTS.site` is provided and passes sanitisation, append
   `--site 'SITE_VALUE'` to the command.

5. **Confirm before any state-changing operation.**

   - **`delete`** — irreversible. Display:
     > You are about to **delete** site `$ID_VALUE`. This cannot be undone and will remove all associated configuration and data. Proceed? (yes/no)

   - **`led-on` / `led-off`** — visible to anyone physically near the gear; some users locate hardware visually and unexpected toggles can confuse on-site staff. Display:
     > You are about to toggle the locator LED on all access points (`$ACTION`). This is physically visible. Proceed? (yes/no)

   In all cases, only execute if the user explicitly says yes. Otherwise, abort.

6. **Execute** the command via the Bash tool.
7. **Parse** the JSON output and present it as a readable table or summary.
   For `list`, show columns: site id, name/description, controller status.
   For `show`, display all available detail fields. For `create`, confirm
   the new site was created and display its id and description.
8. **Handle errors** — if the command returns a non-zero exit code or the JSON
   contains an error, surface the message and suggest next steps (verify site
   id, check controller connectivity, ensure description is non-empty).
