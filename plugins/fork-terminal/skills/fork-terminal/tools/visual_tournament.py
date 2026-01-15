#!/usr/bin/env python3
"""Visual tmux mode for fork-terminal tournaments.

Runs multiple AI CLIs in tmux split panes so you can watch them all simultaneously.
Similar to multi-ai-review's tmux_runner.py but integrated with fork-terminal.
"""

import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

# Import sibling modules
sys.path.insert(0, str(Path(__file__).parent))

from spawn_session import CLI_CONFIGS
from worktree_manager import (
    create_worktree,
    sanitize_branch_name,
    worktree_exists
)
from coordination import register_tournament, register_worker
from tournament import create_tournament_task_file


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
    cmd_name = config.get("command_template", "").split()[0]
    if not cmd_name:
        return False
    try:
        result = subprocess.run(["which", cmd_name], capture_output=True, timeout=10)
        return result.returncode == 0
    except Exception:
        return False


def _shell_quote(s: str) -> str:
    """Quote a string for shell use."""
    # Use $'...' syntax for strings with special characters
    escaped = s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
    return f"$'{escaped}'"


def build_visual_cli_command(cli: str, prompt: str, output_file: Path, model: str = None) -> str:
    """Build the shell command to run a CLI with PTY and output capture.

    Uses 'script' command to provide a PTY while capturing output,
    so CLIs that require a terminal work properly.
    """
    config = CLI_CONFIGS.get(cli)
    if not config:
        raise ValueError(f"Unknown CLI: {cli}")

    if model is None:
        model = config["default_model"]

    # Build the base CLI command based on CLI type
    if cli == "claude":
        cli_cmd = f'claude --model {model} --dangerously-skip-permissions -p {_shell_quote(prompt)}'
    elif cli == "gemini":
        cli_cmd = f'gemini --model {model} -y {_shell_quote(prompt)}'
    elif cli == "codex":
        cli_cmd = f'codex --model {model} --dangerously-bypass-approvals-and-sandbox {_shell_quote(prompt)}'
    else:
        raise ValueError(f"Unknown CLI: {cli}")

    # Wrap with 'script' to provide PTY and capture output
    escaped_cli_cmd = cli_cmd.replace("'", "'\\''")
    cmd = f"script -q {output_file} sh -c '{escaped_cli_cmd}'"

    return cmd


def create_visual_tmux_session(
    session_name: str,
    clis: List[str],
    prompt: str,
    output_dir: Path,
    project_root: str,
    model_config: dict = None
) -> dict:
    """Create a tmux session with split panes for each CLI.

    Args:
        session_name: Name for the tmux session.
        clis: List of CLI types to run.
        prompt: The prompt to send to each CLI.
        output_dir: Directory to store output files.
        project_root: Working directory for the CLIs.
        model_config: Optional dict mapping CLI to model.

    Returns:
        Dict with pane info for each CLI.
    """
    if model_config is None:
        model_config = {}

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
        model = model_config.get(cli)
        cmd = build_visual_cli_command(cli, prompt, output_file, model)

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

        # Send the CLI command
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


def spawn_visual_tournament(
    task: str,
    clis: List[str] = None,
    base: str = "HEAD",
    model_config: dict = None,
    output_dir: Path = None,
    attach: bool = True
) -> dict:
    """Spawn a visual tournament with split panes for each CLI.

    Unlike regular tournament mode which creates separate worktrees,
    visual mode runs all CLIs in the same project with split panes
    for live viewing.

    Args:
        task: Task description / prompt for the CLIs.
        clis: List of CLI types (default: ["claude", "gemini", "codex"]).
        base: Base branch (for worktree mode, currently unused).
        model_config: Optional dict mapping CLI to model.
        output_dir: Directory for output files (auto-generated if None).
        attach: Whether to attach to the tmux session after creation.

    Returns:
        Dict with tournament results.
    """
    if clis is None:
        clis = ["claude", "gemini", "codex"]

    if model_config is None:
        model_config = {}

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
    if output_dir is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        output_dir = Path.home() / ".fork-terminal" / "visual" / f"visual-{timestamp}-{unique_id}"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Get project root
    project_root = os.getcwd()

    # Generate session name
    session_name = f"visual-{datetime.now().strftime('%H%M%S')}"

    print(f"Creating visual tmux session: {session_name}")
    print(f"CLIs: {', '.join(available_clis)}")
    print(f"Output: {output_dir}")
    print()

    pane_results = create_visual_tmux_session(
        session_name=session_name,
        clis=available_clis,
        prompt=task,
        output_dir=output_dir,
        project_root=project_root,
        model_config=model_config
    )

    result = {
        "success": True,
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
    print("To view the session:")
    print(f"  tmux attach -t {session_name}")
    print()
    print("Tmux controls:")
    print("  Ctrl+B then D  - Detach (CLIs continue in background)")
    print("  Ctrl+B then [  - Scroll mode (q to exit)")
    print("  Ctrl+B then z  - Zoom current pane (toggle)")
    print("  Ctrl+B then o  - Switch between panes")
    print("=" * 60)

    if attach:
        print("\nAttaching to session...")
        attach_to_session(session_name)

    return result


def attach_to_session(session_name: str):
    """Attach to the tmux session."""
    # Check if we're already in tmux
    if os.environ.get("TMUX"):
        # Switch to the session
        subprocess.run(["tmux", "switch-client", "-t", session_name])
    else:
        # Attach to session
        subprocess.run(["tmux", "attach-session", "-t", session_name])


# CLI interface
if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Visual tmux mode for fork-terminal")
    parser.add_argument("--task", "-t", required=True, help="Task/prompt for the CLIs")
    parser.add_argument("--clis", "-c", default="claude,gemini,codex",
                        help="Comma-separated CLIs to use")
    parser.add_argument("--no-attach", action="store_true",
                        help="Don't attach to tmux session")
    parser.add_argument("--json", action="store_true", help="Output JSON")

    args = parser.parse_args()

    clis = [c.strip() for c in args.clis.split(",")]

    result = spawn_visual_tournament(
        task=args.task,
        clis=clis,
        attach=not args.no_attach
    )

    if args.json:
        print(json.dumps(result, indent=2))
    elif not result.get("success"):
        print(f"Error: {result.get('error')}", file=sys.stderr)
        sys.exit(1)
