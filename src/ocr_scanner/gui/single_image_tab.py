"""
Single image processing tab for OCR Scanner.
"""

import logging
from typing import Optional, Tuple
import cv2
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTextEdit, QFileDialog, QComboBox, 
                             QSlider, QGroupBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap

from ..core.image_processor import ImageProcessor
from ..utils.image_utils import ImageUtils
from ..config.settings import IMAGE_FILTER, PREPROCESSING_OPTIONS, DEFAULT_IMAGE_DISPLAY_SIZE, SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)


class SingleImageTab(QWidget):
    """Tab for single image processing."""
    
    roi_changed = pyqtSignal(object)  # Emits ROI rectangle or None
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None
        self.original_image = None
        self.camera = None
        self.timer = None
        self.roi_start = None
        self.roi_end = None
        self.selecting_roi = False
        self.roi_rect = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QHBoxLayout(self)
        
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
        self.preprocess_combo.addItems(PREPROCESSING_OPTIONS)
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
        
        # Language selection
        ocr_layout.addWidget(QLabel('Language:'))
        self.language_combo = QComboBox()
        for code, name in SUPPORTED_LANGUAGES.items():
            self.language_combo.addItem(f"{name} ({code})", code)
        self.language_combo.setCurrentText("English (eng)")
        ocr_layout.addWidget(self.language_combo)
        
        # Confidence threshold
        ocr_layout.addWidget(QLabel('Confidence Threshold:'))
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setMinimum(0)
        self.confidence_slider.setMaximum(100)
        self.confidence_slider.setValue(60)
        ocr_layout.addWidget(self.confidence_slider)
        self.confidence_label = QLabel('60%')
        ocr_layout.addWidget(self.confidence_label)
        self.confidence_slider.valueChanged.connect(
            lambda v: self.confidence_label.setText(f'{v}%'))
        
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
        self.image_label.setMinimumSize(*DEFAULT_IMAGE_DISPLAY_SIZE)
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
    
    def load_image(self):
        """Load image from file."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", IMAGE_FILTER)
        
        if file_name:
            self.original_image = cv2.imread(file_name)
            if self.original_image is not None:
                self.image = self.original_image.copy()
                self.display_image(self.image)
                self.ocr_btn.setEnabled(True)
                self.roi_btn.setEnabled(True)
                self.clear_roi()
                logger.info(f"Loaded image: {file_name}")
            else:
                logger.error(f"Failed to load image: {file_name}")
    
    def toggle_camera(self):
        """Toggle camera on/off."""
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)
            if self.camera.isOpened():
                self.timer = QTimer()
                self.timer.timeout.connect(self.update_frame)
                self.timer.start(30)
                self.camera_btn.setText('Stop Camera')
                self.capture_btn.setEnabled(True)
                self.load_btn.setEnabled(False)
                logger.info("Camera started")
            else:
                logger.error("Failed to open camera")
                self.camera = None
        else:
            self.timer.stop()
            self.camera.release()
            self.camera = None
            self.camera_btn.setText('Start Camera')
            self.capture_btn.setEnabled(False)
            self.load_btn.setEnabled(True)
            logger.info("Camera stopped")
    
    def update_frame(self):
        """Update camera frame."""
        if self.camera is not None:
            ret, frame = self.camera.read()
            if ret:
                self.display_image(frame)
    
    def capture_frame(self):
        """Capture current camera frame."""
        if self.camera is not None:
            ret, frame = self.camera.read()
            if ret:
                self.original_image = frame.copy()
                self.image = frame.copy()
                self.toggle_camera()
                self.ocr_btn.setEnabled(True)
                self.roi_btn.setEnabled(True)
                self.display_image(self.image)
                logger.info("Frame captured")
    
    def enable_roi_selection(self):
        """Enable ROI selection mode."""
        self.selecting_roi = True
        self.roi_start = None
        self.roi_end = None
        self.text_output.setText("Click and drag on the image to select ROI")
    
    def clear_roi(self):
        """Clear ROI selection."""
        self.roi_rect = None
        self.roi_start = None
        self.roi_end = None
        self.selecting_roi = False
        if self.image is not None:
            self.display_image(self.image)
        self.clear_roi_btn.setEnabled(False)
        self.roi_changed.emit(None)
    
    def mouse_press(self, event):
        """Handle mouse press for ROI selection."""
        if self.selecting_roi and self.image is not None:
            self.roi_start = (event.x(), event.y())
    
    def mouse_move(self, event):
        """Handle mouse move for ROI selection."""
        if self.selecting_roi and self.roi_start is not None:
            self.roi_end = (event.x(), event.y())
            self.display_image_with_roi()
    
    def mouse_release(self, event):
        """Handle mouse release for ROI selection."""
        if self.selecting_roi and self.roi_start is not None:
            self.roi_end = (event.x(), event.y())
            self.selecting_roi = False
            
            # Convert screen coordinates to image coordinates
            img_size = (self.image.shape[1], self.image.shape[0])
            display_size = (self.image_label.width(), self.image_label.height())
            
            start_img = ImageUtils.screen_to_image_coords(self.roi_start, img_size, display_size)
            end_img = ImageUtils.screen_to_image_coords(self.roi_end, img_size, display_size)
            
            x1, y1 = start_img
            x2, y2 = end_img
            
            if x2 > x1 and y2 > y1:
                self.roi_rect = (x1, y1, x2, y2)
                self.clear_roi_btn.setEnabled(True)
                self.display_image_with_roi()
                self.roi_changed.emit(self.roi_rect)
                logger.info(f"ROI selected: {self.roi_rect}")
    
    def display_image_with_roi(self):
        """Display image with ROI overlay."""
        if self.image is None:
            return
        
        display_img = self.image.copy()
        
        if self.roi_start and self.roi_end:
            # Draw temporary ROI rectangle
            img_size = (display_img.shape[1], display_img.shape[0])
            display_size = (self.image_label.width(), self.image_label.height())
            
            start_img = ImageUtils.screen_to_image_coords(self.roi_start, img_size, display_size)
            end_img = ImageUtils.screen_to_image_coords(self.roi_end, img_size, display_size)
            
            cv2.rectangle(display_img, start_img, end_img, (0, 255, 0), 2)
        elif self.roi_rect:
            x1, y1, x2, y2 = self.roi_rect
            cv2.rectangle(display_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        self.display_image(display_img)
    
    def display_image(self, img):
        """Display image in label."""
        pixmap = ImageUtils.create_scaled_pixmap(img, self.image_label.size())
        self.image_label.setPixmap(pixmap)
    
    def apply_preprocessing(self):
        """Apply preprocessing to image."""
        if self.original_image is None:
            return
        
        method = self.preprocess_combo.currentText()
        threshold_value = self.threshold_slider.value()
        
        self.image = ImageProcessor.apply_preprocessing(
            self.original_image.copy(), method, threshold_value)
        
        if self.roi_rect:
            self.display_image_with_roi()
        else:
            self.display_image(self.image)
    
    def run_ocr(self):
        """Run OCR on current image."""
        if self.image is None:
            return
        
        try:
            # Get the image to process
            if self.roi_rect:
                ocr_image = ImageProcessor.apply_roi(self.image, self.roi_rect)
            else:
                ocr_image = self.image
            
            # Get selected language
            language = self.language_combo.currentData()
            
            # Run OCR
            text = ImageProcessor.run_ocr(ocr_image, language)
            self.text_output.setText(text)
            self.overlay_btn.setEnabled(True)
            logger.info(f"OCR completed successfully with language: {language}")
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.text_output.setText(error_msg)
            logger.error(f"OCR failed: {e}")
    
    def show_overlay(self):
        """Show text overlay on image."""
        if self.image is None:
            return
        
        try:
            # Get the image to process
            if self.roi_rect:
                ocr_image = ImageProcessor.apply_roi(self.image, self.roi_rect)
                offset = (self.roi_rect[0], self.roi_rect[1])
            else:
                ocr_image = self.image.copy()
                offset = (0, 0)
            
            # Get bounding boxes
            language = self.language_combo.currentData()
            confidence_threshold = self.confidence_slider.value()
            data = ImageProcessor.get_text_boxes(ocr_image, confidence_threshold, language)
            
            # Draw on original image
            overlay_img = self.original_image.copy()
            
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > confidence_threshold:
                    x = data['left'][i] + offset[0]
                    y = data['top'][i] + offset[1]
                    w = data['width'][i]
                    h = data['height'][i]
                    
                    cv2.rectangle(overlay_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(overlay_img, data['text'][i], (x, y - 5),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            
            self.display_image(overlay_img)
            logger.info("Text overlay displayed")
            
        except Exception as e:
            self.text_output.append(f"\nOverlay Error: {str(e)}")
            logger.error(f"Overlay failed: {e}")