import sys
import os
import cv2
import numpy as np
import pytesseract
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                             QFileDialog, QComboBox, QSlider, QGroupBox,
                             QProgressBar, QListWidget, QCheckBox, QMessageBox,
                             QTabWidget, QTableWidget, QTableWidgetItem,
                             QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt, QTimer, QRect, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
from PIL import Image

class BatchProcessor(QThread):
    progress_updated = pyqtSignal(int)
    file_processed = pyqtSignal(str, str, str)  # filename, text, status
    finished_processing = pyqtSignal()
    
    def __init__(self, file_paths, preprocessing_method, threshold_value, roi_rect=None):
        super().__init__()
        self.file_paths = file_paths
        self.preprocessing_method = preprocessing_method
        self.threshold_value = threshold_value
        self.roi_rect = roi_rect
        self.is_cancelled = False
        
    def cancel(self):
        self.is_cancelled = True
        
    def run(self):
        total_files = len(self.file_paths)
        
        for i, file_path in enumerate(self.file_paths):
            if self.is_cancelled:
                break
                
            try:
                # Load and process image
                image = cv2.imread(file_path)
                if image is None:
                    self.file_processed.emit(os.path.basename(file_path), "", "Error: Could not load image")
                    continue
                
                # Apply preprocessing
                processed_image = self.apply_preprocessing(image)
                
                # Apply ROI if specified
                if self.roi_rect:
                    x1, y1, x2, y2 = self.roi_rect
                    h, w = processed_image.shape[:2]
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(w, x2), min(h, y2)
                    if x2 > x1 and y2 > y1:
                        processed_image = processed_image[y1:y2, x1:x2]
                
                # Convert to PIL and run OCR
                if len(processed_image.shape) == 2:
                    pil_image = Image.fromarray(processed_image)
                else:
                    rgb_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(rgb_image)
                
                text = pytesseract.image_to_string(pil_image).strip()
                status = "Success" if text else "No text detected"
                
                self.file_processed.emit(os.path.basename(file_path), text, status)
                
            except Exception as e:
                self.file_processed.emit(os.path.basename(file_path), "", f"Error: {str(e)}")
            
            # Update progress
            progress = int((i + 1) / total_files * 100)
            self.progress_updated.emit(progress)
        
        self.finished_processing.emit()
    
    def apply_preprocessing(self, img):
        if self.preprocessing_method == 'Grayscale':
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        elif self.preprocessing_method == 'Threshold':
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, processed = cv2.threshold(gray, self.threshold_value, 255, cv2.THRESH_BINARY)
            return processed
        elif self.preprocessing_method == 'Adaptive Threshold':
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        elif self.preprocessing_method == 'Denoise':
            return cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
        else:
            return img


