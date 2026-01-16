#!/usr/bin/env python3
"""
Base class for image generation providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ProviderResult:
    """Result from a provider operation."""
    success: bool
    error: Optional[str] = None
    files: List[str] = field(default_factory=list)
    provider: Optional[str] = None
    model: Optional[str] = None
    prompt: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "success": self.success,
        }
        if self.error:
            result["error"] = self.error
        if self.files:
            result["files"] = self.files
            result["file"] = self.files[0]  # Convenience: first file
        if self.provider:
            result["provider"] = self.provider
        if self.model:
            result["model"] = self.model
        if self.prompt:
            result["prompt"] = self.prompt
        if self.metadata:
            result.update(self.metadata)
        return result


class ImageProvider(ABC):
    """Abstract base class for image generation providers."""

    def __init__(self, model: Optional[str] = None):
        """Initialize provider.

        Args:
            model: Model to use (default: provider-specific default).
        """
        self._model = model

    @property
    def name(self) -> str:
        """Provider name."""
        return self.__class__.__name__.replace("Provider", "").lower()

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Default model for this provider."""
        pass

    @property
    def model(self) -> str:
        """Current model being used."""
        return self._model or self.default_model

    @abstractmethod
    def validate_config(self) -> ProviderResult:
        """Validate provider configuration (API keys, etc).

        Returns:
            ProviderResult with success=True if valid, error message otherwise.
        """
        pass

    @abstractmethod
    def generate(
        self,
        prompt: str,
        output_path: Path,
        count: int = 1,
        **kwargs
    ) -> ProviderResult:
        """Generate image(s) from a text prompt.

        Args:
            prompt: Text prompt describing the image.
            output_path: Path to save the generated image.
            count: Number of images to generate.
            **kwargs: Provider-specific options.

        Returns:
            ProviderResult with generated file paths or error.
        """
        pass

    @abstractmethod
    def edit(
        self,
        image_path: Path,
        prompt: str,
        output_path: Path,
        **kwargs
    ) -> ProviderResult:
        """Edit an existing image based on a prompt.

        Args:
            image_path: Path to the source image.
            prompt: Text instructions for editing.
            output_path: Path to save the edited image.
            **kwargs: Provider-specific options.

        Returns:
            ProviderResult with edited file path or error.
        """
        pass

    def supports_iteration(self) -> bool:
        """Whether this provider supports multi-turn iteration.

        Returns:
            True if provider supports conversation-style iteration.
        """
        return False

    def iterate(
        self,
        session: dict,
        prompt: str,
        output_path: Path,
        **kwargs
    ) -> ProviderResult:
        """Perform an iteration step on an existing session.

        Only available if supports_iteration() returns True.

        Args:
            session: Session state dictionary.
            prompt: Refinement instructions.
            output_path: Path to save the new image.
            **kwargs: Provider-specific options.

        Returns:
            ProviderResult with new image path or error.

        Raises:
            NotImplementedError: If provider doesn't support iteration.
        """
        raise NotImplementedError(
            f"{self.name} provider doesn't support multi-turn iteration"
        )

    def _save_image_data(
        self,
        data: bytes,
        output_path: Path,
        mime_type: str = "image/png"
    ) -> Path:
        """Save binary image data to file.

        Args:
            data: Image bytes.
            output_path: Target path.
            mime_type: MIME type for extension detection.

        Returns:
            Actual path saved to (may differ if extension changed).
        """
        # Determine extension from mime type
        ext = mime_type.split("/")[-1] if "/" in mime_type else "png"
        filepath = output_path.with_suffix(f".{ext}")

        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "wb") as f:
            f.write(data)

        return filepath

    def _error(self, message: str) -> ProviderResult:
        """Create an error result.

        Args:
            message: Error message.

        Returns:
            ProviderResult with success=False.
        """
        return ProviderResult(
            success=False,
            error=message,
            provider=self.name,
            model=self.model
        )

    def _success(
        self,
        files: List[str],
        prompt: str = None,
        **metadata
    ) -> ProviderResult:
        """Create a success result.

        Args:
            files: List of generated file paths.
            prompt: The prompt used.
            **metadata: Additional metadata.

        Returns:
            ProviderResult with success=True.
        """
        return ProviderResult(
            success=True,
            files=files,
            provider=self.name,
            model=self.model,
            prompt=prompt,
            metadata=metadata
        )
