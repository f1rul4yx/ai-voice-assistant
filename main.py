import sys
import threading
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from pynput import keyboard
import config
from audio import AudioRecorder
from stt import STT
from llm import LLM
from tts import TTS
from ui import Window

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
log = logging.getLogger(__name__)


class Assistant(QObject):
    state_changed = pyqtSignal(str)
    transcription_ready = pyqtSignal(str)
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.recorder = AudioRecorder()
        self.stt = STT()
        self.llm = LLM()
        self.tts = TTS()
        self._processing = False

    def toggle(self):
        if self._processing:
            return
        if self.recorder.is_recording():
            self._stop_and_process()
        else:
            self._start()

    def _start(self):
        self.state_changed.emit("listening")
        self.transcription_ready.emit("")
        self.response_ready.emit("")
        try:
            self.recorder.start()
        except Exception as e:
            self.error_occurred.emit(f"Error al grabar: {e}")

    def _stop_and_process(self):
        self._processing = True
        self.state_changed.emit("thinking")

        try:
            audio = self.recorder.stop()
        except Exception as e:
            self.error_occurred.emit(f"Error: {e}")
            self._processing = False
            self.state_changed.emit("idle")
            return

        if audio is None or len(audio) == 0:
            self._processing = False
            self.state_changed.emit("idle")
            return

        threading.Thread(target=self._process, args=(audio,), daemon=True).start()

    def _process(self, audio):
        try:
            text = self.stt.transcribe(audio)
            log.info(f"Transcripcion: '{text}'")
            self.transcription_ready.emit(text)

            if not text.strip():
                self._processing = False
                self.state_changed.emit("idle")
                return

            response = self.llm.chat(text)
            log.info(f"Respuesta: '{response[:80]}'")
            self.response_ready.emit(response)

            self.state_changed.emit("speaking")
            self.tts.speak(response)
            self.state_changed.emit("idle")
        except Exception as e:
            log.error(f"Error: {e}", exc_info=True)
            self.error_occurred.emit(str(e))
        finally:
            self._processing = False


class HotkeyListener(QObject):
    activated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._keys = set()
        self._listener = None

    def start(self):
        self._listener = keyboard.Listener(on_press=self._press, on_release=self._release)
        self._listener.start()

    def stop(self):
        if self._listener:
            self._listener.stop()

    def _press(self, key):
        name = self._key_name(key)
        if name:
            self._keys.add(name)
            if config.HOTKEY.issubset(self._keys):
                self.activated.emit()
                self._keys.clear()

    def _release(self, key):
        name = self._key_name(key)
        if name:
            self._keys.discard(name)

    @staticmethod
    def _key_name(key):
        if isinstance(key, keyboard.Key):
            return key.name.lower()
        if isinstance(key, keyboard.KeyCode) and key.char:
            return key.char.lower()
        return None


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    win = Window()
    assistant = Assistant()

    def on_state(s):
        win.set_state(s)
        if s == "idle":
            win.schedule_hide(3)

    def on_transcription(t):
        win.set_transcription(t)

    def on_response(r):
        win.set_response(r)

    def on_error(e):
        win.set_state("error")
        win.set_response(e)
        win.schedule_hide(5)

    assistant.state_changed.connect(on_state, Qt.ConnectionType.QueuedConnection)
    assistant.transcription_ready.connect(on_transcription, Qt.ConnectionType.QueuedConnection)
    assistant.response_ready.connect(on_response, Qt.ConnectionType.QueuedConnection)
    assistant.error_occurred.connect(on_error, Qt.ConnectionType.QueuedConnection)

    hotkey = HotkeyListener()

    def on_hotkey():
        win.show_window()
        assistant.toggle()

    hotkey.activated.connect(on_hotkey, Qt.ConnectionType.QueuedConnection)
    hotkey.start()

    app.aboutToQuit.connect(hotkey.stop)

    log.info(f"Nova iniciado ({config.OPENCODE_MODEL}). Ctrl+Alt+Space para hablar.")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
