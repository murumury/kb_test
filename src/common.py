"""Common utilities for loading configuration."""

from pathlib import Path
from typing import Any, Dict

import yaml


def load_config(path: str = "config/config.yaml") -> Dict[str, Any]:
    """Load YAML configuration file."""
    with open(Path(path), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

