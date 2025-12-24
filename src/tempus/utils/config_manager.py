"""Configuration manager for persisting layer settings across sessions."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages persistent configuration for layer settings per CSV file.

    Stores settings in a JSON file in the project directory. Settings are
    keyed by the file path relative to the user's home directory.

    JSON Schema:
    {
        "relative/path/to/file.csv": {
            "layers": {
                "ColumnName": {
                    "color": "#FF0000",
                    "visible": true,
                    "line_width": 2
                },
                ...
            },
            "smoothing": 1
        },
        ...
    }
    """

    _instance: "ConfigManager | None" = None
    CONFIG_FILENAME = "tempus_settings.json"

    def __new__(cls) -> "ConfigManager":
        """Singleton pattern to ensure single config manager instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        self._initialized = True
        # Store config in the project directory (where this module is located)
        self._config_path = Path(__file__).parent.parent.parent.parent / self.CONFIG_FILENAME
        self._config: dict[str, Any] = {}
        self._load_config()

    @classmethod
    def instance(cls) -> "ConfigManager":
        """Get the singleton instance of ConfigManager."""
        return cls()

    def _load_config(self) -> None:
        """Load configuration from the settings file."""
        if not self._config_path.exists():
            self._config = {}
            return

        try:
            with open(self._config_path, encoding="utf-8") as f:
                self._config = json.load(f)
            logger.debug("Loaded config from %s", self._config_path)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Failed to load config file: %s", e)
            self._config = {}

    def _save_config(self) -> None:
        """Save configuration to the settings file."""
        try:
            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2)
            logger.debug("Saved config to %s", self._config_path)
        except OSError as e:
            logger.warning("Failed to save config file: %s", e)

    def _get_relative_key(self, filepath: str | Path) -> str:
        """Get the file key relative to the user's home directory.

        Args:
            filepath: Path to the CSV file

        Returns:
            Path string relative to home directory, or absolute path if not under home.
        """
        abs_path = Path(filepath).resolve()
        home = Path.home()
        try:
            return str(abs_path.relative_to(home))
        except ValueError:
            # File is not under home directory, use absolute path
            return str(abs_path)

    def get_file_config(self, filepath: str | Path) -> dict[str, Any] | None:
        """Get the stored configuration for a specific file.

        Args:
            filepath: Path to the CSV file

        Returns:
            Configuration dictionary with 'layers' and 'smoothing' keys,
            or None if no configuration exists for this file.
        """
        rel_path = self._get_relative_key(filepath)
        return self._config.get(rel_path)

    def save_file_config(self, filepath: str | Path, config_dict: dict[str, Any]) -> None:
        """Save configuration for a specific file.

        Args:
            filepath: Path to the CSV file
            config_dict: Configuration dictionary with 'layers' and 'smoothing' keys.
                        'layers' should contain layer configurations keyed by column name.
        """
        rel_path = self._get_relative_key(filepath)
        self._config[rel_path] = config_dict
        self._save_config()

    def get_layer_config(self, filepath: str | Path, column_name: str) -> dict[str, Any] | None:
        """Get configuration for a specific layer in a file.

        Args:
            filepath: Path to the CSV file
            column_name: Name of the column/layer

        Returns:
            Layer configuration dictionary with 'color', 'visible', 'line_width' keys,
            or None if no configuration exists.
        """
        file_config = self.get_file_config(filepath)
        if file_config is None:
            return None

        layers = file_config.get("layers", {})
        return layers.get(column_name)

    def remove_file_config(self, filepath: str | Path) -> None:
        """Remove stored configuration for a specific file.

        Args:
            filepath: Path to the CSV file
        """
        rel_path = self._get_relative_key(filepath)
        if rel_path in self._config:
            del self._config[rel_path]
            self._save_config()

    def clear_all(self) -> None:
        """Clear all stored configurations."""
        self._config = {}
        self._save_config()

    def has_config(self, filepath: str | Path) -> bool:
        """Check if configuration exists for a file.

        Args:
            filepath: Path to the CSV file

        Returns:
            True if configuration exists, False otherwise
        """
        rel_path = self._get_relative_key(filepath)
        return rel_path in self._config

    def reset_all(self) -> bool:
        """Reset all settings by deleting the configuration file.

        This removes the tempus_settings.json file completely and
        clears the in-memory configuration.

        Returns:
            True if the file was deleted successfully or didn't exist,
            False if deletion failed.
        """
        self._config = {}
        if self._config_path.exists():
            try:
                self._config_path.unlink()
                logger.info("Deleted config file: %s", self._config_path)
                return True
            except OSError as e:
                logger.error("Failed to delete config file: %s", e)
                return False
        return True

    @property
    def config_path(self) -> Path:
        """Get the path to the configuration file."""
        return self._config_path
