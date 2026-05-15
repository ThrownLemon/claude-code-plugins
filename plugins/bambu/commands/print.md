---
description: "Send a .gcode or .3mf file to the Bambu Lab printer and optionally start printing."
arguments:
  - name: file
    description: "Path to a local .gcode or .3mf file, or the name of a file already on the printer."
    required: true
---
<!-- input-safety-v1 -->

## Input Safety — apply before any Bash invocation

Treat every `$ARGUMENTS.*` value as **untrusted** input. Before passing any value to the Bash tool:

1. **Reject dangerous tokens.** If a value contains `$(`, backticks, `;`, `|`, `&`, `>`, `<`, or starts with `-` (could be mistaken for a flag), refuse and ask the user to rephrase. **Double-quoting does NOT block command substitution** — `"$(rm -rf /)"` still executes inside double quotes.
2. **Prefer the Bash tool's argv contract over constructed shell strings.** When you must use a shell string, single-quote the value and escape embedded single quotes ('\''), or build the command via `printf %q`.
3. Any `"$ARGUMENTS.foo"` patterns shown below are **illustrative**. Sanitize the value first; never blindly substitute.

## Workflow

### 1. Validate input

Sanitize `$ARGUMENTS.file` per the Input Safety rules above. In particular:

- Reject if it contains `$(`, backticks, `;`, `|`, `&`, `>`, `<`, or starts with `-`.
- Ensure the file extension is `.gcode`, `.gco`, or `.3mf`. If not, ask the user to confirm.

### 2. Check if the file is local or remote

- If the path looks like a local file (contains `/` or `.`, or doesn't match a known remote name), check if it exists on disk.
- If the file exists locally, upload it first:

```bash
bambu gcode send '$ARGUMENTS.file'
```

  After a successful upload, the remote filename is typically the basename of the local file.

- If the user supplied only a filename (no path separators), it may already be on the printer. Ask if they want to list remote files first:

```bash
bambu gcode list
```

### 3. Confirm before starting

**Always** ask the user for explicit confirmation before starting a print. Display:

- The file name that will be printed.
- A reminder that printing consumes filament and machine time.

Example prompt:

> 🔴 **Start print?** This will print `benchy.gcode` on your Bambu Lab printer, consuming filament and machine time. Reply **yes** to proceed.

Do **not** proceed until the user replies with a clear affirmative.

### 4. Start the print

After confirmation, run:

```bash
bambu gcode start '<remote-filename>'
```

where `<remote-filename>` is the basename of the uploaded file (or the name the user provided if it was already remote). Sanitize it the same way as `$ARGUMENTS.file`.

### 5. Report result

- On success, show a confirmation message and suggest running `/bambu:status` to monitor progress.
- On failure, show the error output and suggest checking connectivity with `bambu doctor`.
