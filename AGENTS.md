# AGENTS.md

## Arquitectura

Aplicación de escritorio Linux (X11/Wayland) que actúa como asistente de voz:
- **Trigger**: archivo `/tmp/ai_voice_trigger` polleado cada 200ms (funciona en X11 y Wayland sin root)
- **Audio**: `parecord` (PulseAudio/PipeWire), NO sounddevice/PortAudio
- **Transcripción**: Whisper local (`base` por defecto)
- **Consulta**: `opencode run` via subprocess
- **TTS**: `edge-tts` + `ffplay`
- **Captura**: detecta Wayland vs X11 y usa `spectacle`/`gnome-screenshot`/`scrot`/`grim`/`import`
- **UI**: PyQt6 ventana tipo terminal, inicia oculta

## Estado machine (main.py)

```
idle → recording → processing → speaking → idle
                              ↘ (error) → idle
```

- **idle**: trigger abre ventana y graba
- **recording**: trigger para y procesa
- **speaking**: trigger corta TTS y cierra ventana
- **processing**: trigger ignorado (no bloquear)

## Thread-safety

- UI updates desde threads secundarios usan `WorkerSignals` (`pyqtSignal`), NUNCA llamadas directas a widgets
- `_ui()` emite señal → `_on_ui_update` ejecuta en main thread
- TTS corre en thread separado, al terminar emite `tts_finished` → `_do_hide` resetea estado a `idle`
- `_finish()` usa QTimer con referencia guardada (`_hide_timer`), parando el anterior antes de crear uno nuevo

## Comandos clave

```bash
# Instalar (servicio systemd de sistema)
sudo ./install.sh

# Desinstalar
sudo ./uninstall.sh

# Servicio
sudo systemctl start|stop|restart|status ai-voice-assistant
sudo journalctl -u ai-voice-assistant -f

# Manual (dev) — crea venv primero si no existe
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
python main.py
```

## Gotchas

- **Capturas en Wayland**: `scrot` NO funciona. `screen_capture.py` detecta `WAYLAND_DISPLAY` y prioriza `spectacle`/`gnome-screenshot`
- **Captura por monitor**: `spectacle -m` captura el monitor del cursor. `scrot` usa `xdotool` para calcular geometría
- **Rutas de captura**: siempre convertir a absoluta con `Path.resolve()` antes de pasar a `opencode -f`
- **opencode run**: requiere `--` después de `-f archivo` → `["opencode", "run", "-f", path, "--", message]`
- **systemd service**: plantilla con `%%USER%%`, `%%HOME%%`, `%%UID%%` que `install.sh` reemplaza con `sed`
- **No usar** `keyboard` o `pynput` para hotkeys en Wayland (requieren root o no funcionan)
- **Audio vacío**: si `parecord` genera < 1000 bytes, tratar como error
- **parecord stdout**: debe ir a `DEVNULL`, no `PIPE`, o el buffer se llena y bloquea la grabación
- **grim**: NO usar flag `-o` con path de archivo (espera nombre de monitor). Uso correcto: `grim output.png`
- **temp_media/**: directorio compartido para `recording.wav` y `screenshot.png`. Creado con `mkdir(exist_ok=True)` en `AudioRecorder` y `ScreenCapture` (renombrado de `temp_audio`)
- **debug.log**: usa `RotatingFileHandler` (5MB, 3 backups). No usar `FileHandler` simple
- **Mensajes del chat**: siempre aplicar `html.escape()` antes de `insertHtml`, luego convertir `\n` → `<br>`
- **TTS temp files**: usar UUID para nombres, no PID (evita colisiones en conversaciones rápidas)
- **_needs_screenshot**: detecta preguntas visuales por keywords en `opencode_client.py`. Si se añaden nuevas, actualizar la lista
- **opencode timeout**: 300s (5 min) por consulta en `opencode_client.py`
- **install.sh excludes**: `venv`, `__pycache__`, `temp_audio`, `temp_media`, `debug.log`, `.git`, `*.log`
- **Dependencias externas**: `parecord` (pulseaudio/pipewire), `ffplay` (ffmpeg), captura (`spectacle`/`gnome-screenshot`/`scrot`/`grim`/`import`), `opencode` en PATH
