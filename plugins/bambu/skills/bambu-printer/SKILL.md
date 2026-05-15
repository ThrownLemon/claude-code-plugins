---
name: bambu-printer
description: >
  Automatically assist with Bambu Lab X1Plus 3D printer operations via the bambu CLI.
  Covers status checks, file transfer, print control, calibration, filament management,
  camera analysis, diagnostics, and SSH commands.
triggers:
  - "print status"
  - "printer status"
  - "send to printer"
  - "what's printing"
  - "bambu status"
  - "is my print done"
  - "send gcode"
  - "send .gcode"
  - "calibrate printer"
  - "calibrate bed"
  - "filament loaded"
  - "AMS slot"
  - "spaghetti detection"
  - "first layer check"
  - "bambu doctor"
  - "printer info"
  - "bambu info"
  - "print history"
  - "run bambu"
  - "3d printer"
  - "bambu lab"
  - "gcode file"
  - "printer temperature"
  - "check on my print"
  - "cancel print"
  - "pause print"
  - "resume print"
  - "start print"
---

## Bambu printer skill — usage guide

You have access to the **bambu** CLI for controlling a Bambu Lab X1Plus 3D printer. Follow these rules every time the user mentions their printer.

### Core principles

1. **Use the CLI, don't guess.** Always run `bambu` commands via the Bash tool to get real data. Never fabricate printer state, temperatures, or progress numbers.
2. **Prefer `--json` output.** When a subcommand supports `--json`, use it — then parse and present the result in a human-readable format.
3. **Recommend slash commands.** If the user's request maps cleanly to a plugin command, suggest the slash form:
   - `/bambu:status` — quick status check
   - `/bambu:print` — send & start a print
   - `/bambu:control` — pause / resume / cancel
   - `/bambu:calibrate` — bed or vibration calibration
4. **Quote all file paths and arguments.** Filenames with spaces or special characters must be properly quoted.

### Command quick reference

| Intent | Command |
|---|---|
| Current state | `bambu status --json` |
| Printer info | `bambu info --json` |
| Send file | `bambu gcode send "<file>"` |
| List files on printer | `bambu gcode list` |
| Start remote print | `bambu gcode start "<file>"` |
| Pause / Resume / Cancel | `bambu gcode pause` / `resume` / `cancel` |
| Print history | `bambu history --json` |
| Calibrate | `bambu calibrate bed` / `vibration` / `all` |
| Filament | `bambu filament list` / `add <name>` / `remove <name>` |
| Camera analysis | `bambu xcam first-layer` / `spaghetti` |
| Diagnostics | `bambu doctor --json` |
| Automation scripts | `bambu script <name>` |
| SSH (X1Plus) | `bambu ssh "<command>"` |
| Config | `bambu config set <k> <v>` / `get <k>` (never `list` — prints secrets) |

### Destructive-operation policy

Before executing any of the following, **stop and ask the user for explicit confirmation**:

- `bambu gcode start` — starts a physical print (consumes filament & machine time)
- `bambu gcode cancel` — aborts the current print
- `bambu calibrate *` — takes the printer offline for several minutes
- `bambu ssh *` — runs arbitrary commands on the printer OS
- `bambu filament remove` — removes a filament profile

Display what will happen and wait for a clear "yes" / "go ahead" before proceeding.

### Presenting status

When showing printer status, format it as a clean block:

```
🖨️  Bambu Lab Printer Status
─────────────────────────────
State:     Printing
Progress:  42% — Layer 127/300
Nozzle:    220 °C
Bed:       60 °C
AMS:       Slot 1 — PLA Basic (Gray)
ETA:       1h 23m remaining
File:      benchy.gcode
```

If `--json` output is available, parse it and render a block like the one above.

### Troubleshooting

If a command fails:

1. Suggest running `/bambu:doctor` (delegates to the `bambu-doctor` subagent) or `bambu doctor --json` for diagnostics.
2. Check that `bambu` is on PATH with `which bambu`.
3. Verify required config keys are set **without echoing their values** (never run `bambu config list` — it prints `accessCode` and `ssh.password`). Use:
   ```bash
   for k in printer.ip printer.serial printer.accessCode printer.ssh.password; do
     bambu config get "$k" >/dev/null 2>&1 && echo "$k: set" || echo "$k: NOT set"
   done
   ```
4. Mention network issues (printer IP reachable on LAN).
