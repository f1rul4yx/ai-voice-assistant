#!/bin/bash
set -e

INSTALL_DIR="$HOME/.local/share/ai-voice-assistant"

echo "=== Desinstalando AI Voice Assistant ==="

# Parar servicio
systemctl --user stop ai-voice-assistant 2>/dev/null || true
systemctl --user disable ai-voice-assistant 2>/dev/null || true

# Eliminar servicio
rm -f "$HOME/.config/systemd/user/ai-voice-assistant.service"
systemctl --user daemon-reload

# Eliminar archivos
rm -rf "$INSTALL_DIR"

echo "Desinstalación completada."
