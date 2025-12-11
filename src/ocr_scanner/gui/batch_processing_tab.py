"""
Batch processing tab for OCR Scanner.
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Any
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QFileDialog, QComboBox, QSlider, QGroupBox,
                             QProgressBar, QListWidget, QCheckBox, QMessageBox,
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QAbstractItemView)
from PyQt5.QtCore import Qt

from ..core.batch_processor import BatchProcessor
from ..utils.export import ResultExporter
from ..config.settings import IMAGE_FILTER, PREPROCESSING_OPTIONS, EXPORT_FORMATS

logger = logging.getLogger(__name__)


class BatchProcessingTab(QWidget):
    """Tab for batch processing multiple images."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.batch_processor = None
        self.batch_results = []
        self.batch_file_paths = []
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QHBoxLayout(self)
        
        # Left panel - Batch controls
        left_panel = QVBoxLayout()
        
        # File selection group
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout()
        
        self.batch_load_btn = QPushButton('Select Images')
        self.batch_load_btn.clicked.connect(self.load_batch_images)
        file_layout.addWidget(self.batch_load_btn)
        
        self.batch_clear_btn = QPushButton('Clear List')
        self.batch_clear_btn.clicked.connect(self.clear_batch_list)
        file_layout.addWidget(self.batch_clear_btn)
        
        file_layout.addWidget(QLabel('Selected Files:'))
        self.file_list = QListWidget()
        self.file_list.setMaximumHeight(150)
        file_layout.addWidget(self.file_list)
        
        file_group.setLayout(file_layout)
        left_panel.addWidget(file_group)
        
        # Batch preprocessing group
        batch_preprocess_group = QGroupBox("Batch Preprocessing")
        batch_preprocess_layout = QVBoxLayout()
        
        self.batch_preprocess_combo = QComboBox()
        self.batch_preprocess_combo.addItems(PREPROCESSING_OPTIONS)
        batch_preprocess_layout.addWidget(QLabel('Method:'))
        batch_preprocess_layout.addWidget(self.batch_preprocess_combo)
        
        self.batch_threshold_slider = QSlider(Qt.Horizontal)
        self.batch_threshold_slider.setMinimum(0)
        self.batch_threshold_slider.setMaximum(255)
        self.batch_threshold_slider.setValue(127)
        batch_preprocess_layout.addWidget(QLabel('Threshold:'))
        batch_preprocess_layout.addWidget(self.batch_threshold_slider)
        self.batch_threshold_label = QLabel('127')
        batch_preprocess_layout.addWidget(self.batch_threshold_label)
        self.batch_threshold_slider.valueChanged.connect(
            lambda v: self.batch_threshold_label.setText(str(v)))
        
        self.use_roi_checkbox = QCheckBox('Use ROI from Single Image Tab')
        self.use_roi_checkbox.setEnabled(False)
        batch_preprocess_layout.addWidget(self.use_roi_checkbox)
        
        batch_preprocess_group.setLayout(batch_preprocess_layout)
        left_panel.addWidget(batch_preprocess_group)
        
        # Batch processing group
        batch_process_group = QGroupBox("Processing")
        batch_process_layout = QVBoxLayout()
        
        self.batch_process_btn = QPushButton('Start Batch OCR')
        self.batch_process_btn.clicked.connect(self.start_batch_processing)
        self.batch_process_btn.setEnabled(False)
        batch_process_layout.addWidget(self.batch_process_btn)
        
        self.batch_cancel_btn = QPushButton('Cancel Processing')
        self.batch_cancel_btn.clicked.connect(self.cancel_batch_processing)
        self.batch_cancel_btn.setEnabled(False)
        batch_process_layout.addWidget(self.batch_cancel_btn)
        
        self.progress_bar = QProgressBar()
        batch_process_layout.addWidget(self.progress_bar)
        
        self.batch_export_btn = QPushButton('Export Results')
        self.batch_export_btn.clicked.connect(self.export_batch_results)
        self.batch_export_btn.setEnabled(False)
        batch_process_layout.addWidget(self.batch_export_btn)
        
        batch_process_group.setLayout(batch_process_layout)
        left_panel.addWidget(batch_process_group)
        
     