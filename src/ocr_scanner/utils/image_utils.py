"""
Image utility functions for OCR Scanner.
"""

import logging
from typing import Tuple
import cv2
import numpy as np
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt

logger = logging.getLogger(__name__)


class ImageUtils:
    """Utility functions for image handling and display."""
    
    @staticmethod
    def cv2_to_qimage(cv_img: np.ndarray) -> QImage:
        """
        Convert OpenCV image to QImage.
        
        Args:
            cv_img: OpenCV image (BGR or grayscale)
            
        Returns:
            QImage object
        """
        if len(cv_img.shape) == 2:
            # Grayscale image
            height, width = cv_img.shape
            bytes_per_line = width
            return QImage(cv_img.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        else:
            # Color image
            height, width, channel = cv_img.shape
            bytes_per_line = 3 * width
            rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            return QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
    
    @staticmethod
    def create_scaled_pixmap(cv_img: np.ndarray, target_size: Tuple[int, int]) -> QPixmap:
        """
        Create scaled pixmap from OpenCV image.
        
        Args:
            cv_img: OpenCV image
            target_size: Target size (width, height)
            
        Returns:
            Scaled QPixmap
        """
        q_img = ImageUtils.cv2_to_qimage(cv_img)
        pixmap = QPixmap.fromImage(q_img)
        return pixmap.scaled(target_size[0], target_size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation)
    
    @staticmethod
    def calculate_display_scale(img_size: Tuple[int, int], display_size: Tuple[int, int]) -> float:
        """
        Calculate scale factor for displaying image in widget.
        
        Args:
            img_size: Original image size (width, height)
            display_size: Display widget size (width, height)
            
        Returns:
            Scale factor
        """
        img_width, img_height = img_size
        display_width, display_height = display_size
        
        return min(display_width / img_width, display_height / img_height)
    
    @staticmethod
    def screen_to_image_coords(screen_pos: Tuple[int, int], img_size: Tuple[int, int], 
                              display_size: Tuple[int, int]) -> Tuple[int, int]:
        """
        Convert screen coordinates to image coordinates.
        
        Args:
            screen_pos: Screen position (x, y)
            img_size: Original image size (width, height)
            display_size: Display widget size (width, height)
            
        Returns:
            Image coordinates (x, y)
        """
        screen_x, screen_y = screen_pos
        img_width, img_height = img_size
        display_width, display_height = display_size
        
        scale = ImageUtils.calculate_display_scale(img_size, display_size)
        scaled_width = int(img_width * scale)
        scaled_height = int(img_height * scale)
        
        offset_x = (display_width - scaled_width) // 2
        offset_y = (display_height - scaled_height) // 2
        
        img_x = max(0, min(img_width, int((screen_x - offset_x) / scale)))
        img_y = max(0, min(img_height, int((screen_y - offset_y) / scale)))
        
        return img_x, img_y
    
    @staticmethod
    def validate_image_file(file_path: str) -> bool:
        """
        Validate if file is a supported image format.
        
        Args:
            file_path: Path to image file
            
        Returns:
            True if valid image file
        """
        try:
            img = cv2.imread(file_path)
            return img is not None
        except Exception as e:
            logger.warning(f"Invalid image file {file_path}: {e}")
            return False