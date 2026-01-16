#!/usr/bin/env python3
"""
Image iteration script - refine images through multiple generations.
Supports conversation-style iteration with Google Gemini.

Usage:
    python iterate.py --image PATH --prompt "Refinement instructions" [options]
    python iterate.py --session SESSION_ID --prompt "Next refinement"

Options:
    --image PATH               Starting image for new session
    --session ID               Continue existing session
    --prompt PROMPT            Refinement instructions
    --provider google|openai   Provider to use
    --output PATH              Output file path
    --history                  Show session history
"""

import argparse
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Add scripts directory to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from config import load_config, get_output_dir
from providers import get_provider
from utils import print_result, validate_api_key

# Session storage
SESSIONS_DIR = Path.home() / ".config" / "claude-imagegen" / "sessions"


def is_safe_output_path(output_path: Path) -> bool:
    """Validate output path to prevent directory traversal attacks."""
    try:
        resolved = output_path.resolve()
        # Don't allow writing to system directories
        dangerous_prefixes = ['/etc', '/usr', '/bin', '/sbin', '/var', '/root']
        for prefix in dangerous_prefixes:
            if str(resolved).startswith(prefix):
                return False
        return True
    except Exception:
        return False


def get_session_path(session_id: str) -> Path:
    """Get path to session file."""
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    return SESSIONS_DIR / f"{session_id}.json"


def create_session(image_path: Path, prompt: str, provider: str, model: str) -> dict:
    """Create a new iteration session."""
    session_id = str(uuid.uuid4())[:8]

    session = {
        "id": session_id,
        "created": datetime.now().isoformat(),
        "provider": provider,
        "model": model,
        "history": [
            {
                "step": 0,
                "type": "initial",
                "image": str(image_path.resolve()),
                "prompt": prompt,
                "timestamp": datetime.now().isoformat()
            }
        ]
    }

    # Save session
    session_path = get_session_path(session_id)
    with open(session_path, "w") as f:
        json.dump(session, f, indent=2)

    return session


def load_session(session_id: str) -> dict:
    """Load an existing session."""
    session_path = get_session_path(session_id)
    if not session_path.exists():
        return None

    with open(session_path, "r") as f:
        return json.load(f)


def save_session(session: dict) -> None:
    """Save session state."""
    session_path = get_session_path(session["id"])
    with open(session_path, "w") as f:
        json.dump(session, f, indent=2)


def list_sessions() -> list:
    """List all active sessions."""
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    sessions = []

    for session_file in SESSIONS_DIR.glob("*.json"):
        try:
            with open(session_file, "r") as f:
                session = json.load(f)
                sessions.append({
                    "id": session["id"],
                    "created": session["created"],
                    "provider": session["provider"],
                    "steps": len(session["history"])
                })
        except (json.JSONDecodeError, KeyError):
            continue

    return sorted(sessions, key=lambda x: x["created"], reverse=True)


def main():
    parser = argparse.ArgumentParser(description="Iterate on images with AI")
    parser.add_argument("--image", "-i", help="Starting image for new session")
    parser.add_argument("--session", "-s", help="Continue existing session")
    parser.add_argument("--prompt", "-p", help="Refinement instructions")
    parser.add_argument("--provider", choices=["google", "openai"],
                        help="Provider to use")
    parser.add_argument("--model", "-m", help="Model to use")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--list", action="store_true", help="List active sessions")
    parser.add_argument("--history", action="store_true", help="Show session history")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # List sessions
    if args.list:
        sessions = list_sessions()
        if args.json:
            print(json.dumps(sessions, indent=2))
        else:
            if sessions:
                print("Active iteration sessions:")
                for s in sessions:
                    print(f"  {s['id']} - {s['provider']} - {s['steps']} steps - {s['created']}")
            else:
                print("No active sessions")
        return

    # Show session history
    if args.history and args.session:
        session = load_session(args.session)
        if session:
            if args.json:
                print(json.dumps(session["history"], indent=2))
            else:
                print(f"Session {session['id']} history:")
                for entry in session["history"]:
                    print(f"  Step {entry['step']}: {entry['prompt'][:50]}...")
                    print(f"    Image: {entry['image']}")
        else:
            print(f"Session not found: {args.session}")
        return

    # Require prompt for iteration
    if not args.prompt:
        print("Error: --prompt is required for iteration")
        sys.exit(1)

    config = load_config()

    # Either continue session or start new one
    if args.session:
        session = load_session(args.session)
        if not session:
            error_msg = f"Session not found: {args.session}"
            if args.json:
                print(json.dumps({"success": False, "error": error_msg}))
            else:
                print_result(False, error_msg)
            sys.exit(1)
    elif args.image:
        image_path = Path(args.image)
        if not image_path.exists():
            error_msg = f"Image not found: {args.image}"
            if args.json:
                print(json.dumps({"success": False, "error": error_msg}))
            else:
                print_result(False, error_msg)
            sys.exit(1)

        provider_name = args.provider or config.get("default_provider", "google")
        provider_config = config.get(provider_name, {})
        model = args.model or provider_config.get("model")
        if not model:
            model = "gemini-2.5-flash-image" if provider_name == "google" else "gpt-image-1"

        session = create_session(image_path, args.prompt, provider_name, model)
        print(f"Created new session: {session['id']}")
    else:
        print("Error: Either --image (for new session) or --session (to continue) is required")
        sys.exit(1)

    # Validate API key
    valid, msg = validate_api_key(session["provider"])
    if not valid:
        if args.json:
            print(json.dumps({"success": False, "error": msg}))
        else:
            print_result(False, msg)
        sys.exit(1)

    # Get provider
    provider = get_provider(session["provider"], model=session["model"])

    # Check if provider supports native multi-turn iteration
    # If not (e.g., OpenAI), the provider's iterate() method will internally
    # fall back to edit-based iteration using the last image in the session.
    # No action needed here - the provider handles the fallback transparently.
    if not provider.supports_iteration():
        # Provider will use edit-based iteration internally (e.g., OpenAI edits last image)
        pass

    # Determine output path
    if args.output:
        output_path = Path(args.output)
        if not is_safe_output_path(output_path):
            error_msg = f"Unsafe output path: {args.output}"
            if args.json:
                print(json.dumps({"success": False, "error": error_msg}))
            else:
                print_result(False, error_msg)
            sys.exit(1)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = get_output_dir()
        step = len(session["history"])
        filename = f"iter_{session['id']}_step{step}.png"
        output_path = output_dir / filename

    # Perform iteration
    result = provider.iterate(session, args.prompt, output_path)

    # Update session on success
    if result.success:
        session["history"].append({
            "step": len(session["history"]),
            "type": "iteration",
            "image": result.files[0] if result.files else None,
            "prompt": args.prompt,
            "timestamp": datetime.now().isoformat()
        })
        save_session(session)

    # Output result
    if args.json:
        result_dict = result.to_dict()
        result_dict["session_id"] = session["id"]
        result_dict["step"] = len(session["history"]) - 1
        print(json.dumps(result_dict, indent=2))
    else:
        if result.success:
            print_result(
                True,
                f"Iteration step {len(session['history']) - 1} complete",
                filepath=Path(result.files[0]) if result.files else None,
                metadata={
                    "session_id": session["id"],
                    "step": len(session["history"]) - 1,
                    "prompt": args.prompt
                }
            )
            print(f"\nContinue with: python iterate.py --session {session['id']} --prompt \"next instructions\"")
        else:
            print_result(False, result.error or "Unknown error")
            sys.exit(1)


if __name__ == "__main__":
    main()
