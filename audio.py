import logging
import queue
import numpy as np
import sounddevice as sd
from scipy.signal import resample_poly
from math import gcd
import config

log = logging.getLogger(__name__)


class AudioRecorder:
    def __init__(self):
        self._queue: queue.Queue = queue.Queue()
        self._frames: list[np.ndarray] = []
        self._is_recording = False
        self._stream: sd.InputStream | None = None
        self._rate: int = 44100

    def start(self) -> None:
        dev = sd.query_devices(kind="input")
        self._rate = int(dev["default_samplerate"])
        log.info(f"Mic: {dev['name']} at {self._rate}Hz")

        self._frames = []
        self._is_recording = True
        self._stream = sd.InputStream(
            samplerate=self._rate,
            channels=1,
            dtype="float32",
            callback=lambda indata, frames, time, status: self._queue.put(indata.copy()),
        )
        self._stream.start()

    def stop(self) -> np.ndarray | None:
        self._is_recording = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        while not self._queue.empty():
            self._frames.append(self._queue.get_nowait())

        if not self._frames:
            return None

        audio = np.concatenate(self._frames).flatten()

        if self._rate != config.WHISPER_SAMPLE_RATE:
            up = config.WHISPER_SAMPLE_RATE // gcd(self._rate, config.WHISPER_SAMPLE_RATE)
            down = self._rate // gcd(self._rate, config.WHISPER_SAMPLE_RATE)
            audio = resample_poly(audio, up, down).astype(np.float32)

        return audio

    def is_recording(self) -> bool:
        return self._is_recording
