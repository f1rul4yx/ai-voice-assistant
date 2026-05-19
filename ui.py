from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication, QSizePolicy
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor
import config

STYLESHEET = """
QWidget#AssistantWindow {
    background-color: rgba(30, 30, 46, 240);
    border: 1px solid rgba(137, 180, 250, 100);
    border-radius: 12px;
}
QLabel#StatusLabel { color: #89b4fa; font-size: 13px; font-weight: bold; }
QLabel#TranscriptionLabel { color: #cdd6f4; font-size: 13px; }
QLabel#ResponseLabel { color: #a6e3a1; font-size: 13px; }
QLabel#HotkeyLabel { color: rgba(108, 112, 134, 200); font-size: 10px; }
"""

STATES = {
    "idle": ("Listo", "#89b4fa"),
    "listening": ("\U0001f3a4 Escuchando...", "#89b4fa"),
    "thinking": ("\U0001f4ad Pensando...", "#f9e2af"),
    "speaking": ("\U0001f50a Hablando...", "#a6e3a1"),
    "error": ("\u2717 Error", "#f38ba8"),
}


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("AssistantWindow")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self.setStyleSheet(STYLESHEET)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        self.status = QLabel("Listo")
        self.status.setObjectName("StatusLabel")
        layout.addWidget(self.status)

        self.transcription = QLabel("")
        self.transcription.setObjectName("TranscriptionLabel")
        self.transcription.setWordWrap(True)
        self.transcription.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.transcription, stretch=1)

        self.response = QLabel("")
        self.response.setObjectName("ResponseLabel")
        self.response.setWordWrap(True)
        self.response.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.response, stretch=2)

        self.hotkey_lbl = QLabel("Ctrl+Alt+Space para activar")
        self.hotkey_lbl.setObjectName("HotkeyLabel")
        self.hotkey_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.hotkey_lbl)

        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._hide_and_reset)
        self._position()

    def _position(self):
        screen = QApplication.primaryScreen()
        if screen:
            g = screen.availableGeometry()
            self.move(
                g.right() - config.WINDOW_WIDTH - config.WINDOW_MARGIN,
                g.bottom() - config.WINDOW_HEIGHT - config.WINDOW_MARGIN,
            )

    def _hide_and_reset(self):
        self.hide()
        self.status.setText("Listo")
        self.status.setStyleSheet("")
        self.transcription.setText("")
        self.response.setText("")

    def set_state(self, state: str):
        text, color = STATES.get(state, ("Listo", "#89b4fa"))
        self.status.setText(text)
        self.status.setStyleSheet(f"color: {color}; font-size: 13px; font-weight: bold;")

    def set_transcription(self, text: str):
        self.transcription.setText(f"Tu: {text}" if text else "")

    def set_response(self, text: str):
        self.response.setText(f"IA: {text}" if text else "")

    def show_window(self):
        self._timer.stop()
        self._position()
        self.show()
        self.raise_()

    def schedule_hide(self, seconds: int = 3):
        self._timer.start(seconds * 1000)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(30, 30, 46, 240))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(self.rect(), 12, 12)
        super().paintEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self._hide_and_reset()
        super().keyPressEvent(event)
