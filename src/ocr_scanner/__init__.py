"""
OCR Scanner - Advanced OCR application with batch processing capabilities.

This package provides a comprehensive GUI-based OCR scanner built with PyQt5 
and Tesseract that allows you to extract text from images and live camera feeds.
"""

__version__ = "1.1.0"
__author__ = "Mugisha Prosper"
__email__ = "nelsonprox92@gmail.com"

from .main import main
from .gui.main_window import OCRScanner
from .core.batch_processor import BatchProcessor

__all__ = ["main", "OCRScanner", "BatchProcessor"]