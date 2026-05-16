import threading
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
import logging

logger = logging.getLogger(__name__)


class HotkeyManager(QObject):
    hotkey_pressed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._trigger_file = Path("/tmp/ai_voice_trigger")

    def start_listening(self):
        self._trigger_file.unlink(missing_ok=True)
        self._poll_timer = QTimer()
        self._poll_timer.timeout.connect(self._check_trigger)
        self._poll_timer.start(200)
        logger.info("Hotkey: usando archivo trigger (compatible X11/Wayland)")
        logger.info(f"  Configura tu atajo para ejecutar: {self._trigger_file}")

    def _check_trigger(self):
        if self._trigger_file.exists():
            self._trigger_file.unlink()
            self.hotkey_pressed.emit()

    def stop_listening(self):
        if hasattr(self, '_poll_timer'):
            self._poll_timer.stop()
