#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="$HOME/.local/share/ai-voice-assistant"

echo "=== Instalando AI Voice Assistant ==="

# Copiar proyecto
echo "1. Copiando archivos a $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
rsync -a --exclude='venv' --exclude='__pycache__' --exclude='temp_audio' --exclude='debug.log' \
    "$SCRIPT_DIR/" "$INSTALL_DIR/"

# Crear venv en destino
echo "2. Creando entorno virtual..."
cd "$INSTALL_DIR"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -q

# Instalar servicio systemd
echo "3. Instalando servicio systemd..."
mkdir -p "$HOME/.config/systemd/user"
cp "$INSTALL_DIR/ai-voice-assistant.service" "$HOME/.config/systemd/user/"
sed -i "s|%h|$HOME|g" "$HOME/.config/systemd/user/ai-voice-assistant.service"

# Recargar systemd
systemctl --user daemon-reload

# Configurar atajo (solo info)
echo ""
echo "=== Instalación completada ==="
echo ""
echo "Para iniciar el servicio:"
echo "  systemctl --user start ai-voice-assistant"
echo ""
echo "Para iniciar automáticamente al login:"
echo "  systemctl --user enable ai-voice-assistant"
echo ""
echo "Para ver el estado:"
echo "  systemctl --user status ai-voice-assistant"
echo ""
echo "Para ver logs:"
echo "  journalctl --user -u ai-voice-assistant -f"
echo ""
echo "IMPORTANTE: Configura un atajo de teclado en tu entorno de escritorio"
echo "  apuntando a: $INSTALL_DIR/trigger.sh"
