import asyncio
import subprocess
import edge_tts
import tempfile
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TextToSpeech:
    def __init__(self, voice="es-ES-AlvaroNeural"):
        self.voice = voice
        self._process = None

    async def _generate_speech(self, text: str) -> str:
        communicate = edge_tts.Communicate(text, self.voice)
        temp_path = tempfile.mktemp(suffix=".mp3")
        await communicate.save(temp_path)
        return temp_path

    def speak(self, text: str):
        if not text:
            return

        try:
            logger.info(f"Generando audio TTS para: '{text[:50]}...'")
            audio_path = asyncio.run(self._generate_speech(text))
            logger.info(f"Audio TTS generado: {audio_path}")

            logger.info("Reproduciendo con ffplay...")
            self._process = subprocess.Popen(
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", audio_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self._process.wait()
            logger.info("ffplay terminado")

            Path(audio_path).unlink(missing_ok=True)
            logger.info("TTS completado")
        except Exception as e:
            logger.error(f"Error en TTS: {e}")
        finally:
            self._process = None

    def stop(self):
        if self._process:
            logger.info("Deteniendo TTS...")
            self._process.terminate()
            try:
                self._process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait()
            self._process = None
            logger.info("TTS detenido")
