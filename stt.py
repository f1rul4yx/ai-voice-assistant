import numpy as np
from faster_whisper import WhisperModel
import config


class STT:
    def __init__(self):
        self._model: WhisperModel | None = None

    def transcribe(self, audio: np.ndarray) -> str:
        if self._model is None:
            self._model = WhisperModel(config.WHISPER_MODEL, device="cpu", compute_type="int8")

        kwargs = {"beam_size": 1, "vad_filter": False}
        if config.WHISPER_LANGUAGE is not None:
            kwargs["language"] = config.WHISPER_LANGUAGE

        segments, _ = self._model.transcribe(audio.astype(np.float32), **kwargs)
        return " ".join(s.text for s in segments).strip()
