#!/usr/bin/env python3
"""
Main entry point for the OCR Scanner application.
"""

import sys
import logging
from PyQt5.QtWidgets import QApplication

from .gui.main_window import OCRScanner
from .config.settings import setup_logging


def main():
    """Main application entry point."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("OCR Scanner")
        app.setApplicationVersion("1.1.0")
        
        # Create and show main window
        scanner = OCRScanner()
        scanner.show()
        
        logger.info("OCR Scanner application started successfully")
        
        # Run application
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()