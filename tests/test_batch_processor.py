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
        file_