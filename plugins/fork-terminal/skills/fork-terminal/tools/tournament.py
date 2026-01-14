#!/usr/bin/env python3
"""Tournament mode for fork-terminal.

Spawns multiple AI CLIs (Claude, Gemini, Codex) to compete on the same task
in separate worktrees, then reviews solutions and creates a combined branch.
"""

import os
import sys
import time
from pathlib import Path
from typing import List, Optional

# Import sibling modules
sys.path.insert(0, str(Path(__file__).parent))

from worktree_manager import (
    create_worktree,
    sanitize_branch_name,
    worktree_exists
)
from coordination import (
    register_tournament,
    get_tournament,
    get_active_tournaments,
    get_all_tournaments,
    update_tournament,
    mark_tournament_worker_done,
    check_tournament_completion,
    register_worker
)
from spawn_session import (
    CLI_CONFIGS,
    build_cli_command,
    detect_terminal_env,
    spawn_tmux_session,
    spawn_terminal_window
)


def create_tournament_task_file(
    worktree_path: str,
    task: str,
    tournament_id: str,
    cli: str,
    branch: str,
    worker_id: int,
    other_clis: List[str]
) -> str:
    """Create TASK.md for a tournament worker with DONE.md instructions.

    Args:
        worktree_path: Path to the worktree.
        task: Task description.
        tournament_id: Tournament ID.
        cli: This worker's CLI type.
        branch: Branch name.
        worker_id: Worker ID.
        other_clis: List of other CLIs competing.

    Returns:
        Path to the created TASK.md file.
    """
    others = ", ".join(other_clis) if other_clis else "none"

    content = f"""# Tournament Task Assignment

## Task
{task}

## Tournament Context
- **Tournament ID**: `{tournament_id}`
- **Your CLI**: `{cli}` (competing against: {others})
- **Branch**: `{branch}`
- **Worktree**: `{worktree_path}`
- **Worker ID**: {worker_id}

## Instructions
1. Work on the task described above
2. Commit your changes as you go
3. **When complete, create DONE.md** in this directory with:
   - Summary of your approach
   - List of files modified
   - Key decisions made
   - Any trade-offs

## DONE.md Template

When finished, create a file called `DONE.md` with this structure:

```markdown
# Solution Complete

## Summary
[Brief description of your approach - 2-3 sentences]

## Files Modified
- path/to/file1.ts - [what was changed]
- path/to/file2.ts - [what was changed]

## Key Decisions
- [Decision 1 and why you made it]
- [Decision 2 and why you made it]

## Trade-offs
- [Any limitations or trade-offs in your solution]
```

## IMPORTANT
Your solution will not be reviewed until DONE.md exists in this directory!
"""

    task_file = os.path.join(worktree_path, "TASK.md")
    with open(task_file, "w") as f:
        f.write(content)

    return task_file


