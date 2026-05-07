"""Configuration management for Tracify application."""

from pathlib import Path
from typing import Any

try:
    import tomli as tomllib  # Python < 3.11
except ImportError:
    import tomllib  # Python >= 3.11

import tomli_w


class Config:
    """Application configuration manager."""

    DEFAULT_CONFIG = {
        "defaults": {
            "output_format": "png",
            "max_image_size": 4096,
            "output_directory": "",
        },
        "effects": {
            "sketch": {"blur_kernel": 21, "scale": 256},
            "contour": {"threshold1": 50, "threshold2": 150},
            "tattoo": {"threshold_type": "otsu"},
        },
        "export": {
            "jpeg_quality": 95,
            "png_compression": 6,
        },
    }

    def __init__(self, config_path: Path | None = None) -> None:
        """Initialize configuration manager.

        Args:
            config_path: Path to config file. If None, uses default location.
        """
        if config_path is None:
            config_dir = Path.home() / ".tracify"
            config_dir.mkdir(exist_ok=True)
            config_path = config_dir / "config.toml"

        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from file or use defaults.

        Returns:
            Configuration dictionary.
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, "rb") as f:
                    return tomllib.load(f)
            except Exception:
                # If config is corrupted, use defaults
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()

    def save(self) -> None:
        """Save current configuration to file."""
        with open(self.config_path, "wb") as f:
            tomli_w.dump(self.config, f)

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            section: Configuration section (e.g., 'effects', 'defaults').
            key: Configuration key.
            default: Default value if not found.

        Returns:
            Configuration value or default.
        """
        return self.config.get(section, {}).get(key, default)

    def set(self, section: str, key: str, value: Any) -> None:
        """Set configuration value.

        Args:
            section: Configuration section.
            key: Configuration key.
            value: Value to set.
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value

    def get_effect_params(self, effect: str) -> dict[str, Any]:
        """Get parameters for specific effect.

        Args:
            effect: Effect name ('sketch', 'contour', 'tattoo').

        Returns:
            Dictionary of effect parameters.
        """
        return self.config.get("effects", {}).get(effect, {})

    def set_effect_params(self, effect: str, params: dict[str, Any]) -> None:
        """Set parameters for specific effect.

        Args:
            effect: Effect name.
            params: Dictionary of parameters to set.
        """
        if "effects" not in self.config:
            self.config["effects"] = {}
        if effect not in self.config["effects"]:
            self.config["effects"][effect] = {}
        self.config["effects"][effect].update(params)
