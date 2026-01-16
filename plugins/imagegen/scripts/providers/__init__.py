"""
Image generation providers for imagegen plugin.

Provides a unified interface for generating images with different
AI providers (Google Gemini, OpenAI GPT-Image).

Usage:
    from providers import get_provider

    provider = get_provider("google")
    result = provider.generate("A sunset over mountains", output_path=Path("image.png"))
"""

from .base import ImageProvider, ProviderResult
from .google import GoogleProvider
from .openai import OpenAIProvider

# Provider registry
_PROVIDERS = {
    "google": GoogleProvider,
    "openai": OpenAIProvider,
}


def get_provider(name: str, **kwargs) -> ImageProvider:
    """Get a provider instance by name.

    Args:
        name: Provider name ("google" or "openai").
        **kwargs: Additional arguments passed to provider constructor.

    Returns:
        Provider instance.

    Raises:
        ValueError: If provider name is unknown.
    """
    provider_class = _PROVIDERS.get(name.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider: {name}. Supported: {list(_PROVIDERS.keys())}")
    return provider_class(**kwargs)


def list_providers() -> list:
    """Get list of available provider names."""
    return list(_PROVIDERS.keys())


__all__ = [
    "ImageProvider",
    "ProviderResult",
    "GoogleProvider",
    "OpenAIProvider",
    "get_provider",
    "list_providers",
]
