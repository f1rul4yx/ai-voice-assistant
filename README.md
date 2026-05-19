# Nova

Asistente de voz para Linux con hotkey global, STT local, LLM en la nube y TTS natural.

## Arquitectura

```
Ctrl+Alt+Space → Grabar audio → faster-whisper (STT) → opencode CLI (LLM) → edge-tts + ffplay (TTS)
```

- **Hotkey**: `Ctrl+Alt+Space` para activar/detener grabación
- **STT**: faster-whisper con detección automática de idioma (es/en)
- **LLM**: opencode CLI con modelo `opencode/qwen3.6-plus-free`
- **TTS**: edge-tts con voz `es-ES-AlvaroNeural`
- **UI**: Ventana flotante Catppuccin-style en la esquina inferior derecha

## Instalación (Arch/Manjaro)

```bash
./install.sh
```

Esto instala:
- Dependencias del sistema (python, ffmpeg, pipewire-pulse, etc.)
- venv de Python con los paquetes necesarios
- Servicio systemd de usuario para autostart

## Uso

```bash
# Iniciar el servicio
systemctl --user start nova

# Detener
systemctl --user stop nova

# Reiniciar
systemctl --user restart nova

# Ver logs
journalctl --user -u nova -f
```

Pulsa `Ctrl+Alt+Space` para activar. Habla y vuelve a pulsar para enviar. La ventana se oculta automáticamente 3 segundos después de que la IA termina de hablar.

## Configuración

Edita `config.py`:

| Variable | Default | Descripción |
|---|---|---|
| `OPENCODE_MODEL` | `opencode/qwen3.6-plus-free` | Modelo LLM |
| `HOTKEY` | `{"ctrl", "alt", "space"}` | Combinación de teclas |
| `WHISPER_MODEL` | `base` | Modelo de Whisper (tiny/base/small/medium/large) |
| `WHISPER_LANGUAGE` | `None` | Idioma STT (None = auto) |
| `TTS_VOICE` | `es-ES-AlvaroNeural` | Voz de edge-tts |
| `SYSTEM_PROMPT` | Ver config | Instrucciones del sistema |

## Dependencias

**Sistema**: python, ffmpeg, pipewire-pulse, portaudio

**Python**: numpy, scipy, sounddevice, faster-whisper, pynput, PyQt6, edge-tts
