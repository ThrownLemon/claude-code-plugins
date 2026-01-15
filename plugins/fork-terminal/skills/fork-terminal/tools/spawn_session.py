#!/usr/bin/env python3
"""Terminal session spawning for fork-terminal worktree mode.

Supports tmux (if available) with fallback to new terminal windows.
"""

import os
import platform
import shlex
import subprocess
import sys
from typing import Optional, Tuple

# Import sibling modules
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from worktree_manager import (
    create_worktree,
    sanitize_branch_name,
    create_task_file,
    worktree_exists
)
from coordination import register_worker


# CLI configurations for tournament mode
CLI_CONFIGS = {
    "claude": {
        "command_template": "claude --model {model} --dangerously-skip-permissions {mode_flag} '{prompt}'",
        "default_model": "opus-4-5",
        "fast_model": "sonnet-4-5",
        "interactive_flag": "",  # No -p flag for interactive
        "autonomous_flag": "-p"  # -p flag for autonomous (run and exit)
    },
    "gemini": {
        "command_template": "gemini --model {model} -y -i '{prompt}'",
        "default_model": "gemini-3-pro-preview",
        "fast_model": "gemini-3-flash-preview",
        "interactive_flag": "",
        "autonomous_flag": ""
    },
    "codex": {
        "command_template": "codex --model {model} --dangerously-bypass-approvals-and-sandbox '{prompt}'",
        "default_model": "gpt-5.2-codex",
        "fast_model": "gpt-5.1-codex-mini",
        "interactive_flag": "",
        "autonomous_flag": ""
    }
}


def detect_terminal_env() -> str:
    """Detect the available terminal environment.

    Returns:
        One of: "tmux_attached", "tmux_available", "window"
    """
    # Check if we're in Warp terminal (doesn't support tmux)
    term_program = os.environ.get("TERM_PROGRAM", "")
    if term_program == "WarpTerminal":
        return "window"  # Warp doesn't support tmux, use window mode

    # Check if tmux is installed
    tmux_check = subprocess.run(
        ["which", "tmux"],
        capture_output=True,
        text=True
    )

    if tmux_check.returncode != 0:
        return "window"  # tmux not installed

    # Check if we're inside a tmux session
    if os.environ.get("TMUX"):
        return "tmux_attached"

    # tmux is installed but we're not inside a session
    return "tmux_available"


def is_tmux_available() -> bool:
    """Check if tmux is installed.

    Returns:
        True if tmux is available.
    """
    result = subprocess.run(["which", "tmux"], capture_output=True)
    return result.returncode == 0


