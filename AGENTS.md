# AGENTS.md

## Arquitectura

Aplicación de escritorio Linux (X11/Wayland) que actúa como asistente de voz:
- **Trigger**: archivo `/tmp/ai_voice_trigger` polleado cada 200ms (funciona en X11 y Wayland sin root)
- **Audio**: `parecord` (PulseAudio/PipeWire), NO sounddevice/PortAudio
- **Transcripción**: Whisper local (`base` por defecto)
- **Consulta**: `opencode run` via subprocess
- **TTS**: `edge-tts` + `ffplay`
- **Captura**: detecta Wayland vs X11 y usa `spectacle`/`gnome-screenshot`/`scrot`/`grim`
- **UI**: PyQt6 ventana tipo terminal, inicia oculta

## Estado machine (main.py)

```
idle → recording → processing → speaking → idle
                              ↘ (error) → idle
```

- **idle**: ALT+Z abre ventana y graba
- **recording**: ALT+Z para y procesa
- **speaking**: ALT+Z corta TTS y cierra ventana
- **processing**: ALT+Z ignorado (no bloquear)

## Thread-safety

- UI updates desde threads secundarios usan `WorkerSignals` (`pyqtSignal`), NUNCA `QTimer.singleShot` directo ni `QMetaObject.invokeMethod` con `Qt.QueuedConnection`
- `_ui()` emite señal → `_on_ui_update` ejecuta en main thread
- TTS corre en thread separado, al terminar emite `tts_finished` → `_do_hide` resetea estado a `idle`

## Comandos clave

```bash
# Instalar (servicio systemd de sistema)
sudo ./install.sh

# Desinstalar
sudo ./uninstall.sh

# Servicio
sudo systemctl start|stop|restart|status ai-voice-assistant
sudo journalctl -u ai-voice-assistant -f

# Manual (dev)
python main.py
```

## Dependencias externas requeridas

- `parecord` (viene con pulseaudio/pipewire)
- `ffplay` (viene con ffmpeg)
- Una herramienta de captura: `spectacle` (KDE), `gnome-screenshot` (GNOME), `scrot` (X11), `grim` (Wayland wlroots)
- `opencode` en PATH (típicamente `~/.opencode/bin/opencode`)

## Gotchas

- **Capturas en Wayland**: `scrot` NO funciona. `screen_capture.py` detecta `WAYLAND_DISPLAY` y prioriza `spectacle`/`gnome-screenshot`
- **Captura por monitor**: `spectacle -m` captura el monitor del cursor. `scrot` usa `xdotool` para calcular geometría
- **Rutas de captura**: siempre convertir a absoluta con `Path.resolve()` antes de pasar a `opencode -f`
- **opencode run**: requiere `--` después de `-f archivo` → `["opencode", "run", "-f", path, "--", message]`
- **systemd service**: plantilla con `%%USER%%`, `%%HOME%%`, `%%UID%%` que `install.sh` reemplaza con `sed`
- **No usar** `keyboard` o `pynput` para hotkeys en Wayland (requieren root o no funcionan)
- **Audio vacío**: si `parecord` genera < 1000 bytes, tratar como error
