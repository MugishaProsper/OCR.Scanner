"""
Base plugin class for custom preprocessing.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import numpy as np


class BasePreprocessingPlugin(ABC):
    """Base class for preprocessing plugins."""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.description = "Custom preprocessing plugin"
        self.version = "1.0.0"
        self.author = "Unknown"
        self.parameters = {}
        
    @abstractmethod
    def process(self, image: np.ndarray, **kwargs) -> np.ndarray:
        """
        Process the input image.
        
        Args:
            image: Input image as numpy array
            **kwargs: Additional parameters
            
        Returns:
            Processed image as numpy array
        """
        pass
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get plugin parameters for UI configuration.
        
        Returns:
            Dictionary of parameter definitions
        """
        pass
    
    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """
        Set plugin parameters.
        
        Args:
            parameters: Dictionary of parameter values
        """
        self.parameters.update(parameters)
    
    def get_info(self) -> Dict[str, str]:
        """
        Get plugin information.
        
        Returns:
            Dictionary with plugin metadata
        """
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author
        }
    
    def validate_image(self, image: np.ndarray) -> bool:
        """
        Validate input image.
        
        Args:
            image: Input image
            
        Returns:
            True if image is valid
        """
        if image is None:
            return False
        if not isinstance(image, np.ndarray):
            return False
        if len(image.shape) not in [2, 3]:
            return False
        return True