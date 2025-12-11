"""
Contrast enhancement plugin.
"""

import cv2
import numpy as np
from typing import Dict, Any

from ..base_plugin import BasePreprocessingPlugin


class ContrastEnhancementPlugin(BasePreprocessingPlugin):
    """Plugin for enhancing image contrast."""
    
    def __init__(self):
        super().__init__()
        self.name = "Contrast Enhancement"
        self.description = "Enhance image contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)"
        self.version = "1.0.0"
        self.author = "OCR Scanner Team"
        
        # Default parameters
        self.parameters = {
            "clip_limit": 2.0,
            "tile_grid_size": 8
        }
    
    def process(self, image: np.ndarray, **kwargs) -> np.ndarray:
        """
        Enhance image contrast using CLAHE.
        
        Args:
            image: Input image
            **kwargs: Additional parameters
            
        Returns:
            Contrast-enhanced image
        """
        if not self.validate_image(image):
            return image
            
        # Update parameters from kwargs
        clip_limit = kwargs.get("clip_limit", self.parameters["clip_limit"])
        tile_grid_size = kwargs.get("tile_grid_size", self.parameters["tile_grid_size"])
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply CLAHE
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_grid_size, tile_grid_size))
        enhanced = clahe.apply(gray)
        
        # Convert back to color if original was color
        if len(image.shape) == 3:
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
            
        return enhanced
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get plugin parameters for UI configuration."""
        return {
            "clip_limit": {
                "type": "float",
                "min": 0.1,
                "max": 10.0,
                "default": 2.0,
                "description": "Threshold for contrast limiting"
            },
            "tile_grid_size": {
                "type": "int",
                "min": 2,
                "max": 16,
                "default": 8,
                "description": "Size of the neighborhood area for histogram equalization"
            }
        }