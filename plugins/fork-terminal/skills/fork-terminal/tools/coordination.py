#!/usr/bin/env python3
"""Worker coordination for fork-terminal worktree sessions.

Tracks active workers across worktrees using a JSON file stored in .git/
"""

import fcntl
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional


@dataclass
class WorkerInfo:
    """Information about an active worker."""
    id: int
    path: str
    branch: str
    task: str
    started: str
    status: str = "active"
    pid: Optional[int] = None
    terminal: str = "unknown"


@dataclass
class TournamentWorker:
    """Information about a tournament worker."""
    worker_id: int
    cli: str  # "claude", "gemini", "codex"
    path: str
    branch: str
    done: bool = False
    done_file: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class TournamentInfo:
    """Information about a tournament."""
    id: str
    task: str
    started: str
    status: str  # "running", "reviewing", "complete"
    clis: List[str]
    workers: List[TournamentWorker]
    combined_branch: Optional[str] = None
    base: str = "HEAD"


def get_git_dir() -> str:
    """Get the .git directory for the current repository.

    Returns:
        Path to the .git directory.

    Raises:
        RuntimeError: If not in a git repository.
    """
    result = subprocess.run(
        ["git", "rev-parse", "--git-dir"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError("Not in a git repository")

    git_dir = result.stdout.strip()
    # Make absolute if relative
    if not os.path.isabs(git_dir):
        repo_root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True
        ).stdout.strip()
        git_dir = os.path.join(repo_root, git_dir)

    return git_dir


def get_coordination_file() -> str:
    """Get the path to the coordination file.

    Returns:
        Path to .git/.fork-terminal-workers.json
    """
    git_dir = get_git_dir()
    return os.path.join(git_dir, ".fork-terminal-workers.json")


def load_coordination() -> dict:
    """Load coordination data from file.

    Returns:
        Coordination data dictionary.
    """
    coord_file = get_coordination_file()
    if not os.path.exists(coord_file):
        return {
            "version": 1,
            "main_repo": get_git_dir().replace("/.git", ""),
            "workers": []
        }

    with open(coord_file, "r") as f:
        return json.load(f)


def save_coordination(data: dict) -> None:
    """Save coordination data to file atomically with locking.

    Uses a temp file + rename to prevent corruption from concurrent writes.
    Uses file locking to prevent race conditions between workers.

    Args:
        data: Coordination data dictionary.
    """
    coord_file = get_coordination_file()
    coord_dir = os.path.dirname(coord_file)
    lock_file = coord_file + ".lock"

    # Ensure directory exists
    os.makedirs(coord_dir, exist_ok=True)

    # Use a lock file to prevent concurrent writes
    with open(lock_file, "w") as lock_f:
        fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX)
        try:
            # Write to temp file first, then atomically rename
            fd, temp_path = tempfile.mkstemp(dir=coord_dir, suffix=".tmp")
            try:
                with os.fdopen(fd, "w") as f:
                    json.dump(data, f, indent=2)
                os.rename(temp_path, coord_file)
            except Exception:
                # Clean up temp file on error
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise
        finally:
            fcntl.flock(lock_f.fileno(), fcntl.LOCK_UN)


def get_next_worker_id(data: dict) -> int:
    """Get the next available worker ID.

    Args:
        data: Coordination data.

    Returns:
        Next available worker ID.
    """
    if not data["workers"]:
        return 1
    return max(w["id"] for w in data["workers"]) + 1


def register_worker(
    path: str,
    branch: str,
    task: str,
    pid: Optional[int] = None,
    terminal: str = "unknown"
) -> int:
    """Register a new worker in the coordination file.

    Args:
        path: Worktree path.
        branch: Branch name.
        task: Task description.
        pid: Process ID of the terminal/session.
        terminal: Terminal type (tmux, window, etc.)

    Returns:
        Assigned worker ID.
    """
    data = load_coordination()

    worker_id = get_next_worker_id(data)
    worker = WorkerInfo(
        id=worker_id,
        path=path,
        branch=branch,
        task=task,
        started=datetime.now().isoformat(),
        status="active",
        pid=pid,
        terminal=terminal
    )

    data["workers"].append(asdict(worker))
    save_coordination(data)

    return worker_id


def unregister_worker(path: str = None, worker_id: int = None) -> bool:
    """Mark a worker as inactive.

    Args:
        path: Worktree path (optional).
        worker_id: Worker ID (optional).

    Returns:
        True if a worker was updated.
    """
    if path is None and worker_id is None:
        raise ValueError("Must specify either path or worker_id")

    data = load_coordination()
    updated = False

    for worker in data["workers"]:
        if (path and worker["path"] == path) or (worker_id and worker["id"] == worker_id):
            worker["status"] = "stopped"
            updated = True
            break

    if updated:
        save_coordination(data)

    return updated


