import subprocess
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class AudioRecorder:
    def __init__(self, sample_rate=16000, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.recording = False
        self.process = None
        self.output_dir = Path("temp_media")
        self.output_dir.mkdir(exist_ok=True)

    def start_recording(self):
        output_path = self.output_dir / "recording.wav"
        logger.info(f"Iniciando parecord: {output_path}")
        self.recording = True
        self.process = subprocess.Popen(
            [
                "parecord", "-r",
                "--format=s16le",
                f"--rate={self.sample_rate}",
                f"--channels={self.channels}",
                str(output_path)
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
        logger.info(f"parecord PID: {self.process.pid}")

    def stop_recording(self) -> str:
        output_path = self.output_dir / "recording.wav"

        if self.process:
            logger.info("Terminando parecord...")
            self.process.terminate()
            try:
                _, stderr = self.process.communicate(timeout=5)
                logger.info(f"parecord stderr: {stderr.decode()[:200]}")
            except subprocess.TimeoutExpired:
                logger.warning("parecord no terminó, matando...")
                self.process.kill()
                self.process.communicate()
            self.recording = False

        if output_path.exists():
            size = output_path.stat().st_size
            logger.info(f"Audio guardado: {size} bytes")
            return str(output_path)

        logger.error("Archivo de audio no encontrado")
        return ""
