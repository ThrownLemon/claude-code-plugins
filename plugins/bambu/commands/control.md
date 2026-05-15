---
description: "Control the active Bambu Lab print — pause, resume, or cancel."
arguments:
  - name: action
    description: "The control action to perform: pause, resume, cancel, or status (default: status)."
    required: false
---
<!-- input-safety-v1 -->

## Input Safety — apply before any Bash invocation

Treat every `$ARGUMENTS.*` value as **untrusted** input. Before passing any value to the Bash tool:

1. **Reject dangerous tokens.** If a value contains `$(`, backticks, `;`, `|`, `&`, `>`, `<`, or starts with `-` (could be mistaken for a flag), refuse and ask the user to rephrase. **Double-quoting does NOT block command substitution** — `"$(rm -rf /)"` still executes inside double quotes.
2. **Prefer the Bash tool's argv contract over constructed shell strings.** When you must use a shell string, single-quote the value and escape embedded single quotes ('\''), or build the command via `printf %q`.
3. Any `"$ARGUMENTS.foo"` patterns shown below are **illustrative**. Sanitize the value first; never blindly substitute.

## Workflow

### 1. Sanitize and resolve action

Validate `$ARGUMENTS.action` (or default to `status`):

- Lowercase the value.
- It must be one of: `pause`, `resume`, `cancel`, `status`.
- Reject any value containing `$(`, backticks, `;`, `|`, `&`, `>`, `<`, or starting with `-`.
- If it is none of the accepted values, tell the user the valid options and stop.

### 2. Dispatch

#### `status`

```bash
bambu status --json
```

Parse the JSON and present a formatted status block (same format as `/bambu:status`).

#### `pause`

```bash
bambu gcode pause
```

Report success or failure.

#### `resume`

```bash
bambu gcode resume
```

Report success or failure.

#### `cancel` — ⚠️ DESTRUCTIVE

Cancelling **aborts the current print**. The partial print and filament are usually unrecoverable.

Before executing, show a confirmation prompt:

> 🔴 **Cancel the current print?** This will abort the running print. Filament and progress will be lost. Reply **yes** to proceed.

Wait for a clear affirmative response. If the user does not confirm, stop without running the command.

After confirmation:

```bash
bambu gcode cancel
```

Report the result.

### 3. Report result

For every action, show the CLI output or a clear success/failure message. Suggest `/bambu:status` to verify the new state.
