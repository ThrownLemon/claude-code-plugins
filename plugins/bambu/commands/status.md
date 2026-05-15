---
description: "Show current Bambu Lab printer status — state, progress, temperatures, AMS, and ETA."
arguments: []
---

Fetch the current printer status and present it in a readable summary.

## Steps

1. Run the CLI command:

```bash
bambu status --json
```

2. If the command succeeds, parse the JSON output. Present a formatted block:

```
🖨️  Bambu Lab Printer Status
─────────────────────────────
State:     <stg_cur or state>
Progress:  <mc_percent>% — Layer <layer_num>/<total_layer_num>
Nozzle:    <nozzle_temp> °C  (target <nozzle_target_temp> °C)
Bed:       <bed_temp> °C     (target <bed_target_temp> °C)
AMS:       <ams info or "N/A">
ETA:       <remaining time, human-readable>
File:      <subtask_name or gcode_file>
```

3. Adapt the displayed fields to whatever keys the JSON actually contains — not every printer/feature reports every field. Omit sections that are missing or empty.

4. If the printer is **idle** (not printing), say so clearly:

```
🖨️  Bambu Lab Printer — Idle
────────────────────────────
State:   Idle
Nozzle:  <temp> °C
Bed:     <temp> °C
```

5. If the command fails (non-zero exit, timeout, or connection error):
   - Show the error message.
   - Suggest running `/bambu:doctor` to diagnose connectivity or configuration issues.
