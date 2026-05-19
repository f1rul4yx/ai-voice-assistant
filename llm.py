import json
import subprocess
import os
import logging
import config

log = logging.getLogger(__name__)


class LLM:
    def __init__(self):
        self._bin = os.path.expanduser(config.OPENCODE_BIN)
        self._model = config.OPENCODE_MODEL

    def chat(self, message: str) -> str:
        prompt = f"[Instrucciones: {config.SYSTEM_PROMPT}]\n\n{message}"

        cmd = [
            self._bin, "run", prompt,
            "--model", self._model,
            "--format", "json",
            "--dangerously-skip-permissions",
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except FileNotFoundError:
            log.error(f"opencode no encontrado en {self._bin}")
            return f"Error: opencode no encontrado en {self._bin}"
        except subprocess.TimeoutExpired:
            log.error("opencode timeout")
            return "La IA tardó demasiado en responder."

        texts = []
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if data.get("type") == "text" and "text" in data.get("part", {}):
                    texts.append(data["part"]["text"])
            except json.JSONDecodeError:
                continue

        if texts:
            return " ".join(texts)

        log.error(f"opencode sin respuesta. stderr: {result.stderr[:300]}")
        return "No se pudo obtener respuesta de la IA."
