"""
Plugin manager for loading and managing preprocessing plugins.
"""

import os
import sys
import importlib.util
import logging
from typing import Dict, List, Type, Optional
from pathlib import Path

from .base_plugin import BasePreprocessingPlugin

logger = logging.getLogger(__name__)


class PluginManager:
    """Manages preprocessing plugins."""
    
    def __init__(self):
        self.plugins: Dict[str, Type[BasePreprocessingPlugin]] = {}
        self.plugin_instances: Dict[str, BasePreprocessingPlugin] = {}
        self.plugin_directories = []
        
        # Add default plugin directories
        self.add_plugin_directory(Path(__file__).parent / "builtin")
        
        # Add user plugin directory
        from ..config.settings import get_app_data_dir
        user_plugin