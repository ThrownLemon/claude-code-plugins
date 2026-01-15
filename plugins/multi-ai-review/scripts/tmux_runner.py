#!/usr/bin/env python3
"""
Tmux-based parallel AI review runner.

Runs multiple AI CLIs in tmux split panes so you can watch them all simultaneously.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from cli_configs import CLI_CONFIGS, get_model


def get_output_dir() -> Path:
    """Get or create the output directory."""
    default = Path.home() / ".multi-ai-review"
    env_dir = os.environ.get("MULTI_REVIEW_OUTPUT_DIR", "")
    if env_dir:
        output_dir = Path(os.path.expanduser(os.path.expandvars(env_dir)))
    else:
        output_dir = default
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def generate_review_id() -> str:
    """Generate a unique review ID."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"review-{timestamp}-{unique_id}"


def check_tmux() -> bool:
    """Check if tmux is installed."""
    try:
        result = subprocess.run(["which", "tmux"], capture_output=True)
        return result.returncode == 0
    except Exception:
        return False


def check_cli_installed(cli: str) -> bool:
    """Check if a CLI is installed."""
    config = CLI_CONFIGS.get(cli)
    if not config:
        return False
    cmd_parts = config["check_cmd"].split()
    try:
        result = subprocess.run(cmd_parts, capture_output=True, timeout=10)
        return result.returncode == 0
    except Exception:
        return False


def build_cli_command(cli: str, prompt: str, output_file: Path) -> str:
    """Build the shell command to run a CLI and save output.

    Different CLIs need different handling:
    - Claude/Gemini: Use tee for output capture (don't need PTY)
    - Codex: Use script for PTY emulation (requires terminal)
    """
    config = CLI_CONFIGS.get(cli)
    if not config:
        raise ValueError(f"Unknown CLI: {cli}")

    model = get_model(cli)

    # Build the base CLI command
    # Models match fork-terminal defaults: claude=opus, gemini=gemini-3-pro-preview, codex=gpt-5.2-codex
    if cli == "claude":
        # Claude: use -p for prompt, --dangerously-skip-permissions for non-interactive
        # Claude doesn't need PTY, so use tee for live output capture
        cli_cmd = f'claude --model {model} --dangerously-skip-permissions -p {_shell_quote(prompt)}'
        cmd = f"{cli_cmd} 2>&1 | tee {output_file}"
    elif cli == "gemini":
        # Gemini: prompt as positional arg after flags, -y for auto-accept
        # Gemini doesn't need PTY, so use tee for live output capture
        cli_cmd = f'gemini --model {model} -y {_shell_quote(prompt)}'
        cmd = f"{cli_cmd} 2>&1 | tee {output_file}"
    elif cli == "codex":
        # Codex: requires PTY for interactive UI
        # Use script command to provide pseudo-terminal
        # On macOS, script syntax is: script [-q] file command [args...]
        # Quote the prompt directly, no need for sh -c wrapper
        quoted_prompt = _shell_quote(prompt)
        cmd = f"script -q {output_file} codex --model {model} --dangerously-bypass-approvals-and-sandbox {quoted_prompt}"
    else:
        raise ValueError(f"Unknown CLI: {cli}")

    return cmd


def _shell_quote(s: str) -> str:
    """Quote a string for shell use with double quotes."""
    # Use double quotes - escape backslash, double quote, dollar, backtick
    escaped = s.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$").replace("`", "\\`")
    return f'"{escaped}"'


