"""
Morphological operations plugin.
"""

import cv2
import numpy as np
from typing import Dict, Any

from ..base_plugin import BasePreprocessingPlugin


class MorphologicalOperationsPlugin(BasePreprocessingPlugin):
    """Plugin for morphological operations."""
    
    def __init__(self):
        super().__init__()
        self.name = "Morphological Operations"
        self.description = "Apply morphological operations to clean up text"
        self.version = "1.0.0"
        self.author = "OCR Scanner Team"
        
        # Default parameters
        self.parameters = {
            "operation": "opening",
            "kernel_size": 3,
            "kernel_shape": "rectangle",
            "iterations": 1
        }
    
    def process(self, image: np.ndarray, **kwargs) -> np.ndarray:
        """
        Apply morphological operations.
        
        Args:
            image: Input image
            **kwargs: Additional parameters
            
        Returns:
            Processed image
        """
        if not self.validate_image(image):
            return image
            
        # Update parameters from kwargs
        operation = kwargs.get("operation", self.parameters["operation"])
        kernel_size = kwargs.get("kernel_size", self.parameters["kernel_size"])
        kernel_shape = kwargs.get("kernel_shape", self.parameters["kernel_shape"])
        iterations = kwargs.get("iterations", self.parameters["iterations"])
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Create kernel
        if kernel_shape == "rectangle":
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        elif kernel_shape == "ellipse":
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        else:  # cross
            kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (kernel_size, kernel_size))
        
        # Apply morphological operation
        if operation == "opening":
            processed = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel, iterations=iterations)
        elif operation == "closing":
            processed = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel, iterations=iterations)
        elif operation == "erosion":
            processed = cv2.erode(gray, kernel, iterations=iterations)
        elif operation == "dilation":
            processed = cv2.dilate(gray, kernel, iterations=iterations)
        else:
            processed = gray
        
        # Convert back to color if original was color
        if len(image.shape) == 3:
            processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
            
        return processed
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get plugin parameters for UI configuration."""
        return {
            "operation": {
                "type": "choice",
                "choices": ["opening", "closing", "erosion", "dilation"],
                "default": "opening",
                "description": "Type of morphological operation"
            },
            "kernel_size": {
                "type": "int",
                "min": 1,
                "max": 15,
                "default": 3,
                "description": "Size of the morphological kernel"
            },
            "kernel_shape": {
                "type": "choice",
                "choices": ["rectangle", "ellipse", "cross"],
                "default": "rectangle",
                "description": "Shape of the morphological kernel"
            },
            "iterations": {
                "type": "int",
                "min": 1,
                "max": 10,
                "default": 1,
                "description": "Number of iterations to apply the operation"
            }
        }