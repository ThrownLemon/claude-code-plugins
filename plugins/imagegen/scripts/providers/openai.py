#!/usr/bin/env python3
"""
OpenAI GPT-Image generation provider.
"""

import base64
import os
import sys
from pathlib import Path
from typing import Optional

# Add parent and shared directories for imports
SCRIPT_DIR = Path(__file__).parent.parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent.parent
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(REPO_ROOT))

from .base import ImageProvider, ProviderResult

# Import SSRF protection from shared (with fallback)
try:
    from shared.security import is_safe_url
except ImportError:
    # Fallback if shared not available - comprehensive private IP rejection
    def is_safe_url(url: str) -> bool:
        """URL validation fallback with comprehensive private IP rejection."""
        from urllib.parse import urlparse
        import ipaddress
        import socket
        try:
            parsed = urlparse(url)
            host = parsed.hostname
            if not host:
                return False

            # Block common dangerous hostnames
            dangerous_hosts = {
                'localhost', '127.0.0.1', '::1',
                '169.254.169.254',  # AWS metadata
                'metadata.google.internal',  # GCP metadata
                '100.100.100.200',  # Alibaba metadata
            }
            if host.lower() in dangerous_hosts:
                return False

            # Try to resolve and check if it's a private IP
            try:
                # Resolve hostname to IP
                ip_str = socket.gethostbyname(host)
                ip = ipaddress.ip_address(ip_str)

                # Reject private, loopback, link-local, and reserved IPs
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                    return False
            except (socket.gaierror, ValueError):
                # If we can't resolve, be cautious but allow (might be valid external host)
                pass

            # Only allow http and https schemes
            if parsed.scheme not in ('http', 'https'):
                return False

            return True
        except Exception:
            return False


