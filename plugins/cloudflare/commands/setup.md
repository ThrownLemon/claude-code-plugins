---
description: Verify cf CLI installation and credentials
---

You are verifying that the Cloudflare plugin environment is correctly set up.

Run the following checks:

1. **Check cf CLI installation:**
   - Run `which cf` or check if `cf` command exists
   - If not found, inform the user: "The cf CLI is not installed or not in your PATH. Please install it from github.com/ThrownLemon/cloudflare-cli"
   - If found, display the version by running `cf --version`

2. **Check credentials configuration (without printing secrets):**
   - Confirm `~/.cloudflare/.env` exists: `[ -f ~/.cloudflare/.env ] && echo present || echo missing`
   - Confirm the required variable **names** are present without revealing values:
     ```bash
     for k in CF_API_KEY CF_API_EMAIL CF_ACCOUNT_ID; do
       grep -q "^${k}=" ~/.cloudflare/.env 2>/dev/null && echo "$k: set in .env" || echo "$k: not in .env"
     done
     ```
   - Optionally check whether the variables are in the process environment (`[ -n "$CF_API_KEY" ]` etc.) — again without echoing their values.
   - **Never `cat` the .env file or print its values.** Only report whether each key name exists.
   - If neither source has the required variables, instruct the user: "Cloudflare credentials not found. Please configure them in ~/.cloudflare/.env with CF_API_KEY, CF_API_EMAIL, and CF_ACCOUNT_ID."

3. **Test API connectivity:**
   - Run `cf zones list --json` to verify credentials work
   - If successful, display: "✓ API connectivity verified"
   - If failed, display the error and suggest checking credentials

4. **Generate a status summary:**
   ```
   Cloudflare Plugin Setup Status:
   
   cf CLI: [installed/not installed]
   Version: [version if available]
   Credentials: [configured/missing]
   API Connectivity: [working/failed]
   
   Zones accessible: [count of zones]
   ```

If any checks fail, provide clear instructions on how to fix the issue.
