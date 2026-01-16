#!/usr/bin/env python3
"""
Google Gemini image generation provider.
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from .base import ImageProvider, ProviderResult


class GoogleProvider(ImageProvider):
    """Google Gemini image generation provider."""

    @property
    def default_model(self) -> str:
        return "gemini-2.5-flash-image"

    def _get_api_key(self) -> Optional[str]:
        """Get Google API key from environment."""
        return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    def _get_client(self):
        """Get Google GenAI client."""
        try:
            from google import genai
            return genai.Client(api_key=self._get_api_key())
        except ImportError:
            raise ImportError(
                "google-genai package not installed. Run: pip install google-genai"
            )

    def validate_config(self) -> ProviderResult:
        """Validate Google API configuration."""
        if not self._get_api_key():
            return self._error(
                "GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set"
            )
        return ProviderResult(success=True, provider=self.name)

    def generate(
        self,
        prompt: str,
        output_path: Path,
        count: int = 1,
        aspect_ratio: str = "1:1",
        **kwargs
    ) -> ProviderResult:
        """Generate image(s) with Google Gemini.

        Args:
            prompt: Image prompt.
            output_path: Output file path.
            count: Number of images (max 4).
            aspect_ratio: Aspect ratio (e.g., "1:1", "16:9").

        Returns:
            ProviderResult with generated files.
        """
        validation = self.validate_config()
        if not validation.success:
            return validation

        try:
            from google.genai import types

            client = self._get_client()

            # Configure generation
            config = types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            )

            # Configure image-specific settings including count
            image_config_params = {}
            if aspect_ratio:
                image_config_params["aspect_ratio"] = aspect_ratio
            if count > 1:
                image_config_params["number_of_images"] = min(count, 4)  # Max 4 images

            if image_config_params:
                config.image_config = types.ImageConfig(**image_config_params)

            response = client.models.generate_content(
                model=self.model,
                contents=[prompt],
                config=config
            )

            # Extract and save images
            saved_files = []
            for i, part in enumerate(response.parts):
                if hasattr(part, "inline_data") and part.inline_data:
                    mime = getattr(part.inline_data, "mime_type", "image/png")

                    # Generate filename for multiple images
                    if count > 1 or i > 0:
                        filepath = output_path.parent / f"{output_path.stem}_{i+1}.{mime.split('/')[-1]}"
                    else:
                        filepath = output_path

                    actual_path = self._save_image_data(
                        part.inline_data.data,
                        filepath,
                        mime
                    )
                    saved_files.append(str(actual_path))

            if saved_files:
                return self._success(saved_files, prompt)
            else:
                return self._error("No images returned from API")

        except ImportError as e:
            return self._error(str(e))
        except OSError as e:
            return self._error(f"File I/O error: {e}")
        except Exception as e:
            return self._error(f"{type(e).__name__}: {e}")

    def edit(
        self,
        image_path: Path,
        prompt: str,
        output_path: Path,
        **kwargs
    ) -> ProviderResult:
        """Edit an image with Google Gemini.

        Gemini supports editing via multi-modal input (image + text prompt).

        Args:
            image_path: Source image path.
            prompt: Edit instructions.
            output_path: Output file path.

        Returns:
            ProviderResult with edited file.
        """
        validation = self.validate_config()
        if not validation.success:
            return validation

        if not image_path.exists():
            return self._error(f"Source image not found: {image_path}")

        try:
            from google.genai import types

            client = self._get_client()

            # Load source image
            with open(image_path, "rb") as f:
                image_data = f.read()

            # Detect mime type
            ext = image_path.suffix.lower()
            mime_types = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".webp": "image/webp",
                ".gif": "image/gif"
            }
            mime_type = mime_types.get(ext, "image/png")

            # Create image part
            image_part = types.Part(
                inline_data=types.Blob(
                    mime_type=mime_type,
                    data=image_data
                )
            )

            # Configure for image output
            config = types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            )

            # Send image + prompt
            response = client.models.generate_content(
                model=self.model,
                contents=[image_part, prompt],
                config=config
            )

            # Extract result
            for part in response.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    mime = getattr(part.inline_data, "mime_type", "image/png")
                    actual_path = self._save_image_data(
                        part.inline_data.data,
                        output_path,
                        mime
                    )
                    return self._success(
                        [str(actual_path)],
                        prompt,
                        original=str(image_path)
                    )

            return self._error("No edited image returned from API")

        except ImportError as e:
            return self._error(str(e))
        except OSError as e:
            return self._error(f"File I/O error: {e}")
        except Exception as e:
            return self._error(f"{type(e).__name__}: {e}")

    def supports_iteration(self) -> bool:
        """Google Gemini supports multi-turn iteration."""
        return True

    def iterate(
        self,
        session: dict,
        prompt: str,
        output_path: Path,
        **kwargs
    ) -> ProviderResult:
        """Perform iteration step with conversation history.

        Args:
            session: Session with history of images/prompts.
            prompt: New refinement instructions.
            output_path: Output path for new image.

        Returns:
            ProviderResult with new image.
        """
        validation = self.validate_config()
        if not validation.success:
            return validation

        try:
            from google.genai import types

            client = self._get_client()

            # Build conversation history
            contents = []

            for entry in session.get("history", []):
                if entry.get("image"):
                    image_path = Path(entry["image"])
                    if image_path.exists():
                        with open(image_path, "rb") as f:
                            image_data = f.read()

                        # Detect mime type
                        ext = image_path.suffix.lower()
                        mime_types = {
                            ".png": "image/png",
                            ".jpg": "image/jpeg",
                            ".jpeg": "image/jpeg",
                            ".webp": "image/webp",
                            ".gif": "image/gif"
                        }
                        mime_type = mime_types.get(ext, "image/png")

                        contents.append(types.Part(
                            inline_data=types.Blob(
                                mime_type=mime_type,
                                data=image_data
                            )
                        ))

                if entry.get("prompt"):
                    contents.append(entry["prompt"])

            # Add current prompt
            contents.append(prompt)

            # Configure for image output
            config = types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            )

            response = client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config
            )

            # Extract result
            for part in response.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    mime = getattr(part.inline_data, "mime_type", "image/png")
                    actual_path = self._save_image_data(
                        part.inline_data.data,
                        output_path,
                        mime
                    )
                    return self._success(
                        [str(actual_path)],
                        prompt,
                        session_id=session.get("id"),
                        step=len(session.get("history", [])) + 1
                    )

            return self._error("No image returned from iteration")

        except ImportError as e:
            return self._error(str(e))
        except OSError as e:
            return self._error(f"File I/O error: {e}")
        except Exception as e:
            return self._error(f"{type(e).__name__}: {e}")
