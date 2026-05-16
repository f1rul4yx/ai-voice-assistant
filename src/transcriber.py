import whisper
from pathlib import Path


class Transcriber:
    def __init__(self, model_size="base"):
        print(f"Cargando modelo Whisper '{model_size}'...")
        self.model = whisper.load_model(model_size)
        print("Modelo Whisper cargado.")

    def transcribe(self, audio_path: str, language="es") -> str:
        if not Path(audio_path).exists():
            return ""

        result = self.model.transcribe(
            audio_path,
            language=language,
            fp16=False
        )
        return result.get("text", "").strip()
