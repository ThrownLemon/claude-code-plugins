# unifi — Claude Code Plugin

Manage UniFi network devices directly from Claude Code.

Wraps the local `unifi` CLI from
[github.com/ThrownLemon/unifi-cli](https://github.com/ThrownLemon/unifi-cli)
— a Bun/TypeScript CLI for Ubiquiti UniFi controllers.

---

## Prerequisites

1. **Node ≥ 18** and **Bun** installed.
2. Install the CLI:

```bash
bun install -g @thrownlemon/unifi-cli
```

3. Verify it works:

```bash
unifi --version
unifi sites list
```

4. Your UniFi controller must be reachable from this machine (VPN or local
   network).

## Configuration

The CLI reads from `~/.config/unifi-cli/config.json` or these environment
variables:

| Variable | Purpose |
|---|---|
| `UNIFI_CONTROLLER_URL` | Base URL, e.g. `https://unifi.local:8443` |
| `UNIFI_USERNAME` | Controller username (if not using token auth) |
| `UNIFI_PASSWORD` | Controller password |
| `UNIFI_API_TOKEN` | API token (preferred over username/password) |

Example `config.json`:

```json
{
  "controllerUrl": "https://192.168.1.1:8443",
  "username": "admin",
  "password": "s3cret"
}
```

> **Restrict permissions on this file** — it holds plaintext credentials:
> ```bash
> chmod 600 ~/.config/unifi-cli/config.json
> ```
> Prefer using `UNIFI_API_TOKEN` (a controller-issued API token) over username/password where supported by your controller version. Tokens can be revoked individually without rotating a password used elsewhere.

## Installation

Add the plugin from the marketplace:

```bash
claude plugin add unifi --marketplace travis-plugins
```

Or manually — clone this repo and symlink:

```bash
git clone https://github.com/ThrownLemon/claude-code-plugins.git
claude plugin add ./claude-code-plugins/plugins/unifi
```

Restart Claude Code after installation.

## Slash Commands

| Command | Description |
|---|---|
| `/unifi:clients` | List, show, block, unblock, reconnect, or forget clients |
| `/unifi:devices` | List, show, or restart UniFi devices |
| `/unifi:sites` | List, show, create, delete sites; toggle site LED |

All commands default to the current site. Pass `--site <id>` to target a
different site.

## Skill — `unifi-network`

Auto-triggered when you ask Claude about your UniFi network in natural
language. Examples:

- "Show me all connected WiFi clients"
- "Block the device with MAC aa:bb:cc:dd:ee:ff"
- "What's using the most bandwidth?"
- "Restart the access point in the living room"
- "Turn off the site LED"

The skill prefers `--json` output for reliable parsing and will **always
confirm** before running state-changing operations (block, forget, delete,
restart device, LED on/off — the LED is physically visible and worth
flagging).

## Agent — `unifi-troubleshooter`

A diagnostic agent that:

1. Verifies the CLI is installed and the controller is reachable.
2. Gathers state (devices, clients, sessions, DPI stats).
3. Identifies probable causes for reported issues.
4. Proposes fix commands — never executes destructive ops without confirmation.

Trigger it by asking Claude to troubleshoot a UniFi issue, e.g.:

> "A client at aa:bb:cc:dd:ee:ff can't connect to the network. Help me figure
> out why."

## Safety

Each command file under `commands/` and the troubleshooter agent include an
**Input Safety** preamble (look for the `<!-- input-safety-v1 -->` marker) that
sanitises all user-supplied arguments before they reach the shell. State-changing
actions (block, forget, delete, restart, LED on/off) require explicit user
confirmation.

## Uninstall

```bash
claude plugin remove unifi
```

## License

MIT — see [github.com/ThrownLemon/claude-code-plugins](https://github.com/ThrownLemon/claude-code-plugins).