class OCRScanner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image = None
        self.original_image = None
        self.camera = None
        self.timer = None
        self.roi_start = None
        self.roi_end = None
        self.selecting_roi = False
        self.roi_rect = None
        self.batch_processor = None
        self.batch_results = []
        
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Advanced OCR Scanner with Batch Processing')
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Single image processing tab
        self.single_tab = QWidget()
        self.tab_widget.addTab(self.single_tab, "Single Image")
        self.setup_single_tab()
        
        # Batch processing tab
        self.batch_tab = QWidget()
        self.tab_widget.addTab(self.batch_tab, "Batch Processing")
        self.setup_batch_tab()
    
    def setup_single_tab(self):
        main_layout = QHBoxLayout(self.single_tab)
        
        # Left panel - Controls
        left_panel = QVBoxLayout()
        
        # Input source group
        input_group = QGroupBox("Input Source")
        input_layout = QVBoxLayout()
        
        self.load_btn = QPushButton('Load Image')
        self.load_btn.clicked.connect(self.load_image)
        input_layout.addWidget(self.load_btn)
        
        self.camera_btn = QPushButton('Start Camera')
        self.camera_btn.clicked.connect(self.toggle_camera)
        input_layout.addWidget(self.camera_btn)
        
        self.capture_btn = QPushButton('Capture Frame')
        self.capture_btn.clicked.connect(self.capture_frame)
        self.capture_btn.setEnabled(False)
        input_layout.addWidget(self.capture_btn)
        
        input_group.setLayout(input_layout)
        left_panel.addWidget(input_group)
        
        # ROI Selection group
        roi_group = QGroupBox("ROI Selection")
        roi_layout = QVBoxLayout()
        
        self.roi_btn = QPushButton('Select ROI')
        self.roi_btn.clicked.connect(self.enable_roi_selection)
        self.roi_btn.setEnabled(False)
        roi_layout.addWidget(self.roi_btn)
        
        self.clear_roi_btn = QPushButton('Clear ROI')
        self.clear_roi_btn.clicked.connect(self.clear_roi)
        self.clear_roi_btn.setEnabled(False)
        roi_layout.addWidget(self.clear_roi_btn)
        
        roi_group.setLayout(roi_layout)
        left_panel.addWidget(roi_group)
        
        # Preprocessing group
        preprocess_group = QGroupBox("Preprocessing")
        preprocess_layout = QVBoxLayout()
        
        self.preprocess_combo = QComboBox()
        self.preprocess_combo.addItems(['None', 'Grayscale', 'Threshold', 
                                        'Adaptive Threshold', 'Denoise'])
        self.preprocess_combo.currentTextChanged.connect(self.apply_preprocessing)
        preprocess_layout.addWidget(QLabel('Method:'))
        preprocess_layout.addWidget(self.preprocess_combo)
        
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(0)
        self.threshold_slider.setMaximum(255)
        self.threshold_slider.setValue(127)
        self.threshold_slider.valueChanged.connect(self.apply_preprocessing)
        preprocess_layout.addWidget(QLabel('Threshold:'))
        preprocess_layout.addWidget(self.threshold_slider)
        self.threshold_label = QLabel('127')
        preprocess_layout.addWidget(self.threshold_label)
        self.threshold_slider.valueChanged.connect(
            lambda v: self.threshold_label.setText(str(v)))
        
        preprocess_group.setLayout(preprocess_layout)
        left_panel.addWidget(preprocess_group)
        
        # OCR group
        ocr_group = QGroupBox("OCR")
        ocr_layout = QVBoxLayout()
        
        self.ocr_btn = QPushButton('Run OCR')
        self.ocr_btn.clicked.connect(self.run_ocr)
        self.ocr_btn.setEnabled(False)
        ocr_layout.addWidget(self.ocr_btn)
        
        self.overlay_btn = QPushButton('Show Text Overlay')
        self.overlay_btn.clicked.connect(self.show_overlay)
        self.overlay_btn.setEnabled(False)
        ocr_layout.addWidget(self.overlay_btn)
        
        ocr_group.setLayout(ocr_layout)
        left_panel.addWidget(ocr_group)
        
        left_panel.addStretch()
        
        # Middle panel - Image display
        middle_panel = QVBoxLayout()
        
        self.image_label = QLabel()
        self.image_label.setMinimumSize(640, 480)
        self.image_label.setStyleSheet("border: 2px solid #888; background-color: #f0f0f0;")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("Load an image or start camera")
        self.image_label.mousePressEvent = self.mouse_press
        self.image_label.mouseMoveEvent = self.mouse_move
        self.image_label.mouseReleaseEvent = self.mouse_release
        middle_panel.addWidget(self.image_label)
        
        # Right panel - Text output
        right_panel = QVBoxLayout()
        
        right_panel.addWidget(QLabel('Extracted Text:'))
        self.text_output = QTextEdit()
        self.text_output.setMinimumWidth(300)
        self.text_output.setReadOnly(True)
        right_panel.addWidget(self.text_output)
        
        # Add panels to main layout
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(middle_panel, 3)
        main_layout.addLayout(right_panel, 2)
    
    def setup_batch_tab(self):
        main_layout = QHBoxLayout(self.batch_tab)
        
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
        self.batch_preprocess_combo.addItems(['None', 'Grayscale', 'Threshold', 
                                            'Adaptive Threshold', 'Denoise'])
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
        
    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff)")
        
        if file_name:
            self.original_image = cv2.imread(file_name)
            self.image = self.original_image.copy()
            self.display_image(self.image)
            self.ocr_btn.setEnabled(True)
            self.roi_btn.setEnabled(True)
            self.clear_roi()
            
    def toggle_camera(self):
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)
            self.camera_btn.setText('Stop Camera')
            self.capture_btn.setEnabled(True)
            self.load_btn.setEnabled(False)
        else:
            self.timer.stop()
            self.camera.release()
            self.camera = None
            self.camera_btn.setText('Start Camera')
            self.capture_btn.setEnabled(False)
            self.load_btn.setEnabled(True)
            
    def update_frame(self):
        ret, frame = self.camera.read()
        if ret:
            self.display_image(frame)
            
    def capture_frame(self):
        if self.camera is not None:
            ret, frame = self.camera.read()
            if ret:
                self.original_image = frame.copy()
                self.image = frame.copy()
                self.toggle_camera()
                self.ocr_btn.setEnabled(True)
                self.roi_btn.setEnabled(True)
                self.display_image(self.image)
                
    def enable_roi_selection(self):
        self.selecting_roi = True
        self.roi_start = None
        self.roi_end = None
        self.text_output.setText("Click and drag on the image to select ROI")
        
    def clear_roi(self):
        self.roi_rect = None
        self.roi_start = None
        self.roi_end = None
        self.selecting_roi = False
        if self.image is not None:
            self.display_image(self.image)
        self.clear_roi_btn.setEnabled(False)
        self.update_roi_checkbox()
        
    def mouse_press(self, event):
        if self.selecting_roi and self.image is not None:
            self.roi_start = (event.x(), event.y())
            
    def mouse_move(self, event):
        if self.selecting_roi and self.roi_start is not None:
            self.roi_end = (event.x(), event.y())
            self.display_image_with_roi()
            
    def mouse_release(self, event):
        if self.selecting_roi and self.roi_start is not None:
            self.roi_end = (event.x(), event.y())
            self.selecting_roi = False
            
            # Convert screen coordinates to image coordinates
            label_width = self.image_label.width()
            label_height = self.image_label.height()
            img_height, img_width = self.image.shape[:2]
            
            scale = min(label_width / img_width, label_height / img_height)
            scaled_width = int(img_width * scale)
            scaled_height = int(img_height * scale)
            
            offset_x = (label_width - scaled_width) // 2
            offset_y = (label_height - scaled_height) // 2
            
            x1 = max(0, int((self.roi_start[0] - offset_x) / scale))
            y1 = max(0, int((self.roi_start[1] - offset_y) / scale))
            x2 = min(img_width, int((self.roi_end[0] - offset_x) / scale))
            y2 = min(img_height, int((self.roi_end[1] - offset_y) / scale))
            
            if x2 > x1 and y2 > y1:
                self.roi_rect = (x1, y1, x2, y2)
                self.clear_roi_btn.setEnabled(True)
                self.display_image_with_roi()
                self.update_roi_checkbox()
                
    def display_image_with_roi(self):
        if self.image is None:
            return
            
        display_img = self.image.copy()
        
        if self.roi_start and self.roi_end:
            # Draw temporary ROI rectangle
            label_width = self.image_label.width()
            label_height = self.image_label.height()
            img_height, img_width = display_img.shape[:2]
            
            scale = min(label_width / img_width, label_height / img_height)
            offset_x = (label_width - int(img_width * scale)) // 2
            offset_y = (label_height - int(img_height * scale)) // 2
            
            x1 = max(0, int((self.roi_start[0] - offset_x) / scale))
            y1 = max(0, int((self.roi_start[1] - offset_y) / scale))
            x2 = min(img_width, int((self.roi_end[0] - offset_x) / scale))
            y2 = min(img_height, int((self.roi_end[1] - offset_y) / scale))
            
            cv2.rectangle(display_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        elif self.roi_rect:
            x1, y1, x2, y2 = self.roi_rect
            cv2.rectangle(display_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
        self.display_image(display_img)
        
    def display_image(self, img):
        if len(img.shape) == 2:
            height, width = img.shape
            bytes_per_line = width
            q_img = QImage(img.data, width, height, bytes_per_line, 
                          QImage.Format_Grayscale8)
        else:
            height, width, channel = img.shape
            bytes_per_line = 3 * width
            rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            q_img = QImage(rgb_image.data, width, height, bytes_per_line, 
                          QImage.Format_RGB888)
        
        pixmap = QPixmap.fromImage(q_img)
        scaled_pixmap = pixmap.scaled(self.image_label.size(), 
                                     Qt.KeepAspectRatio, 
                                     Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)
        
    def apply_preprocessing(self):
        if self.original_image is None:
            return
            
        method = self.preprocess_combo.currentText()
        img = self.original_image.copy()
        
        if method == 'Grayscale':
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        elif method == 'Threshold':
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, img = cv2.threshold(gray, self.threshold_slider.value(), 
                                  255, cv2.THRESH_BINARY)
        elif method == 'Adaptive Threshold':
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.adaptiveThreshold(gray, 255, 
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
        elif method == 'Denoise':
            img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
            
        self.image = img
        self.display_image_with_roi() if self.roi_rect else self.display_image(img)
        
    def run_ocr(self):
        if self.image is None:
            return
            
        # Get the image to process
        if self.roi_rect:
            x1, y1, x2, y2 = self.roi_rect
            ocr_image = self.image[y1:y2, x1:x2]
        else:
            ocr_image = self.image
            
        # Convert to PIL Image
        if len(ocr_image.shape) == 2:
            pil_image = Image.fromarray(ocr_image)
        else:
            rgb_image = cv2.cvtColor(ocr_image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            
        # Run OCR
        try:
            text = pytesseract.image_to_string(pil_image)
            self.text_output.setText(text)
            self.overlay_btn.setEnabled(True)
        except Exception as e:
            self.text_output.setText(f"Error: {str(e)}")
            
    def show_overlay(self):
        if self.image is None:
            return
            
        # Get the image to process
        if self.roi_rect:
            x1, y1, x2, y2 = self.roi_rect
            ocr_image = self.image[y1:y2, x1:x2].copy()
            offset = (x1, y1)
        else:
            ocr_image = self.image.copy()
            offset = (0, 0)
            
        # Convert to PIL Image
        if len(ocr_image.shape) == 2:
            pil_image = Image.fromarray(ocr_image)
        else:
            rgb_image = cv2.cvtColor(ocr_image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            
        # Get bounding boxes
        try:
            data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
            
            # Draw on original image
            overlay_img = self.original_image.copy()
            
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 60:
                    x = data['left'][i] + offset[0]
                    y = data['top'][i] + offset[1]
                    w = data['width'][i]
                    h = data['height'][i]
                    
                    cv2.rectangle(overlay_img, (x, y), (x + w, y + h), 
                                (0, 255, 0), 2)
                    cv2.putText(overlay_img, data['text'][i], (x, y - 5),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            
            self.display_image(overlay_img)
        except Exception as e:
            self.text_output.append(f"\nOverlay Error: {str(e)}")
    
    def load_batch_images(self):
        file_names, _ = QFileDialog.getOpenFileNames(
            self, "Select Images for Batch Processing", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff)")
        
        if file_names:
            self.file_list.clear()
            for file_name in file_names:
                self.file_list.addItem(os.path.basename(file_name))
            
            # Store full paths for processing
            self.batch_file_paths = file_names
            self.batch_process_btn.setEnabled(True)
            
            # Update ROI checkbox state
            if self.roi_rect:
                self.use_roi_checkbox.setEnabled(True)
                self.use_roi_checkbox.setText(f'Use ROI from Single Image Tab ({self.roi_rect})')
            else:
                self.use_roi_checkbox.setEnabled(False)
                self.use_roi_checkbox.setText('Use ROI from Single Image Tab (No ROI set)')
    
    def clear_batch_list(self):
        self.file_list.clear()
        self.batch_file_paths = []
        self.batch_process_btn.setEnabled(False)
        self.use_roi_checkbox.setEnabled(False)
        self.results_table.setRowCount(0)
        self.batch_results = []
        self.batch_export_btn.setEnabled(False)
    
    def start_batch_processing(self):
        if not hasattr(self, 'batch_file_paths') or not self.batch_file_paths:
            return
        
        # Get processing parameters
        preprocessing_method = self.batch_preprocess_combo.currentText()
        threshold_value = self.batch_threshold_slider.value()
        roi_rect = self.roi_rect if self.use_roi_checkbox.isChecked() else None
        
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
    
    def cancel_batch_processing(self):
        if self.batch_processor:
            self.batch_processor.cancel()
            self.batch_processor.wait()
        self.batch_processing_finished()
    
    def update_batch_progress(self, value):
        self.progress_bar.setValue(value)
    
    def add_batch_result(self, filename, text, status):
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
        # Re-enable controls
        self.batch_process_btn.setEnabled(True)
        self.batch_cancel_btn.setEnabled(False)
        self.batch_load_btn.setEnabled(True)
        self.batch_clear_btn.setEnabled(True)
        
        if self.batch_results:
            self.batch_export_btn.setEnabled(True)
            
        # Show completion message
        successful = len([r for r in self.batch_results if r['status'] == 'Success'])
        total = len(self.batch_results)
        
        QMessageBox.information(self, "Batch Processing Complete", 
                              f"Processing completed!\n"
                              f"Successfully processed: {successful}/{total} images")
    
    def export_batch_results(self):
        if not self.batch_results:
            return
        
        # Get export file path
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Batch Results", 
            f"batch_ocr_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;CSV Files (*.csv)")
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.csv'):
                self.export_to_csv(file_path)
            else:
                self.export_to_txt(file_path)
            
            QMessageBox.information(self, "Export Complete", 
                                  f"Results exported successfully to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", 
                               f"Failed to export results:\n{str(e)}")
    
    def export_to_txt(self, file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("OCR Batch Processing Results\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total files processed: {len(self.batch_results)}\n\n")
            
            for i, result in enumerate(self.batch_results, 1):
                f.write(f"File {i}: {result['filename']}\n")
                f.write(f"Status: {result['status']}\n")
                f.write(f"Processed: {result['timestamp']}\n")
                f.write("Extracted Text:\n")
                f.write("-" * 30 + "\n")
                f.write(result['text'] if result['text'] else "(No text detected)")
                f.write("\n" + "=" * 50 + "\n\n")
    
    def export_to_csv(self, file_path):
        import csv
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Filename', 'Status', 'Timestamp', 'Extracted Text'])
            
            for result in self.batch_results:
                writer.writerow([
                    result['filename'],
                    result['status'], 
                    result['timestamp'],
                    result['text'].replace('\n', ' ').replace('\r', ' ')
                ])
    
    def update_roi_checkbox(self):
        """Update the ROI checkbox in batch tab when ROI changes in single tab"""
        if hasattr(self, 'use_roi_checkbox'):
            if self.roi_rect:
                self.use_roi_checkbox.setEnabled(True)
                self.use_roi_checkbox.setText(f'Use ROI from Single Image Tab {self.roi_rect}')
            else:
                self.use_roi_checkbox.setEnabled(False)
                self.use_roi_checkbox.setText('Use ROI from Single Image Tab (No ROI set)')
                self.use_roi_checkbox.setChecked(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    scanner = OCRScanner()
    scanner.show()
    sys.exit(app.exec_())