def spawn_tournament(
    task: str,
    clis: List[str] = None,
    base: str = "HEAD",
    model_config: dict = None,
    terminal: str = "auto"
) -> dict:
    """Spawn a tournament with multiple CLIs competing on the same task.

    Args:
        task: Task description.
        clis: List of CLI types to use (default: ["claude", "gemini", "codex"]).
        base: Base commit/branch to start from.
        model_config: Optional dict mapping CLI to model (e.g., {"claude": "haiku"}).
        terminal: Terminal type: "tmux", "window", or "auto".

    Returns:
        Dictionary with results:
        {
            "success": bool,
            "tournament_id": str,
            "workers": [{"worker_id": int, "cli": str, "path": str, "branch": str, "status": str}],
            "errors": [str]
        }
    """
    if clis is None:
        clis = ["claude", "gemini", "codex"]

    if model_config is None:
        model_config = {}

    results = {
        "success": True,
        "tournament_id": None,
        "workers": [],
        "errors": []
    }

    # Validate CLIs
    for cli in clis:
        if cli not in CLI_CONFIGS:
            results["errors"].append(f"Unsupported CLI: {cli}")
            results["success"] = False
            return results

    # Determine terminal type
    if terminal == "auto":
        env = detect_terminal_env()
        use_tmux = env in ("tmux_attached", "tmux_available")
    else:
        use_tmux = terminal == "tmux"

    # Generate base branch name from task
    base_branch = sanitize_branch_name(task)

    # Spawn workers for each CLI
    worker_data = []
    for i, cli in enumerate(clis):
        worker_id = i + 1
        worker_branch = f"tournament/{base_branch}-{cli}-{worker_id}"

        try:
            # Check if worktree already exists
            existing_path = worktree_exists(worker_branch)
            if existing_path:
                results["errors"].append(
                    f"Worktree already exists for branch {worker_branch}: {existing_path}"
                )
                continue

            # Create worktree
            worktree_path = create_worktree(
                branch=worker_branch,
                base=base,
                create_branch=True
            )

            # Determine other CLIs for context
            other_clis = [c for c in clis if c != cli]

            worker_data.append({
                "worker_id": worker_id,
                "cli": cli,
                "path": worktree_path,
                "branch": worker_branch,
                "other_clis": other_clis
            })

        except Exception as e:
            results["errors"].append(f"Worker {worker_id} ({cli}): {str(e)}")
            results["success"] = False

    if not worker_data:
        results["success"] = False
        return results

    # Register tournament (this generates the tournament_id)
    tournament_id = register_tournament(
        task=task,
        workers=worker_data,
        clis=clis,
        base=base
    )
    results["tournament_id"] = tournament_id

    # Now spawn sessions for each worker
    for worker in worker_data:
        try:
            # Create TASK.md with tournament context
            create_tournament_task_file(
                worktree_path=worker["path"],
                task=task,
                tournament_id=tournament_id,
                cli=worker["cli"],
                branch=worker["branch"],
                worker_id=worker["worker_id"],
                other_clis=worker["other_clis"]
            )

            # Get model for this CLI
            model = model_config.get(worker["cli"])

            # Build CLI command (always autonomous for tournament)
            cli_cmd = build_cli_command(
                cli=worker["cli"],
                task=task,
                model=model,
                mode="autonomous"
            )

            # Spawn session
            window_name = f"tournament-{worker['cli']}"

            if use_tmux:
                status, pid = spawn_tmux_session(
                    cwd=worker["path"],
                    command=cli_cmd,
                    window_name=window_name
                )
            else:
                status, pid = spawn_terminal_window(
                    cwd=worker["path"],
                    command=cli_cmd
                )

                # Add delay between workers for terminal automation
                if len(worker_data) > 1 and worker["worker_id"] < len(worker_data):
                    time.sleep(4)

            # Also register as a regular worker for tracking
            register_worker(
                path=worker["path"],
                branch=worker["branch"],
                task=f"[Tournament: {tournament_id}] {task}",
                pid=pid,
                terminal="tmux" if use_tmux else "window"
            )

            results["workers"].append({
                "worker_id": worker["worker_id"],
                "cli": worker["cli"],
                "path": worker["path"],
                "branch": worker["branch"],
                "status": status
            })

        except Exception as e:
            results["errors"].append(f"Spawning {worker['cli']}: {str(e)}")

    # Set overall success
    if not results["workers"]:
        results["success"] = False

    return results


def get_tournament_status(tournament_id: str = None) -> dict:
    """Get status of tournaments.

    Args:
        tournament_id: Specific tournament ID, or None for all active.

    Returns:
        Status dictionary with tournament info and completion status.
    """
    if tournament_id:
        tournament = get_tournament(tournament_id)
        if not tournament:
            return {"error": f"Tournament not found: {tournament_id}"}

        completion = check_tournament_completion(tournament_id)

        # Check for DONE.md files
        for worker in tournament.workers:
            done_path = os.path.join(worker.path, "DONE.md")
            if os.path.exists(done_path) and not worker.done:
                mark_tournament_worker_done(tournament_id, worker.worker_id, done_path)

        # Refresh completion status after checking files
        completion = check_tournament_completion(tournament_id)

        return {
            "tournament": {
                "id": tournament.id,
                "task": tournament.task,
                "status": tournament.status,
                "started": tournament.started,
                "clis": tournament.clis,
                "base": tournament.base,
                "combined_branch": tournament.combined_branch
            },
            "workers": [
                {
                    "worker_id": w.worker_id,
                    "cli": w.cli,
                    "path": w.path,
                    "branch": w.branch,
                    "done": w.done,
                    "completed_at": w.completed_at
                }
                for w in tournament.workers
            ],
            "completion": completion
        }
    else:
        # Get all active tournaments
        tournaments = get_active_tournaments()
        return {
            "active_tournaments": [
                {
                    "id": t.id,
                    "task": t.task,
                    "status": t.status,
                    "clis": t.clis,
                    "worker_count": len(t.workers),
                    "done_count": sum(1 for w in t.workers if w.done)
                }
                for t in tournaments
            ]
        }


