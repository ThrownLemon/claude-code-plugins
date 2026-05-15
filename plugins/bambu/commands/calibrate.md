---
description: "Run a calibration routine on the Bambu Lab printer — bed leveling, vibration compensation, or both."
arguments:
  - name: which
    description: "Which calibration to run: bed, vibration, or all (default: all)."
    required: false
---
<!-- input-safety-v1 -->

## Input Safety — apply before any Bash invocation

Treat every `$ARGUMENTS.*` value as **untrusted** input. Before passing any value to the Bash tool:

1. **Reject dangerous tokens.** If a value contains `$(`, backticks, `;`, `|`, `&`, `>`, `<`, or starts with `-` (could be mistaken for a flag), refuse and ask the user to rephrase. **Double-quoting does NOT block command substitution** — `"$(rm -rf /)"` still executes inside double quotes.
2. **Prefer the Bash tool's argv contract over constructed shell strings.** When you must use a shell string, single-quote the value and escape embedded single quotes ('\''), or build the command via `printf %q`.
3. Any `"$ARGUMENTS.foo"` patterns shown below are **illustrative**. Sanitize the value first; never blindly substitute.

## Workflow

### 1. Sanitize and resolve target

Validate `$ARGUMENTS.which` (or default to `all`):

- Lowercase the value.
- It must be one of: `bed`, `vibration`, `all`.
- Reject any value containing `$(`, backticks, `;`, `|`, `&`, `>`, `<`, or starting with `-`.
- If it is none of the accepted values, tell the user the valid options and stop.

### 2. Confirm before starting

Calibration **takes the printer offline for several minutes**. Always ask for confirmation first.

Map the target to a human description:

| Target | Description |
|---|---|
| `bed` | Bed auto-leveling (~2–4 min) |
| `vibration` | Vibration compensation / resonance testing (~3–5 min) |
| `all` | Full calibration sequence (bed + vibration, ~5–10 min) |

Show a confirmation prompt:

> ⚙️ **Run calibration?** This will run **<description>**. The printer will be unavailable during this time. Reply **yes** to proceed.

Wait for a clear affirmative. If the user declines, stop.

### 3. Execute

After confirmation, run:

```bash
bambu calibrate <target>
```

where `<target>` is the sanitized value of `$ARGUMENTS.which` (or `all`).

### 4. Report result

- On success, report that calibration completed.
- On failure, show the error output and suggest running `bambu doctor` to diagnose issues.
- Suggest `/bambu:status` to verify the printer is back to idle and ready.
