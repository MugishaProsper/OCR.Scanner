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
        user_plugins_dir = get_app_data_dir() / "plugins"
        user_plugins_dir.mkdir(exist_ok=True)
        self.add_plugin_directory(user_plugins_dir)
        
    def add_plugin_directory(self, directory: Path) -> None:
        """
        Add a directory to search for plugins.
        
        Args:
            directory: Path to plugin directory
        """
        if directory.exists() and directory not in self.plugin_directories:
            self.plugin_directories.append(directory)
            logger.info(f"Added plugin directory: {directory}")
    
    def load_plugins(self) -> None:
        """Load all plugins from registered directories."""
        for directory in self.plugin_directories:
            self._load_plugins_from_directory(directory)
            
        logger.info(f"Loaded {len(self.plugins)} plugins")
    
    def _load_plugins_from_directory(self, directory: Path) -> None:
        """
        Load plugins from a specific directory.
        
        Args:
            directory: Directory to search for plugins
        """
        if not directory.exists():
            return
            
        for file_path in directory.glob("*.py"):
            if file_path.name.startswith("__"):
                continue
                
            try:
                self._load_plugin_from_file(file_path)
            except Exception as e:
                logger.error(f"Failed to load plugin {file_path}: {e}")
    
    def _load_plugin_from_file(self, file_path: Path) -> None:
        """
        Load a plugin from a Python file.
        
        Args:
            file_path: Path to plugin file
        """
        module_name = file_path.stem
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        
        if spec is None or spec.loader is None:
            logger.warning(f"Could not load spec for {file_path}")
            return
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find plugin classes in the module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            
            if (isinstance(attr, type) and 
                issubclass(attr, BasePreprocessingPlugin) and 
                attr != BasePreprocessingPlugin):
                
                plugin_name = attr.__name__
                self.plugins[plugin_name] = attr
                logger.info(f"Loaded plugin: {plugin_name}")
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePreprocessingPlugin]:
        """
        Get a plugin instance by name.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Plugin instance or None if not found
        """
        if plugin_name not in self.plugin_instances:
            if plugin_name in self.plugins:
                try:
                    self.plugin_instances[plugin_name] = self.plugins[plugin_name]()
                except Exception as e:
                    logger.error(f"Failed to instantiate plugin {plugin_name}: {e}")
                    return None
            else:
                return None
                
        return self.plugin_instances[plugin_name]
    
    def get_available_plugins(self) -> List[str]:
        """
        Get list of available plugin names.
        
        Returns:
            List of plugin names
        """
        return list(self.plugins.keys())
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, str]]:
        """
        Get information about a plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Plugin information dictionary or None
        """
        plugin = self.get_plugin(plugin_name)
        if plugin:
            return plugin.get_info()
        return None
    
    def reload_plugins(self) -> None:
        """Reload all plugins."""
        self.plugins.clear()
        self.plugin_instances.clear()
        self.load_plugins()


# Global plugin manager instance
plugin_manager = PluginManager()