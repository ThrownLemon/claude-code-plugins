# bambu — Claude Code Plugin

Control your **Bambu Lab X1Plus 3D printer** from Claude Code using the [`bambu`](https://github.com/ThrownLemon/bambulabs-cli) CLI.

## Prerequisites

| Requirement | Install |
|---|---|
| **bambu CLI** on PATH | `bun install -g bambulabs-cli` (see [repo](https://github.com/ThrownLemon/bambulabs-cli)) |
| **sshpass** | `brew install hudochenkov/sshpass/sshpass` · `apt install sshpass` |
| OrcaSlicer *(optional)* | for slicing .3mf → .gcode before sending |
| ffmpeg *(optional)* | for camera / timelapse features |

## Installation

```bash
# From the marketplace repo
claude plugin add travis-plugins/bambu

# Or clone manually
git clone https://github.com/ThrownLemon/claude-code-plugins ~/.claude/plugins/bambu
```

## Configuration

The plugin reads the same config as the CLI:

```bash
# Non-secret keys — fine to put on the command line
bambu config set printer.ip      192.168.1.100
bambu config set printer.serial  "01P00AXXXXXXXXX"

# Secret keys — read interactively so the value never lands in shell history
read -s -p "Access code: " access_code && bambu config set printer.accessCode "$access_code" && unset access_code
read -s -p "SSH password: " ssh_password && bambu config set printer.ssh.password "$ssh_password" && unset ssh_password
```

> **Never use `bambu config list` to verify** — it will print `accessCode` and `ssh.password` to the terminal. To check that secret keys are set without revealing their values:
>
> ```bash
> for k in printer.accessCode printer.ssh.password; do
>   bambu config get "$k" >/dev/null 2>&1 && echo "$k: set" || echo "$k: NOT set"
> done
> ```

Config file location: `~/.config/bambu-cli/config.toml` (chmod 600 if you create it manually).

## Commands

| Slash Command | Description |
|---|---|
| `/bambu:status` | Current printer state, temps, progress, ETA |
| `/bambu:print` | Send a .gcode/.3mf file and optionally start printing |
| `/bambu:control` | Pause / resume / cancel the active print |
| `/bambu:calibrate` | Run bed leveling, vibration calibration, or both |

## Skill — auto-triggered

The **bambu-printer** skill activates on natural-language phrases like
*"print status"*, *"send to printer"*, *"is my print done"*, *"calibrate bed"*, and more — no slash command required.

## Agent

| Agent | Purpose |
|---|---|
| `bambu-doctor` | Run full diagnostics: CLI check → config check → `bambu doctor` → `bambu status` → summary + fixes |

## Destructive operations

The plugin will **always ask for confirmation** before:

- Starting a new print (consumes filament + machine time)
- Cancelling a running print
- Running calibration (printer will be busy for several minutes)
- Executing SSH commands on the printer

## Tips

- All commands that support `--json` use it automatically for reliable parsing.
- Use `bambu history` directly in Bash for past print logs.
- Filament management: `bambu filament list` / `bambu filament add` / `bambu filament remove`.
- Camera analysis: `bambu xcam first-layer` / `bambu xcam spaghetti`.

## License

MIT — see [ThrownLemon/claude-code-plugins](https://github.com/ThrownLemon/claude-code-plugins).
