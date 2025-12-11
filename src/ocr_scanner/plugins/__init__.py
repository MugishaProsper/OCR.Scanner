"""Plugin system for OCR Scanner."""

from .base_plugin import BasePreprocessingPlugin
from .plugin_manager import PluginManager

__all__ = ["BasePreprocessingPlugin", "PluginManager"]