def tmux_session_exists(session_name: str) -> bool:
    """Check if a tmux session with the given name exists.

    Args:
        session_name: Name of the session to check.

    Returns:
        True if the session exists.
    """
    result = subprocess.run(
        ["tmux", "has-session", "-t", session_name],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def spawn_tmux_session(
    cwd: str,
    command: str,
    session_name: Optional[str] = None,
    window_name: Optional[str] = None
) -> Tuple[str, Optional[int]]:
    """Spawn a Claude session in tmux.

    Args:
        cwd: Working directory for the session.
        command: Command to run.
        session_name: Name for the tmux session (if creating new or adding to).
        window_name: Name for the tmux window.

    Returns:
        Tuple of (status message, pid if available).
    """
    env = detect_terminal_env()
    safe_cwd = shlex.quote(cwd)
    full_command = f"cd {safe_cwd} && {command}"

    if env == "tmux_attached":
        # We're inside tmux - create a new window
        cmd = ["tmux", "new-window", "-c", cwd]
        if window_name:
            cmd.extend(["-n", window_name])
        cmd.append(command)

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return f"Created new tmux window: {window_name or 'worktree'}", None
        else:
            return f"tmux error: {result.stderr.strip()}", None

    else:
        # Not inside tmux - check if session already exists
        session = session_name or f"worktree-{os.getpid()}"

        if tmux_session_exists(session):
            # Session exists - create a new window in it
            cmd = [
                "tmux", "new-window",
                "-t", session,
                "-c", cwd,
            ]
            if window_name:
                cmd.extend(["-n", window_name])
            cmd.append(command)

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return f"Added window to session: {session}", None
            else:
                return f"tmux error: {result.stderr.strip()}", None
        else:
            # Create a new detached session
            cmd = [
                "tmux", "new-session",
                "-d",  # detached
                "-c", cwd,
                "-s", session,
            ]
            if window_name:
                cmd.extend(["-n", window_name])
            cmd.append(command)

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Created tmux session '{session}'. Attach with: tmux attach -t {session}")
                return f"Created tmux session: {session}", None
            else:
                return f"tmux error: {result.stderr.strip()}", None


def spawn_terminal_window(cwd: str, command: str) -> Tuple[str, Optional[int]]:
    """Spawn a session in a new terminal window (fallback).

    Uses the same approach as fork_terminal.py.

    Args:
        cwd: Working directory for the session.
        command: Command to run.

    Returns:
        Tuple of (status message, pid if available).
    """
    system = platform.system()
    safe_cwd = shlex.quote(cwd)
    full_command = f"cd {safe_cwd} && {command}"

    # Check terminal preference
    terminal = os.environ.get("FORK_TERMINAL", "auto")

    if terminal == "auto":
        # Check if Warp is installed (macOS)
        if system == "Darwin":
            warp_exists = os.path.exists("/Applications/Warp.app")
            terminal = "warp" if warp_exists else "terminal"
        else:
            terminal = "terminal"

    if system == "Darwin":  # macOS
        if terminal == "warp":
            # Warp: use semicolon to chain commands (more reliable than &&)
            warp_cmd = f"cd {shlex.quote(cwd)} ; {command}"
            escaped_cmd = warp_cmd.replace('"', '\\"')

            applescript = f'''
                set the clipboard to "{escaped_cmd}"

                tell application "Warp" to activate
                delay 0.5

                tell application "System Events"
                    tell process "Warp"
                        -- Open new tab
                        keystroke "t" using command down
                        delay 1.2

                        -- Click to ensure focus
                        click at {{400, 400}}
                        delay 0.3

                        -- Paste and execute
                        keystroke "v" using command down
                        delay 0.5
                        keystroke return

                        -- Wait for command to start before script returns
                        delay 3.0
                    end tell
                end tell
            '''
            result = subprocess.run(
                ["osascript", "-e", applescript],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return "Warp terminal launched", None
            else:
                return f"Warp error: {result.stderr.strip()}", None

        if terminal == "terminal":
            # Terminal.app
            escaped_cmd = full_command.replace("\\", "\\\\").replace('"', '\\"')
            result = subprocess.run(
                ["osascript", "-e", f'tell application "Terminal" to do script "{escaped_cmd}"'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return "Terminal.app launched", None
            else:
                return f"Terminal error: {result.stderr.strip()}", None

    elif system == "Windows":
        safe_cwd_win = cwd.replace("\\", "\\\\").replace('"', '""')
        full_cmd_win = f'cd /d "{safe_cwd_win}" && {command}'
        try:
            proc = subprocess.Popen(
                ["cmd", "/c", "start", "cmd", "/k", full_cmd_win]
            )
            return "Windows terminal launched", proc.pid
        except Exception as e:
            return f"Windows error: {e}", None

    else:
        return f"Platform {system} not supported", None


def build_claude_command(
    task: str,
    model: str = "opus",
    mode: str = "interactive",
    prompt: Optional[str] = None
) -> str:
    """Build the Claude CLI command.

    Args:
        task: Task description.
        model: Claude model to use.
        mode: Execution mode - "interactive" (stays open) or "autonomous" (runs and exits).
        prompt: Custom initial prompt (default: read TASK.md).

    Returns:
        Claude command string.
    """
    if prompt is None:
        prompt = "Read TASK.md in your current directory and begin working on the assigned task."

    # Escape the prompt for shell
    safe_prompt = prompt.replace("'", "'\\''")

    if mode == "autonomous":
        # Use -p flag to run prompt and exit when done
        return f"claude --model {model} --dangerously-skip-permissions -p '{safe_prompt}'"
    else:
        # Interactive mode: pass prompt as argument (without -p) to start interactive with initial message
        return f"claude --model {model} --dangerously-skip-permissions '{safe_prompt}'"


def build_cli_command(
    cli: str,
    task: str,
    model: str = None,
    mode: str = "autonomous",
    prompt: Optional[str] = None
) -> str:
    """Build command for any supported CLI.

    Args:
        cli: CLI type ("claude", "gemini", "codex").
        task: Task description.
        model: Model to use (default: from CLI_CONFIGS).
        mode: Execution mode - "interactive" or "autonomous".
        prompt: Custom prompt (default: read TASK.md).

    Returns:
        CLI command string.
    """
    if cli not in CLI_CONFIGS:
        raise ValueError(f"Unsupported CLI: {cli}. Supported: {list(CLI_CONFIGS.keys())}")

    config = CLI_CONFIGS[cli]

    # Use default model if not specified
    if model is None:
        model = config["default_model"]

    # Build prompt
    if prompt is None:
        prompt = "Read TASK.md in your current directory and begin working on the assigned task."

    # Escape the prompt for shell (single quote escape for single-quoted strings)
    safe_prompt = prompt.replace("'", "'\\''")

    # Escape the model name to prevent shell injection
    safe_model = shlex.quote(model).strip("'")  # Remove quotes since template adds them

    # Get mode flag (these are trusted values from config)
    mode_flag = config["autonomous_flag"] if mode == "autonomous" else config["interactive_flag"]

    # Build command from template
    cmd = config["command_template"].format(
        model=safe_model,
        mode_flag=mode_flag,
        prompt=safe_prompt
    )

    # Clean up extra spaces from empty mode_flag
    cmd = " ".join(cmd.split())

    return cmd


def spawn_claude_in_worktree(
    task: str,
    branch: Optional[str] = None,
    base: str = "HEAD",
    count: int = 1,
    model: str = "opus",
    mode: str = "interactive",
    terminal: str = "auto"
) -> dict:
    """Create worktree(s) and spawn Claude session(s).

    This is the main entry point for worktree spawning.

    Args:
        task: Task description.
        branch: Branch name (default: auto-generate from task).
        base: Base commit/branch to start from.
        count: Number of workers to spawn (1-4).
        model: Claude model to use.
        mode: Execution mode - "interactive" (stays open) or "autonomous" (runs and exits).
        terminal: Terminal type: "tmux", "window", or "auto".

    Returns:
        Dictionary with results:
        {
            "success": bool,
            "workers": [{"id": int, "path": str, "branch": str, "status": str}],
            "errors": [str]
        }
    """
    results = {
        "success": True,
        "workers": [],
        "errors": []
    }

    # Validate count
    if count < 1 or count > 4:
        results["success"] = False
        results["errors"].append("Worker count must be between 1 and 4")
        return results

    # Determine terminal type
    if terminal == "auto":
        env = detect_terminal_env()
        use_tmux = env in ("tmux_attached", "tmux_available")
    else:
        use_tmux = terminal == "tmux"

    # Spawn workers
    for i in range(count):
        worker_num = i + 1
        worker_suffix = f"-{worker_num}" if count > 1 else ""

        # Generate branch name
        if branch:
            worker_branch = f"{branch}{worker_suffix}" if count > 1 else branch
        else:
            base_branch = sanitize_branch_name(task)
            worker_branch = f"{base_branch}{worker_suffix}" if count > 1 else base_branch

        try:
            # Check if worktree already exists
            existing_path = worktree_exists(worker_branch)
            if existing_path:
                results["errors"].append(f"Worktree already exists for branch {worker_branch}: {existing_path}")
                continue

            # Create worktree
            worktree_path = create_worktree(
                branch=worker_branch,
                base=base,
                create_branch=True
            )

            # Create TASK.md
            worker_task = task
            if count > 1:
                worker_task = f"{task}\n\n(Worker {worker_num} of {count})"
            create_task_file(worktree_path, worker_task, worker_branch, worker_num)

            # Build Claude command
            claude_cmd = build_claude_command(task=worker_task, model=model, mode=mode)

            # Spawn session
            window_name = f"worker-{worker_num}" if count > 1 else "worktree"

            if use_tmux:
                status, pid = spawn_tmux_session(
                    cwd=worktree_path,
                    command=claude_cmd,
                    window_name=window_name
                )
            else:
                status, pid = spawn_terminal_window(
                    cwd=worktree_path,
                    command=claude_cmd
                )

                # Add delay between workers for Warp automation to complete
                if count > 1 and worker_num < count:
                    import time
                    time.sleep(6)  # Wait for Warp automation to finish

            # Register worker
            terminal_type = "tmux" if use_tmux else "window"
            worker_id = register_worker(
                path=worktree_path,
                branch=worker_branch,
                task=task,
                pid=pid,
                terminal=terminal_type
            )

            results["workers"].append({
                "id": worker_id,
                "path": worktree_path,
                "branch": worker_branch,
                "status": status
            })

        except Exception as e:
            results["errors"].append(f"Worker {worker_num}: {str(e)}")
            results["success"] = False

    # Set overall success based on workers spawned
    if not results["workers"]:
        results["success"] = False

    return results


# CLI interface
if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Spawn Claude sessions in worktrees")
    parser.add_argument("--task", "-t", required=True, help="Task description")
    parser.add_argument("--branch", "-b", help="Branch name (default: auto from task)")
    parser.add_argument("--base", default="HEAD", help="Base commit/branch")
    parser.add_argument("--count", "-n", type=int, default=1, help="Number of workers (1-4)")
    parser.add_argument("--model", "-m", default="opus", help="Claude model")
    parser.add_argument("--mode", choices=["interactive", "autonomous"], default="interactive",
                        help="Execution mode: interactive (stays open) or autonomous (runs and exits)")
    parser.add_argument("--terminal", choices=["auto", "tmux", "window"], default="auto",
                        help="Terminal type")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    try:
        results = spawn_claude_in_worktree(
            task=args.task,
            branch=args.branch,
            base=args.base,
            count=args.count,
            model=args.model,
            mode=args.mode,
            terminal=args.terminal
        )

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            if results["success"]:
                print(f"Successfully spawned {len(results['workers'])} worker(s):")
                for w in results["workers"]:
                    print(f"  Worker {w['id']}: {w['branch']}")
                    print(f"    Path: {w['path']}")
                    print(f"    Status: {w['status']}")
            else:
                print("Failed to spawn workers:")

            if results["errors"]:
                print("\nErrors:")
                for err in results["errors"]:
                    print(f"  - {err}")

            sys.exit(0 if results["success"] else 1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
