"""
Tests for image processor functionality.
"""

import pytest
import numpy as np
from unittest.mock import patch

from ocr_scanner.core.image_processor import ImageProcessor


class TestImageProcessor:
    """Test cases for ImageProcessor class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.test_image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        self.test_gray_image = np.ones((100, 100), dtype=np.uint8) * 128
    
    def test_apply_preprocessing_none(self):
        """Test no preprocessing."""
        result = ImageProcessor.apply_preprocessing(self.test_image, "None")
        np.testing.assert_array_equal(result, self.test_image)
    
    def test_apply_preprocessing_grayscale(self):
        """Test grayscale preprocessing."""
        result = ImageProcessor.apply_preprocessing(self.test_image, "Grayscale")
        
        assert len(result.shape) == 2  # Should be grayscale
        assert result.shape == (100, 100)
    
    def test_apply_preprocessing_threshold(self):
        """Test threshold preprocessing."""
        result = ImageProcessor.apply_preprocessing(self.test_image, "Threshold", 127)
        
        assert len(result.shape) == 2  # Should be grayscale
        assert result.shape == (100, 100)
        # All values should be either 0 or 255
        assert np.all((result == 0) | (result == 255))
    
    def test_apply_preprocessing_adaptive_threshold(self):
        """Test adaptive threshold preprocessing."""
        result = ImageProcessor.apply_preprocessing(self.test_image, "Adaptive Threshold")
        
        assert len(result.shape) == 2  # Should be grayscale
        assert result.shape == (100, 100)
        # All values should be either 0 or 255
        assert np.all((result == 0) | (result == 255))
    
    def test_apply_roi_valid(self):
        """Test ROI application with valid coordinates."""
        roi_rect = (10, 10, 50, 50)
        result = ImageProcessor.apply_roi(self.test_image, roi_rect)
        
        assert result.shape == (40, 40, 3)  # ROI size
    
    def test_apply_roi_invalid(self):
        """Test ROI application with invalid coordinates."""
        roi_rect = (50, 50, 10, 10)  # Invalid: x2 < x1, y2 < y1
        result = ImageProcessor.apply_roi(self.test_image, roi_rect)
        
        # Should return original image when ROI is invalid
        np.testing.assert_array_equal(result, self.test_image)
    
    def test_apply_roi_out_of_bounds(self):
        """Test ROI application with out-of-bounds coordinates."""
        roi_rect = (-10, -10, 150, 150)  # Extends beyond image
        result = ImageProcessor.apply_roi(self.test_image, roi_rect)
        
        # Should clamp to image bounds
        assert result.shape == (100, 100, 3)  # Full image size
    
    @patch('ocr_scanner.core.image_processor.pytesseract.image_to_string')
    def test_run_ocr_color_image(self, mock_ocr):
        """Test OCR on color image."""
        mock_ocr.return_value = "Test text"
        
        result = ImageProcessor.run_ocr(self.test_image)
        
        assert result == "Test text"
        mock_ocr.assert_called_once()
    
    @patch('ocr_scanner.core.image_processor.pytesseract.image_to_string')
    def test_run_ocr_grayscale_image(self, mock_ocr):
        """Test OCR on grayscale image."""
        mock_ocr.return_value = "Test text"
        
        result = ImageProcessor.run_ocr(self.test_gray_image)
        
        assert result == "Test text"
        mock_ocr.assert_called_once()
    
    @patch('ocr_scanner.core.image_processor.pytesseract.image_to_data')
    def test_get_text_boxes(self, mock_data):
        """Test text box detection."""
        mock_data.return_value = {
            'text': ['Hello', 'World'],
            'left': [10, 50],
            'top': [10, 10],
            'width': [30, 35],
            'height': [20, 20],
            'conf': [95, 90]
        }
        
        result = ImageProcessor.get_text_boxes(self.test_image)
        
        assert 'text' in result
        assert 'left' in result
        assert len(result['text']) == 2
        mock_data.assert_called_once()