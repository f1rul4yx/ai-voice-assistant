#!/bin/bash
set -e

INSTALL_DIR="$HOME/.local/share/ai-voice-assistant"
SERVICE_FILE="/etc/systemd/system/ai-voice-assistant.service"

echo "=== AI Voice Assistant - Desinstalador ==="

# Stop and remove service
sudo systemctl stop ai-voice-assistant 2>/dev/null || true
sudo systemctl disable ai-voice-assistant 2>/dev/null || true
sudo rm -f "$SERVICE_FILE"
sudo systemctl daemon-reload

# Remove files
rm -rf "$INSTALL_DIR"

echo "Desinstalacion completada."
