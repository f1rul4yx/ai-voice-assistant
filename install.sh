#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"

echo "=== Nova Voice Assistant ==="

if ! command -v pacman &> /dev/null; then
    echo "Error: Este script es para Arch/Manjaro."
    exit 1
fi

echo ""
echo "[1/2] Instalando dependencias del sistema..."
sudo pacman -S --needed --noconfirm python python-pip portaudio ffmpeg pipewire-pulse

echo ""
echo "[2/2] Instalando Python y servicio..."
python -m venv "$PROJECT_DIR/.venv"
"$PROJECT_DIR/.venv/bin/pip" install -r "$PROJECT_DIR/requirements.txt"

SERVICE_DIR="$HOME/.config/systemd/user"
mkdir -p "$SERVICE_DIR"
sed -e "s|__VENV_PYTHON__|$VENV_PYTHON|" \
    -e "s|__MAIN_PY__|$PROJECT_DIR/main.py|" \
    -e "s|__PROJECT_DIR__|$PROJECT_DIR|" \
    "$PROJECT_DIR/nova.service" > "$SERVICE_DIR/nova.service"

systemctl --user daemon-reload
systemctl --user enable nova.service

echo ""
echo "=== Instalacion completada ==="
echo ""
echo "Comandos:"
echo "  systemctl --user start nova      # Iniciar"
echo "  systemctl --user stop nova       # Detener"
echo "  systemctl --user restart nova    # Reiniciar"
echo "  journalctl --user -u nova -f     # Ver logs"
echo ""
echo "Atajo: Ctrl+Alt+Space"
