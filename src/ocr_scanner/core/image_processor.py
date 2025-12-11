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
        elif method == 'Auto Rotate':
            return ImageProcessor._auto_rotate(img)
        elif method == 'Deskew':
            return ImageProcessor._deskew_image(img)
        elif method == 'Perspective Correction':
            return ImageProcessor._correct_perspective(img)
        else:
            return img
    
    @staticmethod
    def _auto_rotate(img: np.ndarray) -> np.ndarray:
        """Auto-rotate image based on text orientation."""
        try:
            # Convert to grayscale if needed
            if len(img.shape) == 3:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                gray = img.copy()
            
            # Use Tesseract to detect orientation
            import pytesseract
            osd = pytesseract.image_to_osd(gray, output_type=pytesseract.Output.DICT)
            angle = osd.get('rotate', 0)
            
            if angle != 0:
                # Rotate image
                (h, w) = img.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                logger.info(f"Auto-rotated image by {angle} degrees")
                return rotated
            
            return img
        except Exception as e:
            logger.warning(f"Auto-rotation failed: {e}")
            return img
    
    @staticmethod
    def _deskew_image(img: np.ndarray) -> np.ndarray:
        """Deskew image using Hough line detection."""
        try:
            # Convert to grayscale if needed
            if len(img.shape) == 3:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                gray = img.copy()
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Hough line detection
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None:
                # Calculate average angle
                angles = []
                for rho, theta in lines[:10]:  # Use first 10 lines
                    angle = theta * 180 / np.pi - 90
                    if abs(angle) < 45:  # Only consider reasonable angles
                        angles.append(angle)
                
                if angles:
                    avg_angle = np.mean(angles)
                    
                    # Rotate image
                    (h, w) = img.shape[:2]
                    center = (w // 2, h // 2)
                    M = cv2.getRotationMatrix2D(center, avg_angle, 1.0)
                    deskewed = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                    logger.info(f"Deskewed image by {avg_angle:.2f} degrees")
                    return deskewed
            
            return img
        except Exception as e:
            logger.warning(f"Deskewing failed: {e}")
            return img
    
    @staticmethod
    def _correct_perspective(img: np.ndarray) -> np.ndarray:
        """Correct perspective distortion using contour detection."""
        try:
            # Convert to grayscale if needed
            if len(img.shape) == 3:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                gray = img.copy()
            
            # Edge detection and morphology
            edges = cv2.Canny(gray, 50, 150)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Find the largest rectangular contour
            for contour in sorted(contours, key=cv2.contourArea, reverse=True)[:5]:
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                if len(approx) == 4:
                    # Found a quadrilateral
                    pts = approx.reshape(4, 2).astype(np.float32)
                    
                    # Order points: top-left, top-right, bottom-right, bottom-left
                    rect = np.zeros((4, 2), dtype=np.float32)
                    s = pts.sum(axis=1)
                    rect[0] = pts[np.argmin(s)]  # top-left
                    rect[2] = pts[np.argmax(s)]  # bottom-right
                    
                    diff = np.diff(pts, axis=1)
                    rect[1] = pts[np.argmin(diff)]  # top-right
                    rect[3] = pts[np.argmax(diff)]  # bottom-left
                    
                    # Calculate dimensions
                    width = max(
                        np.linalg.norm(rect[1] - rect[0]),
                        np.linalg.norm(rect[2] - rect[3])
                    )
                    height = max(
                        np.linalg.norm(rect[3] - rect[0]),
                        np.linalg.norm(rect[2] - rect[1])
                    )
                    
                    # Destination points
                    dst = np.array([
                        [0, 0],
                        [width - 1, 0],
                        [width - 1, height - 1],
                        [0, height - 1]
                    ], dtype=np.float32)
                    
                    # Perspective transform
                    M = cv2.getPerspectiveTransform(rect, dst)
                    corrected = cv2.warpPerspective(img, M, (int(width), int(height)))
                    logger.info("Applied perspective correction")
                    return corrected
            
            return img
        except Exception as e:
            logger.warning(f"Perspective correction failed: {e}")
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