def remove_worker(path: str = None, worker_id: int = None) -> bool:
    """Remove a worker from the coordination file entirely.

    Args:
        path: Worktree path (optional).
        worker_id: Worker ID (optional).

    Returns:
        True if a worker was removed.
    """
    if path is None and worker_id is None:
        raise ValueError("Must specify either path or worker_id")

    data = load_coordination()
    original_count = len(data["workers"])

    data["workers"] = [
        w for w in data["workers"]
        if not ((path and w["path"] == path) or (worker_id and w["id"] == worker_id))
    ]

    if len(data["workers"]) < original_count:
        save_coordination(data)
        return True

    return False


def list_active_workers() -> List[WorkerInfo]:
    """Get list of active workers.

    Returns:
        List of active WorkerInfo objects.
    """
    data = load_coordination()
    return [
        WorkerInfo(**w) for w in data["workers"]
        if w["status"] == "active"
    ]


def list_all_workers() -> List[WorkerInfo]:
    """Get list of all workers (active and stopped).

    Returns:
        List of all WorkerInfo objects.
    """
    data = load_coordination()
    return [WorkerInfo(**w) for w in data["workers"]]


def is_process_running(pid: int) -> bool:
    """Check if a process is still running.

    Args:
        pid: Process ID to check.

    Returns:
        True if process is running.
    """
    try:
        os.kill(pid, 0)
        return True
    except (OSError, TypeError):
        return False


def cleanup_stale_workers() -> int:
    """Remove workers whose processes are no longer running.

    Returns:
        Number of workers cleaned up.
    """
    data = load_coordination()
    cleaned = 0

    for worker in data["workers"]:
        if worker["status"] == "active" and worker.get("pid"):
            if not is_process_running(worker["pid"]):
                worker["status"] = "stopped"
                cleaned += 1

    if cleaned > 0:
        save_coordination(data)

    return cleaned


def get_worker_by_path(path: str) -> Optional[WorkerInfo]:
    """Get worker info by worktree path.

    Args:
        path: Worktree path.

    Returns:
        WorkerInfo if found, None otherwise.
    """
    data = load_coordination()
    for w in data["workers"]:
        if w["path"] == path:
            return WorkerInfo(**w)
    return None


# Tournament functions

def register_tournament(
    task: str,
    workers: List[dict],
    clis: List[str],
    base: str = "HEAD"
) -> str:
    """Register a new tournament.

    Args:
        task: Task description.
        workers: List of worker dicts with worker_id, cli, path, branch.
        clis: List of CLI types used.
        base: Base branch/commit.

    Returns:
        Tournament ID.
    """
    data = load_coordination()

    # Ensure tournaments list exists
    if "tournaments" not in data:
        data["tournaments"] = []

    # Generate tournament ID
    import time
    tournament_id = f"tournament-{int(time.time())}"

    # Create tournament workers
    tournament_workers = [
        {
            "worker_id": w["worker_id"],
            "cli": w["cli"],
            "path": w["path"],
            "branch": w["branch"],
            "done": False,
            "done_file": None,
            "completed_at": None
        }
        for w in workers
    ]

    tournament = {
        "id": tournament_id,
        "task": task,
        "started": datetime.now().isoformat(),
        "status": "running",
        "clis": clis,
        "workers": tournament_workers,
        "combined_branch": None,
        "base": base
    }

    data["tournaments"].append(tournament)
    save_coordination(data)

    return tournament_id


def get_tournament(tournament_id: str) -> Optional[TournamentInfo]:
    """Get tournament by ID.

    Args:
        tournament_id: Tournament ID.

    Returns:
        TournamentInfo if found, None otherwise.
    """
    data = load_coordination()
    tournaments = data.get("tournaments", [])

    for t in tournaments:
        if t["id"] == tournament_id:
            workers = [TournamentWorker(**w) for w in t["workers"]]
            return TournamentInfo(
                id=t["id"],
                task=t["task"],
                started=t["started"],
                status=t["status"],
                clis=t["clis"],
                workers=workers,
                combined_branch=t.get("combined_branch"),
                base=t.get("base", "HEAD")
            )
    return None


def get_active_tournaments() -> List[TournamentInfo]:
    """Get all active (running) tournaments.

    Returns:
        List of active TournamentInfo objects.
    """
    data = load_coordination()
    tournaments = data.get("tournaments", [])

    result = []
    for t in tournaments:
        if t["status"] in ("running", "reviewing"):
            workers = [TournamentWorker(**w) for w in t["workers"]]
            result.append(TournamentInfo(
                id=t["id"],
                task=t["task"],
                started=t["started"],
                status=t["status"],
                clis=t["clis"],
                workers=workers,
                combined_branch=t.get("combined_branch"),
                base=t.get("base", "HEAD")
            ))
    return result


