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
        
        left_panel.addStretch()
        
        # Right panel - Results table
        right_panel = QVBoxLayout()
        
        right_panel.addWidget(QLabel('Batch Processing Results:'))
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(['Filename', 'Status', 'Extracted Text'])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results_table.setAlternatingRowColors(True)
        right_panel.addWidget(self.results_table)
        
        # Add panels to main layout
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 2)
    
    def load_batch_images(self):
        """Load multiple images for batch processing."""
        file_names, _ = QFileDialog.getOpenFileNames(
            self, "Select Images for Batch Processing", "", IMAGE_FILTER)
        
        if file_names:
            self.file_list.clear()
            for file_name in file_names:
                self.file_list.addItem(os.path.basename(file_name))
            
            # Store full paths for processing
            self.batch_file_paths = file_names
            self.batch_process_btn.setEnabled(True)
            
            # Update ROI checkbox state
            if self.parent_window and self.parent_window.get_roi_rect():
                roi_rect = self.parent_window.get_roi_rect()
                self.update_roi_checkbox(roi_rect)
            
            logger.info(f"Loaded {len(file_names)} images for batch processing")
    
    def clear_batch_list(self):
        """Clear batch processing list."""
        self.file_list.clear()
        self.batch_file_paths = []
        self.batch_process_btn.setEnabled(False)
        self.use_roi_checkbox.setEnabled(False)
        self.results_table.setRowCount(0)
        self.batch_results = []
        self.batch_export_btn.setEnabled(False)
        logger.info("Batch list cleared")
    
    def start_batch_processing(self):
        """Start batch processing of selected images."""
        if not self.batch_file_paths:
            return
        
        # Get processing parameters
        preprocessing_method = self.batch_preprocess_combo.currentText()
        threshold_value = self.batch_threshold_slider.value()
        roi_rect = None
        
        if self.use_roi_checkbox.isChecked() and self.parent_window:
            roi_rect = self.parent_window.get_roi_rect()
        
        # Clear previous results
        self.results_table.setRowCount(0)
        self.batch_results = []
        self.progress_bar.setValue(0)
        
        # Disable controls
        self.batch_process_btn.setEnabled(False)
        self.batch_cancel_btn.setEnabled(True)
        self.batch_load_btn.setEnabled(False)
        self.batch_clear_btn.setEnabled(False)
        
        # Start batch processor thread
        self.batch_processor = BatchProcessor(
            self.batch_file_paths, preprocessing_method, threshold_value, roi_rect)
        self.batch_processor.progress_updated.connect(self.update_batch_progress)
        self.batch_processor.file_processed.connect(self.add_batch_result)
        self.batch_processor.finished_processing.connect(self.batch_processing_finished)
        self.batch_processor.start()
        
        logger.info(f"Started batch processing of {len(self.batch_file_paths)} files")
    
    def cancel_batch_processing(self):
        """Cancel batch processing."""
        if self.batch_processor:
            self.batch_processor.cancel()
            self.batch_processor.wait()
        self.batch_processing_finished()
        logger.info("Batch processing cancelled")
    
    def update_batch_progress(self, value):
        """Update progress bar."""
        self.progress_bar.setValue(value)
    
    def add_batch_result(self, filename, text, status):
        """Add result to results table."""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        # Add items to table
        self.results_table.setItem(row, 0, QTableWidgetItem(filename))
        self.results_table.setItem(row, 1, QTableWidgetItem(status))
        
        # Truncate text for display but store full text
        display_text = text[:100] + "..." if len(text) > 100 else text
        self.results_table.setItem(row, 2, QTableWidgetItem(display_text))
        
        # Store full result
        self.batch_results.append({
            'filename': filename,
            'text': text,
            'status': status,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # Auto-scroll to latest result
        self.results_table.scrollToBottom()
    
    def batch_processing_finished(self):
        """Handle batch processing completion."""
        # Re-enable controls
        self.batch_process_btn.setEnabled(True)
        self.batch_cancel_btn.setEnabled(False)
        self.batch_load_btn.setEnabled(True)
        self.batch_clear_btn.setEnabled(True)
        
        if self.batch_results:
            self.batch_export_btn.setEnabled(True)
        
        # Show completion message
        if self.batch_results:
            successful = len([r for r in self.batch_results if r['status'] == 'Success'])
            total = len(self.batch_results)
            
            QMessageBox.information(self, "Batch Processing Complete", 
                                  f"Processing completed!\n"
                                  f"Successfully processed: {successful}/{total} images")
            
            logger.info(f"Batch processing completed: {successful}/{total} successful")
    
    def export_batch_results(self):
        """Export batch processing results."""
        if not self.batch_results:
            return
        
        # Create filter string for supported formats
        filter_str = ";;".join(EXPORT_FORMATS.values())
        
        # Get export file path
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "Export Batch Results", 
            f"batch_ocr_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            filter_str)
        
        if not file_path:
            return
        
        try:
            # Determine export format from file extension or filter
            if file_path.endswith('.csv') or 'CSV' in selected_filter:
                ResultExporter.export_to_csv(self.batch_results, file_path)
            elif file_path.endswith('.json') or 'JSON' in selected_filter:
                ResultExporter.export_to_json(self.batch_results, file_path)
            else:
                ResultExporter.export_to_txt(self.batch_results, file_path)
            
            QMessageBox.information(self, "Export Complete", 
                                  f"Results exported successfully to:\n{file_path}")
            logger.info(f"Results exported to: {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", 
                               f"Failed to export results:\n{str(e)}")
            logger.error(f"Export failed: {e}")
    
    def update_roi_checkbox(self, roi_rect):
        """Update ROI checkbox based on current ROI."""
        if roi_rect:
            self.use_roi_checkbox.setEnabled(True)
            self.use_roi_checkbox.setText(f'Use ROI from Single Image Tab {roi_rect}')
        else:
            self.use_roi_checkbox.setEnabled(False)
            self.use_roi_checkbox.setText('Use ROI from Single Image Tab (No ROI set)')
            self.use_roi_checkbox.setChecked(False)