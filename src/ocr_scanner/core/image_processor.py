"""
Image processing utilities for OCR Scanner.
"""

import logging
from typing import Tuple, Optional
import cv2
import numpy as np
import pytesseract
from PIL import Image

from ..config.settings import DEFAULT_OCR_CONFIG

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Handles image processing operations for OCR."""
    
    @staticmethod
    def apply_preprocessing(img: np.ndarray, method: str, threshold_value: int = 127) -> np.ndarray:
        """
        Apply preprocessing to image.
        
        Args:
            img: Input image
            method: Preprocessing method
            threshold_value: Threshold value for binary threshold
            
        Returns:
            Processed image
        """
        if method == 'Grayscale':
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        elif method == 'Threshold':
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, processed = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
            return processed
        elif method == 'Adaptive Threshold':
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, 11, 2)
        elif method == 'Denoise':
            return cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
        else:
            return img
    
    @staticmethod
    def apply_roi(img: np.ndarray, roi_rect: Tuple[int, int, int, int]) -> np.ndarray:
        """
        Apply ROI to image.
        
        Args:
            img: Input image
            roi_rect: ROI rectangle (x1, y1, x2, y2)
            
        Returns:
            Cropped image
        """
        x1, y1, x2, y2 = roi_rect
        h, w = img.shape[:2]
        
        # Ensure ROI is within image bounds
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        
        if x2 > x1 and y2 > y1:
            return img[y1:y2, x1:x2]
        else:
            logger.warning("Invalid ROI coordinates, using full image")
            return img
    
    @staticmethod
    def run_ocr(img: np.ndarray, language: str = "eng") -> str:
        """
        Run OCR on image.
        
        Args:
            img: Input image
            
        Returns:
            Extracted text
        """
        try:
            # Convert to PIL Image
            if len(img.shape) == 2:
                pil_image = Image.fromarray(img)
            else:
                rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_image)
            
            # Run OCR with configuration
            custom_config = f'--oem 3 --psm {DEFAULT_OCR_CONFIG["page_segmentation_mode"]}'
            text = pytesseract.image_to_string(pil_image, lang=language, config=custom_config)
            return text.strip()
            
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            raise
    
    @staticmethod
    def get_text_boxes(img: np.ndarray, confidence_threshold: int = None, language: str = "eng") -> dict:
        """
        Get text bounding boxes from image.
        
        Args:
            img: Input image
            confidence_threshold: Minimum confidence threshold
            
        Returns:
            Dictionary with text box data
        """
        if confidence_threshold is None:
            confidence_threshold = DEFAULT_OCR_CONFIG["confidence_threshold"]
            
        try:
            # Convert to PIL Image
            if len(img.shape) == 2:
                pil_image = Image.fromarray(img)
            else:
                rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_image)
            
            # Get bounding box data
            data = pytesseract.image_to_data(pil_image, lang=language, output_type=pytesseract.Output.DICT)
            return data
            
        except Exception as e:
            logger.error(f"Failed to get text boxes: {e}")
            raise