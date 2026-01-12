---
description: Authenticate with CodeRabbit CLI
---

# CodeRabbit Authentication

Authenticate with the CodeRabbit CLI to enable code reviews.

## Authentication Flow

1. **Check Current Status**
   ```bash
   coderabbit auth status
   ```

2. **If Not Authenticated**
   - Run `coderabbit auth login`
   - A URL will be displayed
   - Open the URL in your browser
   - Log in with your CodeRabbit account
   - Copy the token shown after login
   - Paste the token back into Claude Code

3. **Verify Authentication**
   ```bash
   coderabbit auth status
   ```

## Prerequisites

The CodeRabbit CLI must be installed first:

```bash
curl -fsSL https://cli.coderabbit.ai/install.sh | sh
```

After installation, restart your shell:
```bash
source ~/.zshrc  # or ~/.bashrc
```

## Troubleshooting

**CLI not found:**
- Ensure installation completed successfully
- Restart your terminal or source your shell config
- Check if `coderabbit` or `cr` command is available

**Authentication failed:**
- Verify you have a CodeRabbit account
- Check the token was copied correctly
- Try logging out and back in: `coderabbit auth logout` then `coderabbit auth login`

**Rate limiting:**
- Free tier has limited reviews per hour
- Consider upgrading for higher limits
- Wait for the rate limit to reset

## Steps

Execute the following to check and guide authentication:

1. First, check if CLI is installed:
   ```bash
   which coderabbit || which cr
   ```

2. If not installed, inform the user to run:
   ```bash
   curl -fsSL https://cli.coderabbit.ai/install.sh | sh
   ```

3. Check authentication status:
   ```bash
   coderabbit auth status
   ```

4. If not authenticated, run:
   ```bash
   coderabbit auth login
   ```
   Then guide user through the browser-based authentication flow.

5. Verify successful authentication:
   ```bash
   coderabbit auth status
   ```
