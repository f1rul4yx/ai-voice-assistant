#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="$HOME/.local/share/ai-voice-assistant"

# Detect user info
CURRENT_USER="$(whoami)"
CURRENT_UID="$(id -u)"
WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-}"
XDG_DESKTOP="${XDG_CURRENT_DESKTOP:-KDE}"

echo "=== AI Voice Assistant - Instalador ==="
echo ""
echo "Usuario: $CURRENT_USER (UID: $CURRENT_UID)"
echo "Entorno: $XDG_DESKTOP"
echo "Display: ${WAYLAND_DISPLAY:+Wayland ($WAYLAND_DISPLAY)}${WAYLAND_DISPLAY:+X11}"
echo ""

# Require sudo
if ! command -v sudo &> /dev/null; then
    echo "ERROR: se necesita 'sudo' para instalar el servicio"
    exit 1
fi

# Check dependencies
for cmd in python3 rsync systemctl; do
    if ! command -v $cmd &> /dev/null; then
        echo "ERROR: '$cmd' no encontrado"
        exit 1
    fi
done

# Copy project
echo "1. Copiando archivos a $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
rsync -a --exclude='venv' --exclude='__pycache__' --exclude='temp_audio' \
    --exclude='temp_media' --exclude='debug.log' --exclude='.git' --exclude='*.log' \
    "$SCRIPT_DIR/" "$INSTALL_DIR/"

# Create venv
echo "2. Creando entorno virtual..."
cd "$INSTALL_DIR"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -q

# Install systemd service
echo "3. Instalando servicio systemd..."
SERVICE_FILE="/etc/systemd/system/ai-voice-assistant.service"

# Replace templates
sed -e "s|%%USER%%|$CURRENT_USER|g" \
    -e "s|%%HOME%%|$HOME|g" \
    -e "s|%%UID%%|$CURRENT_UID|g" \
    -e "s|%%DESKTOP%%|$XDG_DESKTOP|g" \
    -e "s|%%WAYLAND%%|$WAYLAND_DISPLAY|g" \
    "$INSTALL_DIR/ai-voice-assistant.service" | sudo tee "$SERVICE_FILE" > /dev/null

sudo systemctl daemon-reload
sudo systemctl enable ai-voice-assistant
sudo systemctl start ai-voice-assistant

echo ""
echo "=== Instalacion completada ==="
echo ""
echo "Comandos utiles:"
echo "  sudo systemctl start ai-voice-assistant    # Iniciar"
echo "  sudo systemctl stop ai-voice-assistant     # Parar"
echo "  sudo systemctl restart ai-voice-assistant  # Reiniciar"
echo "  sudo systemctl status ai-voice-assistant   # Estado"
echo "  sudo journalctl -u ai-voice-assistant -f   # Logs"
echo ""
echo "IMPORTANTE: Configura un atajo de teclado en tu entorno"
echo "  apuntando a: $INSTALL_DIR/trigger.sh"
