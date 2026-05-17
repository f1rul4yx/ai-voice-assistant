import subprocess
import os
import shutil
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ScreenCapture:
    def __init__(self):
        self.output_dir = Path("temp_media")
        self.output_dir.mkdir(exist_ok=True)
        self._tool = self._find_tool()

    def _is_wayland(self) -> bool:
        return bool(os.environ.get("WAYLAND_DISPLAY"))

    def _find_tool(self) -> str:
        wayland_tools = ["spectacle", "gnome-screenshot", "grim"]
        x11_tools = ["scrot", "import"]

        if self._is_wayland():
            logger.info("Detectado Wayland")
            search_order = wayland_tools + x11_tools
        else:
            logger.info("Detectado X11")
            search_order = x11_tools + wayland_tools

        for tool in search_order:
            if shutil.which(tool):
                logger.info(f"Usando {tool} para capturas")
                return tool

        logger.warning("No se encontró herramienta de captura")
        logger.info("Instala: spectacle (KDE), gnome-screenshot (GNOME), scrot (X11), grim (Sway/Hyprland)")
        return ""

    def capture(self) -> str:
        output_path = self.output_dir / "screenshot.png"

        if not self._tool:
            return ""

        try:
            logger.info(f"Capturando monitor activo con {self._tool}...")

            if self._tool == "spectacle":
                subprocess.run(
                    ["spectacle", "-m", "-b", "-n", "-o", str(output_path)],
                    capture_output=True, timeout=10
                )
            elif self._tool == "gnome-screenshot":
                subprocess.run(
                    ["gnome-screenshot", "-f", str(output_path)],
                    capture_output=True, timeout=10
                )
            elif self._tool == "scrot":
                self._capture_scrot(str(output_path))
            elif self._tool == "grim":
                self._capture_grim(str(output_path))
            elif self._tool == "import":
                subprocess.run(
                    ["import", "-window", "root", str(output_path)],
                    capture_output=True, timeout=10
                )

            if output_path.exists() and output_path.stat().st_size > 1000:
                logger.info(f"Captura OK: {output_path.stat().st_size} bytes")
                return str(output_path)
            else:
                logger.warning(f"Captura vacía o muy pequeña")
                return ""

        except subprocess.TimeoutExpired:
            logger.warning(f"{self._tool} tardó demasiado")
        except Exception as e:
            logger.error(f"Error con {self._tool}: {e}")

        return ""

    def _capture_scrot(self, output_path: str):
        try:
            result = subprocess.run(
                ["xdotool", "getmouselocation", "--shell"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                info = dict(line.split("=", 1) for line in result.stdout.strip().split("\n") if "=" in line)
                mx, my = int(info.get("X", 0)), int(info.get("Y", 0))

                monitors = self._get_x11_monitors()
                for m in monitors:
                    if m["x"] <= mx < m["x"] + m["w"] and m["y"] <= my < m["y"] + m["h"]:
                        geo = f'{m["w"]}x{m["h"]}+{m["x"]}+{m["y"]}'
                        subprocess.run(
                            ["scrot", "--overwrite", "-g", geo, output_path],
                            capture_output=True, timeout=10
                        )
                        return
        except Exception as e:
            logger.warning(f"Error en captura scrot con xdotool: {e}")
        subprocess.run(
            ["scrot", "--overwrite", output_path],
            capture_output=True, timeout=10
        )

    def _get_x11_monitors(self) -> list:
        try:
            result = subprocess.run(
                ["xdotool", "get_display_geometry"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                monitors = []
                for block in result.stdout.strip().split("\n\n"):
                    info = {}
                    for line in block.strip().split("\n"):
                        if "=" in line:
                            k, v = line.split("=", 1)
                            info[k.strip()] = int(v.strip())
                    if "width" in info and "height" in info:
                        monitors.append({
                            "x": info.get("x", 0),
                            "y": info.get("y", 0),
                            "w": info["width"],
                            "h": info["height"]
                        })
                return monitors
        except Exception as e:
            logger.warning(f"Error leyendo monitores con xdotool: {e}")
        try:
            result = subprocess.run(
                ["xrandr", "--query"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                monitors = []
                x, y = 0, 0
                for line in result.stdout.split("\n"):
                    if " connected " in line:
                        parts = line.split()
                        for p in parts:
                            if "+" in p and "x" in p:
                                w, rest = p.split("x")
                                h, px = rest.split("+")
                                monitors.append({
                                    "x": int(px.split("+")[0]) if "+" in px else x,
                                    "y": int(px.split("+")[1]) if "+" in px else y,
                                    "w": int(w),
                                    "h": int(h)
                                })
                                break
                return monitors
        except Exception as e:
            logger.warning(f"Error leyendo monitores con xrandr: {e}")
        return []

    def _capture_grim(self, output_path: str):
        result = subprocess.run(
            ["grim", output_path],
            capture_output=True, timeout=10
        )
        if result.returncode != 0:
            logger.warning(f"grim falló: {result.stderr.decode()[:200]}")
