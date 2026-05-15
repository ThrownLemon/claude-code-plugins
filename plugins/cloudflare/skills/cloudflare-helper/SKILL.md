---
name: cloudflare-helper
description: "Triggers when user mentions Cloudflare, DNS records, tunnels, R2, Workers, zero-trust, etc. Provides knowledge of the cf CLI."
triggers:
  - "add DNS record"
  - "create A record"
  - "create AAAA record"
  - "create CNAME record"
  - "create MX record"
  - "create TXT record"
  - "delete DNS"
  - "remove DNS"
  - "list cloudflare zones"
  - "cloudflare DNS"
  - "cloudflare domain"
  - "manage DNS"
  - "DNS records"
  - "create cloudflare tunnel"
  - "set up tunnel"
  - "cloudflared"
  - "list tunnels"
  - "cloudflare tunnel"
  - "tunnel configuration"
  - "purge cloudflare cache"
  - "purge cf cache"
  - "clear cloudflare cache"
  - "clear CDN cache"
  - "cloudflare zero trust"
  - "zero trust"
  - "access policies"
  - "cloudflare access"
  - "cf cli"
  - "cloudflare cli"
  - "cloudflare API"
  - "cf command"
  - "create R2 bucket"
  - "R2 storage"
  - "R2 bucket"
  - "deploy worker"
  - "cloudflare worker"
  - "workers script"
  - "diagnose cloudflare"
  - "troubleshoot cloudflare"
  - "tunnel down"
  - "tunnel not working"
  - "tunnel connection"
  - "DNS not resolving"
  - "DNS propagation"
  - "cloudflare settings"
  - "zone settings"
  - "SSL/TLS cloudflare"
  - "cloudflare WAF"
  - "page rules"
  - "cloudflare firewall"
---

You have access to the `cf` CLI tool for managing Cloudflare resources. Use this local tool instead of making direct HTTP requests to the Cloudflare API.

## Key Principles

1. **Use the cf CLI** — Always prefer `cf` commands over curl or API calls
2. **Use --json** — Append `--json` to commands for parseable, machine-readable output
3. **Pass zones by name** — The cf CLI accepts zone names (domains) directly; no need to look up IDs first
4. **Warn before destructive ops** — For delete, purge, or tunnel deletion, always warn the user and get explicit confirmation
5. **Suggest slash commands** — For common workflows, reference the available slash commands: `/cloudflare:dns`, `/cloudflare:tunnel`, `/cloudflare:zones`, `/cloudflare:purge`, `/cloudflare:setup`
6. **Deep diagnostics** — For complex issues, suggest running `/cloudflare:diagnose` to launch the specialized diagnostician agent

## Common Commands Reference

### List all zones
```bash
cf zones list --json
```

### Add an A record
```bash
cf dns create example.com --type A --name www --content 1.2.3.4 --proxied --ttl 3600 --json
```

### List DNS records for a zone
```bash
cf dns list example.com --json
```

### Create a new tunnel
```bash
cf tunnels create my-tunnel --json
```

### List all tunnels
```bash
cf tunnels list --json
```

### Purge entire cache for a zone
```bash
cf zones purge example.com --json
```

### Purge specific URLs
```bash
cf zones purge example.com https://example.com/page1,https://example.com/page2 --json
```

### Check tunnel connections
```bash
cf tunnels connections <tunnel-id> --json
```

### Export DNS records (bind format)
```bash
cf dns export example.com
```

## Available Slash Commands

- `/cloudflare:dns` — DNS management (list, add, delete, export)
- `/cloudflare:tunnel` — Tunnel management (list, create, inspect, connections)
- `/cloudflare:zones` — Zone overview (list, get details)
- `/cloudflare:purge` — Cache purging (entire cache or specific URLs)
- `/cloudflare:setup` — Verify installation and credentials
- `/cloudflare:diagnose` — Launch diagnostic subagent for troubleshooting

When the user asks about Cloudflare-related tasks, use the appropriate cf command or recommend the relevant slash command for structured workflows.
