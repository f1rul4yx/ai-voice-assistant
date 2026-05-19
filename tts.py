import asyncio
import subprocess
import os
import tempfile
import logging
import config

log = logging.getLogger(__name__)


class TTS:
    def __init__(self):
        self._voice = config.TTS_VOICE

    def speak(self, text: str) -> None:
        if not text.strip():
            return
        try:
            asyncio.run(self._generate_and_play(text))
        except Exception as e:
            log.error(f"TTS error: {e}")

    async def _generate_and_play(self, text: str) -> None:
        import edge_tts

        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        tmp_path = tmp.name
        tmp.close()

        try:
            await edge_tts.Communicate(text, self._voice).save(tmp_path)
            subprocess.run(
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", tmp_path],
                check=True, timeout=30,
            )
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
