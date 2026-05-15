# Cloudflare Plugin

Manage your Cloudflare infrastructure directly from Claude Code using the `cf` CLI.

## Installation

```
/plugin install cloudflare@travis-plugins
```

## Prerequisites

Before using this plugin, ensure you have:

1. **cf CLI installed** - The plugin wraps the local `cf` binary available at `github.com/ThrownLemon/cloudflare-cli`. Install it following the repository's instructions.

2. **Credentials configured** - Place your Cloudflare API credentials in `~/.cloudflare/.env`:

   ```
   CF_API_KEY=your_api_key_here
   CF_API_EMAIL=your_email@example.com
   CF_ACCOUNT_ID=your_account_id
   ```

   Alternatively, set these as environment variables.

## Slash Commands

### `/cloudflare:dns` - DNS Record Management

List, add, delete, or export DNS records for your zones.

**Actions:**
- `list` - View all DNS records for a zone
- `add` - Create a new DNS record
- `delete` - Remove a DNS record
- `export` - Export all records in bind format

**Example usage:**
- `/cloudflare:dns action=list zone=example.com`
- `/cloudflare:dns action=add zone=example.com record-type=A name=www content=1.2.3.4`

### `/cloudflare:tunnel` - Cloudflare Tunnel Management

Create, inspect, and manage Cloudflare Tunnels for secure access to internal services.

**Actions:**
- `list` - List all tunnels in your account
- `create` - Create a new tunnel
- `get` - Get tunnel details and configuration
- `connections` - View active tunnel connections
- `routes` - List or configure tunnel routes

**Example usage:**
- `/cloudflare:tunnel action=list`
- `/cloudflare:tunnel action=create name-or-id=my-tunnel`

### `/cloudflare:zones` - Zone Overview

Quickly view all your zones or get detailed information about a specific zone.

**Example usage:**
- `/cloudflare:zones`
- `/cloudflare:zones action=get zone=example.com`

### `/cloudflare:purge` - Cache Purging

Purge cached content from Cloudflare's edge servers. Use carefully — this impacts live traffic.

**Example usage:**
- `/cloudflare:purge zone=example.com` — Purge entire cache
- `/cloudflare:purge zone=example.com url=https://example.com/page1,https://example.com/page2` — Purge specific URLs

### `/cloudflare:setup` - Installation Verification

Verify that the `cf` CLI is properly installed and your credentials are configured.

**Example usage:**
- `/cloudflare:setup`

### `/cloudflare:diagnose` - Issue Diagnostics

Launch the diagnostic subagent to troubleshoot Cloudflare issues like tunnels not connecting, DNS not resolving, cache problems, or access control issues.

**Example usage:**
- `/cloudflare:diagnose problem="tunnel not connecting" zone=example.com`

## Auto-Triggered Skill

The plugin includes an auto-triggered skill that activates when you mention Cloudflare-related topics:

- Adding or managing DNS records
- Creating or listing Cloudflare tunnels
- Purging cache
- Zero Trust and access policies
- R2 buckets and Workers
- General Cloudflare CLI usage
- Diagnosing Cloudflare issues

Simply describe what you want to do in natural language, and Claude will use the appropriate `cf` commands to help.

## Safety Features

- **Destructive operations require confirmation** — Deletes, purges, and other destructive actions will always prompt for confirmation before executing.
- **JSON output parsing** — All commands use `--json` flags for reliable, machine-readable output.
- **Credential verification** — Setup commands verify your credentials before attempting operations.

## Need Help?

Run `/cloudflare:setup` to verify your installation and credentials are correct.