def create_tmux_session(
    session_name: str,
    clis: list[str],
    prompt: str,
    output_dir: Path,
    project_root: str
) -> dict:
    """Create a tmux session with split panes for each CLI."""

    # Kill existing session if it exists
    subprocess.run(["tmux", "kill-session", "-t", session_name],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Create new detached session
    subprocess.run([
        "tmux", "new-session", "-d", "-s", session_name,
        "-c", project_root,
        "-x", "200", "-y", "50"  # Set initial size
    ], check=True)

    # Set up panes based on number of CLIs
    pane_ids = {}

    for i, cli in enumerate(clis):
        if i == 0:
            # First CLI uses the initial pane
            pane_ids[cli] = f"{session_name}:0.0"
        elif i == 1:
            # Second CLI: split horizontally
            subprocess.run([
                "tmux", "split-window", "-h", "-t", session_name,
                "-c", project_root
            ], check=True)
            pane_ids[cli] = f"{session_name}:0.1"
        elif i == 2:
            # Third CLI: split the first pane vertically
            subprocess.run([
                "tmux", "split-window", "-v", "-t", f"{session_name}:0.0",
                "-c", project_root
            ], check=True)
            # After split, pane IDs shift
            pane_ids[cli] = f"{session_name}:0.2"

    # Use tiled layout for even distribution
    subprocess.run(["tmux", "select-layout", "-t", session_name, "tiled"], check=True)

    # Add status bar showing CLI names
    subprocess.run([
        "tmux", "set-option", "-t", session_name, "pane-border-status", "top"
    ], capture_output=True)

    # Start each CLI in its pane
    results = {}
    for cli, pane_id in pane_ids.items():
        output_file = output_dir / f"{cli}.txt"
        cmd = build_cli_command(cli, prompt, output_file)

        # Set pane title
        subprocess.run([
            "tmux", "select-pane", "-t", pane_id,
            "-T", f"{cli.upper()}"
        ], capture_output=True)

        # Clear the pane first
        subprocess.run([
            "tmux", "send-keys", "-t", pane_id,
            "clear", "Enter"
        ])

        # Small delay to let clear complete
        time.sleep(0.1)

        # Send the CLI command directly (no echo wrapper)
        subprocess.run([
            "tmux", "send-keys", "-t", pane_id,
            cmd, "Enter"
        ])

        results[cli] = {
            "pane_id": pane_id,
            "output_file": str(output_file),
            "status": "running"
        }

    return results


def open_terminal_with_tmux(session_name: str) -> bool:
    """Open a new terminal tab and attach to the tmux session.

    Returns True if successful, False otherwise.
    """
    # Check if Warp is available (preferred)
    warp_exists = os.path.exists("/Applications/Warp.app")

    attach_cmd = f"tmux attach -t {session_name}"

    if warp_exists:
        # Use Warp - open new tab and type command
        escaped_cmd = attach_cmd.replace("\\", "\\\\").replace('"', '\\"')
        applescript = f'''
            tell application "Warp" to activate
            delay 0.5
            tell application "System Events"
                tell process "Warp"
                    keystroke "t" using command down
                    delay 0.5
                    keystroke "{escaped_cmd}"
                    delay 0.3
                    keystroke return
                end tell
            end tell
        '''
        try:
            result = subprocess.run(
                ["osascript", "-e", applescript],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            pass

    # Fallback to Terminal.app
    escaped_cmd = attach_cmd.replace("\\", "\\\\").replace('"', '\\"')
    try:
        result = subprocess.run(
            ["osascript", "-e", f'tell application "Terminal" to do script "{escaped_cmd}"'],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except Exception:
        return False


def attach_to_session(session_name: str):
    """Attach to the tmux session."""
    # Check if we're already in tmux
    if os.environ.get("TMUX"):
        # Switch to the session
        subprocess.run(["tmux", "switch-client", "-t", session_name])
    else:
        # Attach to session
        subprocess.run(["tmux", "attach-session", "-t", session_name])


def wait_for_completion(
    session_name: str,
    clis: list[str],
    output_dir: Path,
    timeout_minutes: int = 10
) -> dict:
    """Wait for all CLIs to complete and collect results."""
    start_time = time.time()
    timeout_seconds = timeout_minutes * 60

    results = {cli: {"status": "running"} for cli in clis}

    while time.time() - start_time < timeout_seconds:
        all_done = True

        for cli in clis:
            if results[cli]["status"] in ("complete", "failed", "timeout"):
                continue

            # Check if pane still has a running process
            pane_check = subprocess.run(
                ["tmux", "list-panes", "-t", session_name, "-F", "#{pane_pid}"],
                capture_output=True, text=True
            )

            # Check if output file exists and has content
            output_file = output_dir / f"{cli}.txt"
            if output_file.exists():
                content = output_file.read_text()
                # Look for completion markers
                if "session_id" in content or "error" in content.lower() or len(content) > 1000:
                    results[cli]["status"] = "complete"
                    results[cli]["output_file"] = str(output_file)
                    continue

            all_done = False

        if all_done:
            break

        time.sleep(5)

    # Mark any still-running as timeout
    for cli in clis:
        if results[cli]["status"] == "running":
            results[cli]["status"] = "timeout"

    return results


def run_tmux_review(
    clis: list[str],
    prompt: str,
    project_root: str,
    timeout: int = 10,
    attach: bool = True
) -> dict:
    """Run parallel reviews in tmux panes."""

    # Check tmux is available
    if not check_tmux():
        return {
            "success": False,
            "error": "tmux is not installed. Install with: brew install tmux"
        }

    # Check which CLIs are available
    available_clis = [cli for cli in clis if check_cli_installed(cli)]
    missing_clis = [cli for cli in clis if cli not in available_clis]

    if not available_clis:
        return {
            "success": False,
            "error": f"No CLIs available. Missing: {', '.join(missing_clis)}"
        }

    # Create output directory
    review_id = generate_review_id()
    output_dir = get_output_dir() / review_id
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save metadata
    metadata = {
        "review_id": review_id,
        "project_root": project_root,
        "prompt_length": len(prompt),
        "requested_clis": clis,
        "available_clis": available_clis,
        "missing_clis": missing_clis,
        "timeout_minutes": timeout,
        "mode": "tmux",
        "started": datetime.now(timezone.utc).isoformat()
    }

    with open(output_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    # Create tmux session
    session_name = f"multi-review-{review_id[-8:]}"

    print(f"Creating tmux session: {session_name}")
    print(f"Review ID: {review_id}")
    print(f"CLIs: {', '.join(available_clis)}")
    print(f"Output: {output_dir}")
    print()

    pane_results = create_tmux_session(
        session_name=session_name,
        clis=available_clis,
        prompt=prompt,
        output_dir=output_dir,
        project_root=project_root
    )

    result = {
        "success": True,
        "review_id": review_id,
        "session_name": session_name,
        "output_dir": str(output_dir),
        "available_clis": available_clis,
        "missing_clis": missing_clis,
        "panes": pane_results
    }

    # Print instructions
    print("=" * 60)
    print(f"Tmux session '{session_name}' created with {len(available_clis)} panes")
    print()
    print("To view the reviews:")
    print(f"  tmux attach -t {session_name}")
    print()
    print("Tmux controls:")
    print("  Ctrl+B then D  - Detach (reviews continue in background)")
    print("  Ctrl+B then [  - Scroll mode (q to exit)")
    print("  Ctrl+B then z  - Zoom current pane (toggle)")
    print("  Ctrl+B then o  - Switch between panes")
    print("=" * 60)

    if attach:
        print("\nOpening new terminal tab with tmux session...")
        if open_terminal_with_tmux(session_name):
            print("✓ Terminal opened successfully")
            result["terminal_opened"] = True
        else:
            print("Could not open terminal automatically.")
            print(f"Run: tmux attach -t {session_name}")
            result["terminal_opened"] = False

    return result


def main():
    parser = argparse.ArgumentParser(description="Tmux-based multi-AI review runner")
    parser.add_argument("--clis", default="claude,gemini,codex",
                        help="Comma-separated CLIs to use")
    parser.add_argument("--prompt", required=True, help="Review prompt")
    parser.add_argument("--project-root", default=".", help="Project directory")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout in minutes")
    parser.add_argument("--no-attach", action="store_true",
                        help="Don't attach to tmux session")
    parser.add_argument("--json", action="store_true", help="Output JSON")

    args = parser.parse_args()

    clis = [c.strip() for c in args.clis.split(",")]

    result = run_tmux_review(
        clis=clis,
        prompt=args.prompt,
        project_root=os.path.abspath(args.project_root),
        timeout=args.timeout,
        attach=not args.no_attach
    )

    if args.json:
        print(json.dumps(result, indent=2))
    elif not result.get("success"):
        print(f"Error: {result.get('error')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
