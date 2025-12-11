import sys
import cv2
import numpy as np
import pytesseract
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                             QFileDialog, QComboBox, QSlider, QGroupBox)
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
from PIL import Image

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
        
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Advanced OCR Scanner')
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    scanner = OCRScanner()
    scanner.show()
    sys.exit(app.exec_())