class OpenAIProvider(ImageProvider):
    """OpenAI GPT-Image generation provider."""

    @property
    def default_model(self) -> str:
        return "gpt-image-1"

    def _get_api_key(self) -> Optional[str]:
        """Get OpenAI API key from environment."""
        return os.environ.get("OPENAI_API_KEY")

    def _get_client(self):
        """Get OpenAI client."""
        try:
            from openai import OpenAI
            return OpenAI(api_key=self._get_api_key())
        except ImportError:
            raise ImportError(
                "openai package not installed. Run: pip install openai"
            )

    def validate_config(self) -> ProviderResult:
        """Validate OpenAI API configuration."""
        if not self._get_api_key():
            return self._error("OPENAI_API_KEY environment variable not set")
        return ProviderResult(success=True, provider=self.name)

    def generate(
        self,
        prompt: str,
        output_path: Path,
        count: int = 1,
        size: str = "1024x1024",
        quality: str = "high",
        background: str = "auto",
        **kwargs
    ) -> ProviderResult:
        """Generate image(s) with OpenAI GPT-Image.

        Args:
            prompt: Image prompt.
            output_path: Output file path.
            count: Number of images (max 10).
            size: Image size (e.g., "1024x1024").
            quality: Quality level ("low", "medium", "high").
            background: Background type for GPT-Image.

        Returns:
            ProviderResult with generated files.
        """
        validation = self.validate_config()
        if not validation.success:
            return validation

        try:
            client = self._get_client()

            params = {
                "model": self.model,
                "prompt": prompt,
                "n": min(count, 10),
                "size": size,
            }

            # GPT-Image specific parameters
            if self.model.startswith("gpt-image"):
                params["quality"] = quality
                if background != "auto":
                    params["background"] = background

            response = client.images.generate(**params)

            # Save images
            saved_files = []
            for i, image_data in enumerate(response.data):
                # Generate filename for multiple images
                if count > 1:
                    filepath = output_path.parent / f"{output_path.stem}_{i+1}.png"
                else:
                    filepath = output_path

                filepath.parent.mkdir(parents=True, exist_ok=True)

                # Handle base64 response
                if hasattr(image_data, "b64_json") and image_data.b64_json:
                    self._save_base64(image_data.b64_json, filepath)
                    saved_files.append(str(filepath))

                # Handle URL response (DALL-E)
                elif hasattr(image_data, "url") and image_data.url:
                    if not is_safe_url(image_data.url):
                        return self._error(
                            f"Unsafe URL returned by API: {image_data.url}"
                        )
                    self._secure_download(image_data.url, filepath)
                    saved_files.append(str(filepath))

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
        mask_path: Optional[Path] = None,
        size: str = "1024x1024",
        **kwargs
    ) -> ProviderResult:
        """Edit an image with OpenAI.

        Args:
            image_path: Source image path.
            prompt: Edit instructions.
            output_path: Output file path.
            mask_path: Optional mask for inpainting.
            size: Output size.

        Returns:
            ProviderResult with edited file.
        """
        validation = self.validate_config()
        if not validation.success:
            return validation

        if not image_path.exists():
            return self._error(f"Source image not found: {image_path}")

        try:
            client = self._get_client()

            # Prepare edit parameters
            edit_params = {
                "model": self.model,
                "prompt": prompt,
                "n": 1,
                "size": size
            }

            with open(image_path, "rb") as image_file:
                edit_params["image"] = image_file

                # Include mask if provided for inpainting
                if mask_path and mask_path.exists():
                    with open(mask_path, "rb") as mask_file:
                        edit_params["mask"] = mask_file
                        response = client.images.edit(**edit_params)
                else:
                    response = client.images.edit(**edit_params)

            if response.data:
                image_data = response.data[0]
                output_path.parent.mkdir(parents=True, exist_ok=True)

                if hasattr(image_data, "b64_json") and image_data.b64_json:
                    self._save_base64(image_data.b64_json, output_path)
                elif hasattr(image_data, "url") and image_data.url:
                    if not is_safe_url(image_data.url):
                        return self._error(
                            f"Unsafe URL returned by API: {image_data.url}"
                        )
                    self._secure_download(image_data.url, output_path)
                else:
                    return self._error("No image data in API response")

                return self._success(
                    [str(output_path)],
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
        """OpenAI uses edit-based iteration (not true multi-turn)."""
        return False

    def iterate(
        self,
        session: dict,
        prompt: str,
        output_path: Path,
        **kwargs
    ) -> ProviderResult:
        """Perform edit-based iteration.

        OpenAI doesn't have true multi-turn, so we edit the last image.
        """
        history = session.get("history", [])
        if not history:
            return self._error("No images in session history")

        last_entry = history[-1]
        last_image = Path(last_entry.get("image", ""))

        if not last_image.exists():
            return self._error(f"Previous image not found: {last_image}")

        result = self.edit(last_image, prompt, output_path, **kwargs)

        if result.success:
            result.metadata["session_id"] = session.get("id")
            result.metadata["step"] = len(history) + 1

        return result

    def _save_base64(self, b64_data: str, filepath: Path) -> None:
        """Save base64-encoded image data to file.

        Args:
            b64_data: Base64 encoded image string.
            filepath: Target path.
        """
        # Remove data URI prefix if present
        if "," in b64_data:
            b64_data = b64_data.split(",", 1)[1]

        image_data = base64.b64decode(b64_data)
        with open(filepath, "wb") as f:
            f.write(image_data)

    def _secure_download(self, url: str, filepath: Path, timeout: int = 30, max_redirects: int = 5) -> None:
        """Securely download a file from URL with timeout and redirect validation.

        Args:
            url: URL to download from.
            filepath: Target file path.
            timeout: Request timeout in seconds.
            max_redirects: Maximum number of redirects to follow.

        Raises:
            ValueError: If URL becomes unsafe after redirect.
            urllib.error.URLError: On network errors.
            TimeoutError: If request times out.
        """
        import urllib.request
        import urllib.error

        class SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
            """Custom redirect handler that validates each redirect URL."""
            redirect_count = 0

            def redirect_request(self, req, fp, code, msg, headers, newurl):
                self.redirect_count += 1
                if self.redirect_count > max_redirects:
                    raise urllib.error.HTTPError(
                        req.full_url, code, f"Too many redirects (max {max_redirects})", headers, fp
                    )
                # Validate the redirect URL for SSRF
                if not is_safe_url(newurl):
                    raise ValueError(f"Redirect to unsafe URL blocked: {newurl}")
                return super().redirect_request(req, fp, code, msg, headers, newurl)

        # Build opener with custom redirect handler
        opener = urllib.request.build_opener(SafeRedirectHandler())

        # Create request with timeout
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'claude-code-plugins/1.0')

        filepath.parent.mkdir(parents=True, exist_ok=True)

        with opener.open(request, timeout=timeout) as response:
            with open(filepath, 'wb') as f:
                # Read in chunks to avoid memory issues with large files
                chunk_size = 8192
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
