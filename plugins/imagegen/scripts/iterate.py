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
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Add scripts directory to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from config import load_config, get_api_key, get_output_dir
from utils import (
    generate_filename, save_base64_image, print_result,
    validate_api_key, get_image_mime_type
)

# Session storage
SESSIONS_DIR = Path.home() / ".config" / "claude-imagegen" / "sessions"


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


def iterate_with_google(session: dict, prompt: str, output_path: Path) -> dict:
    """Perform iteration step with Google Gemini."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return {
            "success": False,
            "error": "google-genai package not installed. Run: pip install google-genai"
        }

    api_key = get_api_key("google")
    if not api_key:
        return {
            "success": False,
            "error": "GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set"
        }

    try:
        client = genai.Client(api_key=api_key)

        # Build conversation history for multi-turn
        contents = []

        # Add history (Gemini supports multi-turn image conversation)
        for entry in session["history"]:
            if entry["type"] == "initial" or entry["type"] == "iteration":
                # Add the image
                image_path = Path(entry["image"])
                if image_path.exists():
                    with open(image_path, "rb") as f:
                        image_data = f.read()
                    mime_type = get_image_mime_type(image_path)

                    contents.append(types.Part(
                        inline_data=types.Blob(
                            mime_type=mime_type,
                            data=image_data
                        )
                    ))

                # Add the prompt as user turn
                if entry.get("prompt"):
                    contents.append(entry["prompt"])

        # Add current prompt
        contents.append(prompt)

        # Configure for image output
        config = types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        )

        response = client.models.generate_content(
            model=session["model"],
            contents=contents,
            config=config
        )

        # Extract new image
        if not response.parts:
            return {
                "success": False,
                "error": "No parts in response from API"
            }

        for part in response.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                mime = getattr(part.inline_data, "mime_type", "image/png")
                ext = mime.split("/")[-1] if "/" in mime else "png"
                filepath = output_path.with_suffix(f".{ext}")

                with open(filepath, "wb") as f:
                    f.write(part.inline_data.data)

                # Update session
                session["history"].append({
                    "step": len(session["history"]),
                    "type": "iteration",
                    "image": str(filepath.resolve()),
                    "prompt": prompt,
                    "timestamp": datetime.now().isoformat()
                })
                save_session(session)

                return {
                    "success": True,
                    "file": str(filepath),
                    "session_id": session["id"],
                    "step": len(session["history"]) - 1,
                    "prompt": prompt
                }

        return {
            "success": False,
            "error": "No image returned from iteration"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def iterate_with_openai(session: dict, prompt: str, output_path: Path) -> dict:
    """Perform iteration step with OpenAI (edit-based)."""
    # OpenAI doesn't have true multi-turn, so we edit the last image
    try:
        from openai import OpenAI
    except ImportError:
        return {
            "success": False,
            "error": "openai package not installed. Run: pip install openai"
        }

    api_key = get_api_key("openai")
    if not api_key:
        return {
            "success": False,
            "error": "OPENAI_API_KEY environment variable not set"
        }

    try:
        client = OpenAI(api_key=api_key)

        # Get the last image from history
        last_entry = session["history"][-1]
        last_image = Path(last_entry["image"])

        if not last_image.exists():
            return {
                "success": False,
                "error": f"Previous image not found: {last_image}"
            }

        # Use edit endpoint
        with open(last_image, "rb") as image_file:
            response = client.images.edit(
                model=session["model"],
                image=image_file,
                prompt=prompt,
                n=1,
                size="1024x1024"
            )

        if response.data:
            image_data = response.data[0]

            if hasattr(image_data, "b64_json") and image_data.b64_json:
                save_base64_image(image_data.b64_json, output_path)
            elif hasattr(image_data, "url") and image_data.url:
                import urllib.request
                urllib.request.urlretrieve(image_data.url, output_path)

            # Update session
            session["history"].append({
                "step": len(session["history"]),
                "type": "iteration",
                "image": str(output_path.resolve()),
                "prompt": prompt,
                "timestamp": datetime.now().isoformat()
            })
            save_session(session)

            return {
                "success": True,
                "file": str(output_path),
                "session_id": session["id"],
                "step": len(session["history"]) - 1,
                "prompt": prompt
            }

        return {
            "success": False,
            "error": "No image returned from iteration"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


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

        provider = args.provider or config.get("default_provider", "google")
        provider_config = config.get(provider, {})
        model = args.model or provider_config.get("model")
        if not model:
            model = "gemini-2.5-flash-image" if provider == "google" else "gpt-image-1"

        session = create_session(image_path, args.prompt, provider, model)
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

    # Determine output path
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = get_output_dir()
        step = len(session["history"])
        filename = f"iter_{session['id']}_step{step}.png"
        output_path = output_dir / filename

    # Perform iteration
    if session["provider"] == "google":
        result = iterate_with_google(session, args.prompt, output_path)
    else:
        result = iterate_with_openai(session, args.prompt, output_path)

    # Output result
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["success"]:
            print_result(
                True,
                f"Iteration step {result['step']} complete",
                filepath=Path(result['file']),
                metadata={
                    "session_id": result["session_id"],
                    "step": result["step"],
                    "prompt": result["prompt"]
                }
            )
            print(f"\nContinue with: python iterate.py --session {result['session_id']} --prompt \"next instructions\"")
        else:
            print_result(False, result.get("error", "Unknown error"))
            sys.exit(1)


if __name__ == "__main__":
    main()
