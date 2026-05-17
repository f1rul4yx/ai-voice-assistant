from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTextEdit, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCursor
import html


class TerminalWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_style()

    def setup_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.resize(600, 400)

        central = QWidget(self)
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.status_bar = QLabel("ALT+Z para hablar")
        self.status_bar.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.status_bar.setFixedHeight(24)
        layout.addWidget(self.status_bar)

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setFont(QFont("JetBrains Mono", 10))
        self.chat.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        layout.addWidget(self.chat)

    def setup_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0d0d0d;
            }
            QLabel {
                color: #666;
                padding: 4px 12px;
                font-size: 11px;
                font-family: 'JetBrains Mono', monospace;
                border-bottom: 1px solid #222;
            }
            QTextEdit {
                background-color: #0d0d0d;
                color: #e0e0e0;
                border: none;
                padding: 12px;
                font-family: 'JetBrains Mono', monospace;
                selection-background-color: #333;
            }
        """)

    def load_history(self, history):
        self.chat.clear()
        for msg in history:
            if msg["role"] == "user":
                self.add_user_message(msg["content"])
            elif msg["role"] == "assistant":
                self.add_assistant_message(msg["content"])

    def add_user_message(self, text: str):
        cursor = self.chat.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(f'<span style="color: #56b6c2;">&gt; </span><span style="color: #e0e0e0;">{html.escape(text)}</span><br><br>')
        self.chat.setTextCursor(cursor)
        self.chat.ensureCursorVisible()

    def add_assistant_message(self, text: str):
        cursor = self.chat.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        formatted = html.escape(text).replace("\n", "<br>")
        cursor.insertHtml(f'<span style="color: #98c379;">{formatted}</span><br><br>')
        self.chat.setTextCursor(cursor)
        self.chat.ensureCursorVisible()

    def add_system_message(self, text: str):
        cursor = self.chat.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(f'<span style="color: #555; font-style: italic;">{html.escape(text)}</span><br><br>')
        self.chat.setTextCursor(cursor)
        self.chat.ensureCursorVisible()

    def set_status(self, text: str):
        self.status_bar.setText(text)

    def clear(self):
        self.chat.clear()