# CLI interface
if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Tournament mode for fork-terminal")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Spawn command
    spawn_parser = subparsers.add_parser("spawn", help="Spawn a tournament")
    spawn_parser.add_argument("--task", "-t", required=True, help="Task description")
    spawn_parser.add_argument("--clis", "-c", help="Comma-separated CLIs (default: claude,gemini,codex)")
    spawn_parser.add_argument("--base", "-b", default="HEAD", help="Base branch/commit")
    spawn_parser.add_argument("--terminal", choices=["auto", "tmux", "window"], default="auto")
    spawn_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Status command
    status_parser = subparsers.add_parser("status", help="Get tournament status")
    status_parser.add_argument("--tournament", "-t", help="Tournament ID (default: all active)")
    status_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # List command
    list_parser = subparsers.add_parser("list", help="List all tournaments")
    list_parser.add_argument("--all", action="store_true", help="Include completed tournaments")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    try:
        if args.command == "spawn":
            clis = args.clis.split(",") if args.clis else None
            results = spawn_tournament(
                task=args.task,
                clis=clis,
                base=args.base,
                terminal=args.terminal
            )

            if args.json:
                print(json.dumps(results, indent=2))
            else:
                if results["success"]:
                    print(f"Tournament spawned: {results['tournament_id']}")
                    print(f"\nWorkers:")
                    for w in results["workers"]:
                        print(f"  {w['cli']}: {w['branch']}")
                        print(f"    Path: {w['path']}")
                        print(f"    Status: {w['status']}")
                else:
                    print("Failed to spawn tournament")

                if results["errors"]:
                    print("\nErrors:")
                    for err in results["errors"]:
                        print(f"  - {err}")

                sys.exit(0 if results["success"] else 1)

        elif args.command == "status":
            status = get_tournament_status(args.tournament)

            if args.json:
                print(json.dumps(status, indent=2))
            else:
                if "error" in status:
                    print(f"Error: {status['error']}")
                    sys.exit(1)

                if args.tournament:
                    t = status["tournament"]
                    print(f"Tournament: {t['id']}")
                    print(f"Task: {t['task']}")
                    print(f"Status: {t['status']}")
                    print(f"CLIs: {', '.join(t['clis'])}")
                    print(f"\nWorkers:")
                    for w in status["workers"]:
                        done_str = "DONE" if w["done"] else "pending"
                        print(f"  {w['cli']}: {done_str}")
                        print(f"    Branch: {w['branch']}")
                        print(f"    Path: {w['path']}")

                    c = status["completion"]
                    print(f"\nCompletion: {c['done']}/{c['total']}")
                    if c["complete"]:
                        print("Ready for review!")
                else:
                    tournaments = status.get("active_tournaments", [])
                    if not tournaments:
                        print("No active tournaments")
                    else:
                        print(f"Active tournaments: {len(tournaments)}")
                        for t in tournaments:
                            print(f"\n  {t['id']}")
                            print(f"    Task: {t['task']}")
                            print(f"    CLIs: {', '.join(t['clis'])}")
                            print(f"    Progress: {t['done_count']}/{t['worker_count']}")

        elif args.command == "list":
            tournaments = get_all_tournaments() if args.all else get_active_tournaments()

            if args.json:
                data = [
                    {
                        "id": t.id,
                        "task": t.task,
                        "status": t.status,
                        "clis": t.clis,
                        "started": t.started,
                        "worker_count": len(t.workers),
                        "done_count": sum(1 for w in t.workers if w.done)
                    }
                    for t in tournaments
                ]
                print(json.dumps(data, indent=2))
            else:
                if not tournaments:
                    print("No tournaments found")
                else:
                    print(f"{'ID':<30} {'STATUS':<12} {'TASK':<30} {'PROGRESS':<10}")
                    print("-" * 85)
                    for t in tournaments:
                        done = sum(1 for w in t.workers if w.done)
                        total = len(t.workers)
                        task_short = t.task[:27] + "..." if len(t.task) > 30 else t.task
                        print(f"{t.id:<30} {t.status:<12} {task_short:<30} {done}/{total}")

        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
