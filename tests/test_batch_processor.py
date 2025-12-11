"""
Tests for batch processor functionality.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
import numpy as np
import cv2

from ocr_scanner.core.batch_processor import BatchProcessor


class TestBatchProcessor:
    """Test cases for BatchProcessor class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a simple test image
        test_image = np.ones((100, 100, 3), dtype=np.uint8) * 255
        self.test_image_path = os.path.join(self.temp_dir, "test_image.png")
        cv2.imwrite(self.test_image_path, test_image)
        
    def test_initialization(self):
        """Test BatchProcessor initialization."""
        file_paths = [self.test_image_path]
        processor = BatchProcessor(file_paths, "None", 127)
        
        assert processor.file_paths == file_paths
        assert processor.preprocessing_method == "None"
        assert processor.threshold_value == 127
        assert processor.roi_rect is None
        assert not processor.is_cancelled
    
    def test_cancel(self):
        """Test cancellation functionality."""
        processor = BatchProcessor([self.test_image_path], "None", 127)
        processor.cancel()
        
        assert processor.is_cancelled
    
    @patch('ocr_scanner.core.batch_processor.pytesseract.image_to_string')
    def test_run_ocr(self, mock_ocr):
        """Test OCR processing."""
        mock_ocr.return_value = "Test text"
        
        processor = BatchProcessor([self.test_image_path], "None", 127)
        
        # Mock the signals
        processor.progress_updated = Mock()
        processor.file_processed = Mock()
        processor.finished_processing = Mock()
        
        processor.run()
        
        # Verify signals were emitted
        processor.progress_updated.emit.assert_called()
        processor.file_processed.emit.assert_called()
        processor.finished_processing.emit.assert_called()
    
    def test_apply_preprocessing_none(self):
        """Test no preprocessing."""
        processor = BatchProcessor([self.test_image_path], "None", 127)
        
        test_img = np.ones((100, 100, 3), dtype=np.uint8) * 128
        result = processor._apply_preprocessing(test_img)
        
        np.testing.assert_array_equal(result, test_img)
    
    def test_apply_preprocessing_grayscale(self):
        """Test grayscale preprocessing."""
        processor = BatchProcessor([self.test_image_path], "Grayscale", 127)
        
        test_img = np.ones((100, 100, 3), dtype=np.uint8) * 128
        result = processor._apply_preprocessing(test_img)
        
        assert len(result.shape) == 2  # Should be grayscale
        assert result.shape == (100, 100)
    
    def test_apply_roi(self):
        """Test ROI application."""
        processor = BatchProcessor([self.test_image_path], "None", 127, (10, 10, 50, 50))
        
        test_img = np.ones((100, 100, 3), dtype=np.uint8) * 128
        result = processor._apply_roi(test_img)
        
        assert result.shape == (40, 40, 3)  # ROI size
    
    def test_apply_roi_invalid(self):
        """Test ROI application with invalid coordinates."""
        processor = BatchProcessor([self.test_image_path], "None", 127, (50, 50, 10, 10))
        
        test_img = np.ones((100, 100, 3), dtype=np.uint8) * 128
        result = processor._apply_roi(test_img)
        
        # Should return original image when ROI is invalid
        np.testing.assert_array_equal(result, test_img)