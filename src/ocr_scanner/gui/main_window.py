"""
Main window for OCR Scanner application.
"""

import logging
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget
from PyQt5.QtCore import Qt

from .single_image_tab import SingleImageTab
from .batch_processing_tab import BatchProcessingTab
from ..config.settings import DEFAULT_WINDOW_SIZE

logger = logging.getLogger(__name__)


class OCRScanner(QMainWindow):
    """Main application window with tabbed interface."""
    
    def __init__(self):
        super().__init__()
        self.roi_rect = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Advanced OCR Scanner with Batch Processing')
        self.setGeometry(100, 100, *DEFAULT_WINDOW_SIZE)
        
        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.single_tab = SingleImageTab(self)
        self.batch_tab = BatchProcessingTab(self)
        
        # Add tabs to widget
        self.tab_widget.addTab(self.single_tab, "Single Image")
        self.tab_widget.addTab(self.batch_tab, "Batch Processing")
        
        # Connect signals
        self.single_tab.roi_changed.connect(self.on_roi_changed)
        
        logger.info("Main window initialized")
    
    def on_roi_changed(self, roi_rect):
        """Handle ROI change from single image tab."""
        self.roi_rect = roi_rect
        self.batch_tab.update_roi_checkbox(roi_rect)
        logger.debug(f"ROI updated: {roi_rect}")
    
    def get_roi_rect(self):
        """Get current ROI rectangle."""
        return self.roi_rect