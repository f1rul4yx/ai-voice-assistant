import subprocess
from typing import Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class OpenCodeClient:
    def __init__(self):
        self.history = []

    def send_message(self, message: str, screenshot_path: Optional[str] = None) -> Optional[str]:
        needs_screenshot = self._needs_screenshot(message)

        cmd = ["opencode", "run"]
        if needs_screenshot and screenshot_path:
            abs_path = str(Path(screenshot_path).resolve())
            if Path(abs_path).exists():
                cmd.extend(["-f", abs_path, "--"])
                logger.info(f"Captura adjunta: {abs_path}")
            else:
                logger.warning(f"Captura no encontrada: {abs_path}")
        else:
            logger.info("Sin captura (no necesaria)")

        cmd.append(message)

        self.history.append({"role": "user", "content": message})

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            response = result.stdout.strip()

            if response:
                self.history.append({"role": "assistant", "content": response})
                return response

            if result.stderr:
                logger.error(f"opencode stderr: {result.stderr}")
                return f"Error: {result.stderr.strip()}"

            return "No se recibió respuesta."

        except subprocess.TimeoutExpired:
            return "La consulta tardó demasiado."
        except FileNotFoundError:
            return "opencode no está en el PATH."
        except Exception as e:
            return f"Error: {str(e)}"

    def _needs_screenshot(self, message: str) -> bool:
        visual_keywords = [
            "ves", "pantalla", "monitor", "abre", "abierto", "viendo",
            "color", "imagen", "foto", "captura", "describe", "muestra",
            "qué hay", "que hay", "qué tengo", "que tengo", "icono",
            "ventana", "escritorio", "aplicación", "programa",
            "what do you see", "what's on", "screenshot", "screen",
            "mira", "observa", "visual"
        ]
        msg_lower = message.lower()
        return any(kw in msg_lower for kw in visual_keywords)

    def get_history(self):
        return self.history
