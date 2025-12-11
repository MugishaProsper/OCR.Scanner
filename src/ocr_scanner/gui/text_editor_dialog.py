"""
Text editor dialog for OCR result correction.
"""

import logging
from typing import Optional
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTextEdit, QLabel, QCheckBox, QSpinBox, QGroupBox,
                             QSplitter, QListWidget, QListWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QTextCursor

logger = logging.getLogger(__name__)


class TextEditorDialog(QDialog):
    """Dialog for editing and correcting OCR results."""
    
    text_corrected = pyqtSignal(str)  # Emits corrected text
    
    def __init__(self, original_text: str, parent=None):
        super().__init__(parent)
        self.original_text = original_text
        self.corrected_text = original_text
        self.suggestions = []
        
        self.init_ui()
        self.load_text()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("OCR Text Editor & Corrector")
        self.setGeometry(200, 200, 800, 600)
        
        layout = QVBoxLayout(self)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - Text editor
        left_panel = QVBoxLayout()
        left_widget = QGroupBox("Text Editor")
        left_widget.setLayout(left_panel)
        
        # Original text (read-only)
        left_panel.addWidget(QLabel("Original OCR Text:"))
        self.original_text_edit = QTextEdit()
        self.original_text_edit.setReadOnly(True)
        self.original_text_edit.setMaximumHeight(150)
        self.original_text_edit.setFont(QFont("Courier", 10))
        left_panel.addWidget(self.original_text_edit)
        
        # Editable text
        left_panel.addWidget(QLabel("Corrected Text:"))
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Courier", 10))
        self.text_edit.textChanged.connect(self.on_text_changed)
        left_panel.addWidget(self.text_edit)
        
        # Text statistics
        stats_layout = QHBoxLayout()
        self.char_count_label = QLabel("Characters: 0")
        self.word_count_label = QLabel("Words: 0")
        self.line_count_label = QLabel("Lines: 0")
        stats_layout.addWidget(self.char_count_label)
        stats_layout.addWidget(self.word_count_label)
        stats_layout.addWidget(self.line_count_label)
        stats_layout.addStretch()
        left_panel.addLayout(stats_layout)
        
        splitter.addWidget(left_widget)
        
        # Right panel - Correction tools
        right_panel = QVBoxLayout()
        right_widget = QGroupBox("Correction Tools")
        right_widget.setLayout(right_panel)
        
        # Auto-correction options
        auto_correct_group = QGroupBox("Auto-Correction")
        auto_correct_layout = QVBoxLayout()
        
        self.fix_spacing_cb = QCheckBox("Fix spacing issues")
        self.fix_spacing_cb.setChecked(True)
        auto_correct_layout.addWidget(self.fix_spacing_cb)
        
        self.fix_punctuation_cb = QCheckBox("Fix punctuation")
        self.fix_punctuation_cb.setChecked(True)
        auto_correct_layout.addWidget(self.fix_punctuation_cb)
        
        self.fix_capitalization_cb = QCheckBox("Fix capitalization")
        self.fix_capitalization_cb.setChecked(True)
        auto_correct_layout.addWidget(self.fix_capitalization_cb)
        
        self.remove_noise_cb = QCheckBox("Remove noise characters")
        self.remove_noise_cb.setChecked(True)
        auto_correct_layout.addWidget(self.remove_noise_cb)
        
        auto_correct_btn = QPushButton("Apply Auto-Corrections")
        auto_correct_btn.clicked.connect(self.apply_auto_corrections)
        auto_correct_layout.addWidget(auto_correct_btn)
        
        auto_correct_group.setLayout(auto_correct_layout)
        right_panel.addWidget(auto_correct_group)
        
        # Manual corrections
        manual_group = QGroupBox("Manual Corrections")
        manual_layout = QVBoxLayout()
        
        # Find and replace
        find_replace_layout = QHBoxLayout()
        self.find_text = QTextEdit()
        self.find_text.setMaximumHeight(30)
        self.find_text.setPlaceholderText("Find...")
        find_replace_layout.addWidget(self.find_text)
        
        self.replace_text = QTextEdit()
        self.replace_text.setMaximumHeight(30)
        self.replace_text.setPlaceholderText("Replace with...")
        find_replace_layout.addWidget(self.replace_text)
        
        replace_btn = QPushButton("Replace All")
        replace_btn.clicked.connect(self.replace_text_action)
        find_replace_layout.addWidget(replace_btn)
        
        manual_layout.addLayout(find_replace_layout)
        
        # Common corrections
        manual_layout.addWidget(QLabel("Common OCR Errors:"))
        self.suggestions_list = QListWidget()
        self.suggestions_list.itemDoubleClicked.connect(self.apply_suggestion)
        manual_layout.addWidget(self.suggestions_list)
        
        manual_group.setLayout(manual_layout)
        right_panel.addWidget(manual_group)
        
        # Text formatting
        format_group = QGroupBox("Formatting")
        format_layout = QVBoxLayout()
        
        format_btn_layout = QHBoxLayout()
        
        uppercase_btn = QPushButton("UPPERCASE")
        uppercase_btn.clicked.connect(lambda: self.format_text("upper"))
        format_btn_layout.addWidget(uppercase_btn)
        
        lowercase_btn = QPushButton("lowercase")
        lowercase_btn.clicked.connect(lambda: self.format_text("lower"))
        format_btn_layout.addWidget(lowercase_btn)
        
        title_btn = QPushButton("Title Case")
        title_btn.clicked.connect(lambda: self.format_text("title"))
        format_btn_layout.addWidget(title_btn)
        
        format_layout.addLayout(format_btn_layout)
        format_group.setLayout(format_layout)
        right_panel.addWidget(format_group)
        
        right_panel.addStretch()
        splitter.addWidget(right_widget)
        
        # Set splitter proportions
        splitter.setSizes([500, 300])
        
        # Button layout
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset to Original")
        reset_btn.clicked.connect(self.reset_text)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_changes)
        save_btn.setDefault(True)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
    def load_text(self):
        """Load the original text into editors."""
        self.original_text_edit.setPlainText(self.original_text)
        self.text_edit.setPlainText(self.original_text)
        self.update_statistics()
        self.generate_suggestions()
        
    def on_text_changed(self):
        """Handle text changes."""
        self.corrected_text = self.text_edit.toPlainText()
        self.update_statistics()
        
    def update_statistics(self):
        """Update text statistics."""
        text = self.corrected_text
        char_count = len(text)
        word_count = len(text.split()) if text.strip() else 0
        line_count = len(text.splitlines())
        
        self.char_count_label.setText(f"Characters: {char_count}")
        self.word_count_label.setText(f"Words: {word_count}")
        self.line_count_label.setText(f"Lines: {line_count}")
        
    def generate_suggestions(self):
        """Generate common OCR error corrections."""
        self.suggestions_list.clear()
        
        # Common OCR misrecognitions
        common_errors = [
            ("rn", "m"),
            ("cl", "d"),
            ("0", "O"),
            ("1", "l"),
            ("5", "S"),
            ("8", "B"),
            ("vv", "w"),
            ("nn", "m"),
            ("li", "h"),
            (".", ","),
            (" ,", ","),
            (" .", "."),
            ("  ", " "),  # Double spaces
            ("\\n\\n\\n", "\\n\\n"),  # Triple newlines
        ]
        
        text = self.corrected_text.lower()
        for wrong, correct in common_errors:
            if wrong in text:
                item = QListWidgetItem(f"Replace '{wrong}' with '{correct}'")
                item.setData(Qt.UserRole, (wrong, correct))
                self.suggestions_list.addItem(item)
                
    def apply_suggestion(self, item):
        """Apply a suggested correction."""
        wrong, correct = item.data(Qt.UserRole)
        current_text = self.text_edit.toPlainText()
        corrected = current_text.replace(wrong, correct)
        self.text_edit.setPlainText(corrected)
        
    def apply_auto_corrections(self):
        """Apply automatic corrections based on selected options."""
        text = self.text_edit.toPlainText()
        
        if self.remove_noise_cb.isChecked():
            # Remove common OCR noise characters
            noise_chars = "~`!@#$%^&*()_+-=[]{}|;':\",./<>?"
            for char in noise_chars:
                if text.count(char) / len(text) > 0.1:  # If more than 10% of text
                    text = text.replace(char, "")
                    
        if self.fix_spacing_cb.isChecked():
            # Fix spacing issues
            import re
            text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
            text = re.sub(r'\s+([,.!?;:])', r'\1', text)  # Space before punctuation
            text = re.sub(r'([,.!?;:])\s*', r'\1 ', text)  # Space after punctuation
            
        if self.fix_punctuation_cb.isChecked():
            # Fix common punctuation errors
            text = text.replace(' ,', ',')
            text = text.replace(' .', '.')
            text = text.replace(' !', '!')
            text = text.replace(' ?', '?')
            text = text.replace(',,', ',')
            text = text.replace('..', '.')
            
        if self.fix_capitalization_cb.isChecked():
            # Fix capitalization
            sentences = text.split('. ')
            sentences = [s.strip().capitalize() for s in sentences if s.strip()]
            text = '. '.join(sentences)
            
        self.text_edit.setPlainText(text)
        
    def replace_text_action(self):
        """Replace text based on find/replace inputs."""
        find_text = self.find_text.toPlainText().strip()
        replace_text = self.replace_text.toPlainText()
        
        if not find_text:
            return
            
        current_text = self.text_edit.toPlainText()
        if find_text in current_text:
            new_text = current_text.replace(find_text, replace_text)
            self.text_edit.setPlainText(new_text)
            
            # Clear find/replace fields
            self.find_text.clear()
            self.replace_text.clear()
        else:
            QMessageBox.information(self, "Not Found", f"Text '{find_text}' not found.")
            
    def format_text(self, format_type: str):
        """Apply text formatting."""
        cursor = self.text_edit.textCursor()
        
        if cursor.hasSelection():
            # Format selected text
            selected_text = cursor.selectedText()
            if format_type == "upper":
                formatted_text = selected_text.upper()
            elif format_type == "lower":
                formatted_text = selected_text.lower()
            elif format_type == "title":
                formatted_text = selected_text.title()
            else:
                return
                
            cursor.insertText(formatted_text)
        else:
            # Format entire text
            current_text = self.text_edit.toPlainText()
            if format_type == "upper":
                formatted_text = current_text.upper()
            elif format_type == "lower":
                formatted_text = current_text.lower()
            elif format_type == "title":
                formatted_text = current_text.title()
            else:
                return
                
            self.text_edit.setPlainText(formatted_text)
            
    def reset_text(self):
        """Reset text to original."""
        self.text_edit.setPlainText(self.original_text)
        
    def save_changes(self):
        """Save the corrected text."""
        self.corrected_text = self.text_edit.toPlainText()
        self.text_corrected.emit(self.corrected_text)
        self.accept()
        
    def get_corrected_text(self) -> str:
        """Get the corrected text."""
        return self.corrected_text