from PySide6 import QtWidgets, QtGui, QtCore
import os
import sys
import config
import win_size_pos
import zipfile
import whatshtml_fn
import re
from jinja2 import Template
import shutil
from functools import partial
from urllib.parse import urlparse

"""This app was created for anyone to be able to keep their memories from WhatsApp conversations. 
It converts input files - automatic WhatsApp export - to a HTML file including all attachments. 
Designed to be as user-friendly as possible."""

# Whatshtml class - converts whatsapp export to html
class whatshtml(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.temp_dir = "extracted_files"
        self.txt_file = None
        self.attachment_files = []
        self.setAcceptDrops(True) # Enable drag n drop for files
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        button_layout = QtWidgets.QHBoxLayout()
        win_size_pos.set_win_size(self)
        self.setWindowTitle("WhatsHTML")  # Window name
        config.apply_fusion_style()

        # Help label for users
        instruction_text = f"""<h2>Instructions to create a HTML page from a WhatsApp conversation export</h2>
        <p><b>The WhatsHTML app converts a text input to HMTL including all attachments.</b></p>
        <p>1. Drag and drop the exported *.zip file to the app window, or drag and drop the *.txt file 
        and any attachments. Alternatively add files clicking the <b>"Select source files"</b> button.</p>
        <p>2. Press the <b>"Create a HTML conversation"</b> button, the app will ask about the export name, 
        that's what the outpup folder will be named and this will also be the conversation title.</p>
        <p>3. Then set the bubble color of each participant and you can rename any of them.</p>
        <p>4. Next choose the primary participant, this only participant will be placed on the left, 
        others will be placed on the right.</p>
        <p>5. You'll be notified the app finished successfully and you'll find the output in the app 
        folder with your earlier selected name.</p>
        <p>{config.FEEDBACK_TEXT}</p>"""
        instruction_label = QtWidgets.QLabel(instruction_text)
        instruction_label.setWordWrap(True)  # More rows if text is too long
        # Adding logo
        logo_label = QtWidgets.QLabel(self)
        pixmap = QtGui.QPixmap(config.ICON_PATH)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter) # In the middle
        # Label to display input txt file (source)
        self.txt_info_label = QtWidgets.QLabel("COVERSATION TEXT FILE NOT FOUND")
        self.txt_info_label.setWordWrap(True)  # More rows if text is too long
        # Label to display input pics
        self.attachments_info_label = QtWidgets.QLabel("NO ATTACHMENTS DETECTED")
        self.attachments_info_label.setWordWrap(True)  # More rows if text is too long
        # Button to select input zip file
        self.select_zip_btn = QtWidgets.QPushButton('Select source files', self)
        self.select_zip_btn.clicked.connect(self.select_files)
        self.select_zip_btn.setStyleSheet(config.FN_BUTTON_STYLE)
        # Process files button
        self.process_btn = QtWidgets.QPushButton('Create a HTML conversation', self)
        self.process_btn.clicked.connect(lambda: whatshtml_fn.process_files(
            self.txt_file, self.attachment_files, self.temp_dir))
        self.process_btn.setStyleSheet(config.FN_BUTTON_STYLE)
        # Layout
        layout.addWidget(instruction_label)
        layout.addWidget(logo_label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.txt_info_label)
        layout.addWidget(self.attachments_info_label)
        button_layout.addWidget(self.select_zip_btn)
        button_layout.addWidget(self.process_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)  # Set layout for widget
        self.show()  # Display the window

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event: QtGui.QDropEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_name = url.toLocalFile()
                self.process_file(file_name)
        self.update_labels()

    def select_files(self):
        file_names, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select source files", "", "All files (*)")
        for file_name in file_names:
            self.process_file(file_name)
        self.update_labels()

    def process_file(self, file_path):
        if file_path.lower().endswith(".zip"):
            self.process_zip_file(file_path)
        elif file_path.lower().endswith(".txt"):
            self.txt_file = file_path
        else:
            self.attachment_files.append(file_path)

    def process_zip_file(self, zip_file_path):
        # Extract ZIP file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)

        # Process extracted files
        for root, _, files in os.walk(self.temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith(".txt"):
                    self.txt_file = file_path
                else:
                    self.attachment_files.append(file_path)

        self.update_labels()

    def update_labels(self):
        if self.txt_file:
            self.txt_info_label.setText(f"Conversation file: {os.path.basename(self.txt_file)}")
        else:
            self.txt_info_label.setText("COVERSATION TEXT FILE NOT FOUND.")

        self.attachments_info_label.setText(f"Number of attachments: {len(self.attachment_files)}")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = whatshtml()
    ex.show()
    sys.exit(app.exec())