import sys
import threading
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from src.terminal_window import TerminalWindow
from src.audio_recorder import AudioRecorder
from src.transcriber import Transcriber
from src.tts import TextToSpeech
from src.opencode_client import OpenCodeClient
from src.screen_capture import ScreenCapture
from src.hotkey_manager import HotkeyManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class VoiceAssistant:
    def __init__(self):
        logger.info("=== Iniciando asistente ===")
        self.app = QApplication(sys.argv)
        self.window = TerminalWindow()
        self.window.hide()

        self.recorder = AudioRecorder()
        self.transcriber = Transcriber(model_size="base")
        self.tts = TextToSpeech()
        self.opencode = OpenCodeClient()
        self.screencap = ScreenCapture()
        self.hotkey = HotkeyManager()

        self.state = "idle"
        self._lock = threading.Lock()
        self._tts_thread = None

        self.hotkey.hotkey_pressed.connect(self.on_hotkey)
        self.hotkey.start_listening()

    def on_hotkey(self):
        with self._lock:
            logger.info(f"Hotkey pulsado! Estado: {self.state}")
            if self.state == "idle":
                self.start_listening()
            elif self.state == "recording":
                self.stop_and_process()
            elif self.state == "processing":
                logger.info("Ignorado: aún procesando")
            elif self.state == "speaking":
                logger.info("Interrumpiendo TTS")
                self.tts.stop()
                self._do_hide()

    def start_listening(self):
        self.state = "recording"
        self.window.load_history(self.opencode.get_history())
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()
        self.window.set_status("Grabando...")
        self.recorder.start_recording()
        logger.info("Grabación iniciada")

    def stop_and_process(self):
        self.state = "processing"
        self.window.set_status("Procesando...")

        audio_path = self.recorder.stop_recording()
        logger.info(f"Audio: {audio_path}")

        if not audio_path:
            self._ui("add_system_message", "Error: no se grabó audio")
            self._finish()
            return

        import os
        size = os.path.getsize(audio_path)
        logger.info(f"Audio size: {size} bytes")

        if size < 1000:
            self._ui("add_system_message", "Error: audio vacío")
            self._finish()
            return

        threading.Thread(target=self._process_audio, args=(audio_path,), daemon=True).start()

    def _process_audio(self, audio_path: str):
        try:
            logger.info("Transcribiendo...")
            self._ui("set_status", "Transcribiendo...")
            transcription = self.transcriber.transcribe(audio_path)
            logger.info(f"Texto: '{transcription}'")

            if not transcription:
                self._ui("add_system_message", "No se pudo transcribir")
                self._finish()
                return

            self._ui("add_user_message", transcription)

            logger.info("Consultando opencode...")
            self._ui("set_status", "Consultando...")

            screenshot_path = None
            if self.opencode._needs_screenshot(transcription):
                logger.info("Captura necesaria")
                self._ui("set_status", "Capturando pantalla...")
                screenshot_path = self.screencap.capture()

            response = self.opencode.send_message(transcription, screenshot_path)
            logger.info(f"Respuesta: {response[:80] if response else 'Ninguna'}...")

            if response:
                self._ui("add_assistant_message", response)
                logger.info("Reproduciendo TTS...")
                self._ui("set_status", "Reproduciendo... (ALT+Z para cortar)")
                self.state = "speaking"
                self._tts_thread = threading.Thread(
                    target=self._speak_and_close, args=(response,), daemon=True
                )
                self._tts_thread.start()
            else:
                self._ui("add_system_message", "Sin respuesta")
                self._finish()

        except Exception as e:
            logger.exception(f"Error: {e}")
            self._ui("add_system_message", f"Error: {str(e)}")
            self._finish()

    def _speak_and_close(self, text: str):
        self.tts.speak(text)
        logger.info("TTS finalizado")
        self._ui("set_status", "ALT+Z para hablar")
        QTimer.singleShot(0, self._do_hide)

    def _ui(self, method_name, *args):
        func = getattr(self.window, method_name)
        QTimer.singleShot(0, lambda: func(*args))

    def _finish(self):
        self._ui("set_status", "ALT+Z para hablar")
        QTimer.singleShot(2000, self._do_hide)

    def _do_hide(self):
        self.window.hide()
        with self._lock:
            self.state = "idle"

    def run(self):
        logger.info("Asistente listo. Presiona ALT+Z.")
        return self.app.exec()

    def cleanup(self):
        self.tts.stop()
        self.hotkey.stop_listening()


def main():
    assistant = VoiceAssistant()
    try:
        exit_code = assistant.run()
    finally:
        assistant.cleanup()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