def get_all_tournaments() -> List[TournamentInfo]:
    """Get all tournaments (active and complete).

    Returns:
        List of all TournamentInfo objects.
    """
    data = load_coordination()
    tournaments = data.get("tournaments", [])

    result = []
    for t in tournaments:
        workers = [TournamentWorker(**w) for w in t["workers"]]
        result.append(TournamentInfo(
            id=t["id"],
            task=t["task"],
            started=t["started"],
            status=t["status"],
            clis=t["clis"],
            workers=workers,
            combined_branch=t.get("combined_branch"),
            base=t.get("base", "HEAD")
        ))
    return result


def update_tournament(tournament_id: str, updates: dict) -> bool:
    """Update tournament fields.

    Args:
        tournament_id: Tournament ID.
        updates: Dictionary of fields to update.

    Returns:
        True if tournament was updated.
    """
    data = load_coordination()
    tournaments = data.get("tournaments", [])

    for t in tournaments:
        if t["id"] == tournament_id:
            for key, value in updates.items():
                if key in t:
                    t[key] = value
            save_coordination(data)
            return True
    return False


def mark_tournament_worker_done(
    tournament_id: str,
    worker_id: int,
    done_file: str
) -> bool:
    """Mark a tournament worker as done.

    Args:
        tournament_id: Tournament ID.
        worker_id: Worker ID within the tournament.
        done_file: Path to the DONE.md file.

    Returns:
        True if worker was marked done.
    """
    data = load_coordination()
    tournaments = data.get("tournaments", [])

    for t in tournaments:
        if t["id"] == tournament_id:
            for w in t["workers"]:
                if w["worker_id"] == worker_id:
                    w["done"] = True
                    w["done_file"] = done_file
                    w["completed_at"] = datetime.now().isoformat()
                    save_coordination(data)
                    return True
    return False


def check_tournament_completion(tournament_id: str) -> dict:
    """Check if all workers in a tournament are done.

    Args:
        tournament_id: Tournament ID.

    Returns:
        Dict with completion status:
        {
            "complete": bool,
            "total": int,
            "done": int,
            "pending": List[dict]
        }
    """
    tournament = get_tournament(tournament_id)
    if not tournament:
        return {"complete": False, "total": 0, "done": 0, "pending": []}

    done_count = sum(1 for w in tournament.workers if w.done)
    pending = [
        {"worker_id": w.worker_id, "cli": w.cli, "path": w.path}
        for w in tournament.workers if not w.done
    ]

    return {
        "complete": done_count == len(tournament.workers),
        "total": len(tournament.workers),
        "done": done_count,
        "pending": pending
    }


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Worker coordination manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # List command
    list_parser = subparsers.add_parser("list", help="List workers")
    list_parser.add_argument("--all", action="store_true", help="Include stopped workers")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Register command
    reg_parser = subparsers.add_parser("register", help="Register a worker")
    reg_parser.add_argument("--path", required=True, help="Worktree path")
    reg_parser.add_argument("--branch", required=True, help="Branch name")
    reg_parser.add_argument("--task", required=True, help="Task description")
    reg_parser.add_argument("--pid", type=int, help="Process ID")
    reg_parser.add_argument("--terminal", default="unknown", help="Terminal type")

    # Unregister command
    unreg_parser = subparsers.add_parser("unregister", help="Mark worker as stopped")
    unreg_parser.add_argument("--path", help="Worktree path")
    unreg_parser.add_argument("--id", type=int, help="Worker ID")

    # Remove command
    rm_parser = subparsers.add_parser("remove", help="Remove worker record")
    rm_parser.add_argument("--path", help="Worktree path")
    rm_parser.add_argument("--id", type=int, help="Worker ID")

    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up stale workers")

    args = parser.parse_args()

    try:
        if args.command == "list":
            workers = list_all_workers() if args.all else list_active_workers()
            if args.json:
                print(json.dumps([asdict(w) for w in workers], indent=2))
            else:
                print(f"{'ID':<4} {'STATUS':<10} {'BRANCH':<25} {'PATH':<40} {'TASK':<30}")
                print("-" * 110)
                for w in workers:
                    task_short = w.task[:27] + "..." if len(w.task) > 30 else w.task
                    path_short = "..." + w.path[-37:] if len(w.path) > 40 else w.path
                    print(f"{w.id:<4} {w.status:<10} {w.branch:<25} {path_short:<40} {task_short:<30}")

        elif args.command == "register":
            worker_id = register_worker(
                path=args.path,
                branch=args.branch,
                task=args.task,
                pid=args.pid,
                terminal=args.terminal
            )
            print(f"Registered worker {worker_id}")

        elif args.command == "unregister":
            if unregister_worker(path=args.path, worker_id=args.id):
                print("Worker marked as stopped")
            else:
                print("Worker not found")

        elif args.command == "remove":
            if remove_worker(path=args.path, worker_id=args.id):
                print("Worker removed")
            else:
                print("Worker not found")

        elif args.command == "cleanup":
            count = cleanup_stale_workers()
            print(f"Cleaned up {count} stale worker(s)")

        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
