"""
Batch processing functionality for OCR Scanner.
"""

import os
import logging
from typing import List, Optional, Tuple
import cv2
import numpy as np
import pytesseract
from PyQt5.QtCore import QThread, pyqtSignal
from PIL import Image

from ..config.settings import DEFAULT_OCR_CONFIG

logger = logging.getLogger(__name__)


class BatchProcessor(QThread):
    """
    Thread-based batch processor for OCR operations.
    
    Signals:
        progress_updated: Emitted when progress changes (int: percentage)
        file_processed: Emitted when a file is processed (str: filename, str: text, str: status)
        finished_processing: Emitted when all processing is complete
    """
    
    progress_updated = pyqtSignal(int)
    file_processed = pyqtSignal(str, str, str)  # filename, text, status
    finished_processing = pyqtSignal()
    
    def __init__(self, file_paths: List[str], preprocessing_method: str, 
                 threshold_value: int, roi_rect: Optional[Tuple[int, int, int, int]] = None,
                 language: str = "eng"):
        """
        Initialize batch processor.
        
        Args:
            file_paths: List of image file paths to process
            preprocessing_method: Preprocessing method to apply
            threshold_value: Threshold value for binary threshold
            roi_rect: Optional ROI rectangle (x1, y1, x2, y2)
        """
        super().__init__()
        self.file_paths = file_paths
        self.preprocessing_method = preprocessing_method
        self.threshold_value = threshold_value
        self.roi_rect = roi_rect
        self.language = language
        self.is_cancelled = False
        
        logger.info(f"Initialized batch processor for {len(file_paths)} files")
        
    def cancel(self) -> None:
        """Cancel the batch processing operation."""
        self.is_cancelled = True
        logger.info("Batch processing cancelled by user")
        
    def run(self) -> None:
        """Main processing loop."""
        total_files = len(self.file_paths)
        logger.info(f"Starting batch processing of {total_files} files")
        
        for i, file_path in enumerate(self.file_paths):
            if self.is_cancelled:
                logger.info("Processing cancelled")
                break
                
            try:
                filename = os.path.basename(file_path)
                logger.debug(f"Processing file: {filename}")
                
                # Load and process image
                image = cv2.imread(file_path)
                if image is None:
                    error_msg = "Could not load image"
                    logger.warning(f"Failed to load {filename}: {error_msg}")
                    self.file_processed.emit(filename, "", f"Error: {error_msg}")
                    continue
                
                # Apply preprocessing
                processed_image = self._apply_preprocessing(image)
                
                # Apply ROI if specified
                if self.roi_rect:
                    processed_image = self._apply_roi(processed_image)
                
                # Run OCR
                text, status = self._run_ocr(processed_image)
                
                logger.debug(f"Processed {filename}: {status}")
                self.file_processed.emit(filename, text, status)
                
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                logger.error(f"Failed to process {filename}: {error_msg}")
                self.file_processed.emit(os.path.basename(file_path), "", error_msg)
            
            # Update progress
            progress = int((i + 1) / total_files * 100)
            self.progress_updated.emit(progress)
        
        logger.info("Batch processing completed")
        self.finished_processing.emit()
    
    def _apply_preprocessing(self, img: np.ndarray) -> np.ndarray:
        """Apply preprocessing to image."""
        if self.preprocessing_method == 'Grayscale':
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        elif self.preprocessing_method == 'Threshold':
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, processed = cv2.threshold(gray, self.threshold_value, 255, cv2.THRESH_BINARY)
            return processed
        elif self.preprocessing_method == 'Adaptive Threshold':
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, 11, 2)
        elif self.preprocessing_method == 'Denoise':
            return cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
        else:
            return img
    
    def _apply_roi(self, img: np.ndarray) -> np.ndarray:
        """Apply ROI to image."""
        if not self.roi_rect:
            return img
            
        x1, y1, x2, y2 = self.roi_rect
        h, w = img.shape[:2]
        
        # Ensure ROI is within image bounds
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        
        if x2 > x1 and y2 > y1:
            return img[y1:y2, x1:x2]
        else:
            logger.warning("Invalid ROI coordinates, using full image")
            return img
    
    def _run_ocr(self, img: np.ndarray) -> Tuple[str, str]:
        """Run OCR on processed image."""
        try:
            # Convert to PIL Image
            if len(img.shape) == 2:
                pil_image = Image.fromarray(img)
            else:
                rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_image)
            
            # Run OCR with configuration
            custom_config = f'--oem 3 --psm {DEFAULT_OCR_CONFIG["page_segmentation_mode"]}'
            text = pytesseract.image_to_string(pil_image, lang=self.language, config=custom_config).strip()
            
            status = "Success" if text else "No text detected"
            return text, status
            
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return "", f"OCR Error: {str(e)}"