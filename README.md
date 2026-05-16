# AI Voice Assistant

Asistente de voz universal para Linux. Se activa con un atajo de teclado, graba el micrófono, transcribe con Whisper, consulta a opencode y reproduce la respuesta por voz.

## Compatibilidad

Funciona en **cualquier distro** y **cualquier entorno de escritorio**:

| Distro | Entorno | Funciona |
|---|---|---|
| Arch Linux | KDE Plasma, GNOME, bspwm, Sway, Hyprland, XFCE, i3 | Sí |
| Debian/Ubuntu | KDE Plasma, GNOME, XFCE, MATE, Cinnamon | Sí |
| Fedora | KDE Plasma, GNOME, Sway | Sí |
| Cualquier otra | Cualquiera con X11 o Wayland | Sí |

## Requisitos

- **Python 3.10+**
- **`opencode`** en el PATH
- **Micrófono** funcionando
- **Internet** (para edge-tts)
- **PulseAudio o PipeWire** (presente en cualquier distro moderna)
- **Una herramienta de captura** (instala al menos una):

| Herramienta | Entorno | Debian | Arch |
|---|---|---|---|
| `scrot` | X11 (universal) | `sudo apt install scrot` | `sudo pacman -S scrot` |
| `gnome-screenshot` | GNOME | `sudo apt install gnome-screenshot` | `sudo pacman -S gnome-screenshot` |
| `spectacle` | KDE | `sudo apt install spectacle` | `sudo pacman -S spectacle` |
| `grim` | Wayland (Sway/Hyprland) | `sudo apt install grim` | `sudo pacman -S grim` |
| `import` (ImageMagick) | X11 | `sudo apt install imagemagick` | `sudo pacman -S imagemagick` |

El asistente detecta automáticamente cuál está instalada.

## Instalación

### Opción rápida (recomendada)

```bash
git clone https://github.com/TU_USUARIO/ai-voice-assistant.git
cd ai-voice-assistant
chmod +x install.sh
./install.sh
```

Esto copia el proyecto a `~/.local/share/ai-voice-assistant`, crea el entorno virtual e instala el servicio systemd.

### Opción manual

```bash
git clone https://github.com/TU_USUARIO/ai-voice-assistant.git
cd ai-voice-assistant
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Uso

### Con servicio systemd (tras instalar)

```bash
# Iniciar
systemctl --user start ai-voice-assistant

# Iniciar automáticamente al login
systemctl --user enable ai-voice-assistant

# Ver estado
systemctl --user status ai-voice-assistant

# Ver logs
journalctl --user -u ai-voice-assistant -f

# Parar
systemctl --user stop ai-voice-assistant
```

### Manual (sin servicio)

```bash
python main.py
```

### Configurar atajo de teclado

El asistente usa un archivo trigger (`/tmp/ai_voice_trigger`) que funciona en **cualquier entorno** (X11 y Wayland). Configura un atajo de teclado en tu DE/WM apuntando a `trigger.sh`:

**KDE Plasma:**
1. `Configuración del sistema` → `Atajos` → `Atajos personalizados`
2. `Editar` → `Nuevo` → `Nuevo grupo` ("AI Voice Assistant")
3. Click derecho → `Nuevo` → `Acción global` → `Comando/URL`
4. Trigger: tu atajo preferido (ej: `ALT+Z`)
5. Comando: `~/.local/share/ai-voice-assistant/trigger.sh`
6. Aplicar

**GNOME:**
1. `Settings` → `Keyboard` → `View and Customize Shortcuts` → `Custom Shortcuts`
2. Add: Name="AI Voice Assistant", Command=`~/.local/share/ai-voice-assistant/trigger.sh`, Shortcut=`ALT+Z`

**bspwm** (con sxhkd):
```bash
# En ~/.config/sxhkd/sxhkdrc
alt + z
    ~/.local/share/ai-voice-assistant/trigger.sh
```

**Sway:**
```
# En ~/.config/sway/config
bindsym Mod4+z exec ~/.local/share/ai-voice-assistant/trigger.sh
```

**Hyprland:**
```
# En ~/.config/hypr/hyprland.conf
bind = ALT, Z, exec, ~/.local/share/ai-voice-assistant/trigger.sh
```

**XFCE:**
`Settings` → `Keyboard` → `Application Shortcuts` → Add → Command: `~/.local/share/ai-voice-assistant/trigger.sh`, Shortcut: `ALT+Z`

**i3:**
```
# En ~/.config/i3/config
bindsym Mod4+z exec ~/.local/share/ai-voice-assistant/trigger.sh
```

## Flujo del programa

```
Atajo (1ª vez)
    │
    ├─ Aparece ventana terminal (oculta hasta ahora)
    ├─ Carga historial de conversaciones anteriores
    └─ Empieza a grabar audio del micrófono
         │
         │ (hablas)
         │
         ▼
Atajo (2ª vez)
    │
    ├─ Para la grabación
    ├─ Transcribe audio → texto (Whisper local)
    ├─ Analiza si la pregunta es visual
    │   ├─ Sí → captura pantalla y adjunta imagen
    │   └─ No → consulta sin imagen (ahorra tokens)
    ├─ Envía pregunta a opencode
    ├─ Muestra respuesta en la terminal
    ├─ Lee la respuesta en voz alta (edge-tts)
    └─ Al terminar de hablar → ventana se oculta
         │
         ▼
Atajo (mientras habla)
    │
    └─ Corta la respuesta inmediatamente y oculta la ventana
         │
         ▼
Atajo (siguiente vez)
    │
    └─ Mismo flujo, pero la ventana muestra
       todo el historial acumulado
```

### Captura de pantalla inteligente

Solo se envía captura cuando la pregunta implica algo visual:
- "qué ves", "describe la pantalla", "qué tengo abierto"
- "qué color es", "qué aplicación es esa"
- "mira esto", "observa"

Las preguntas normales ("qué hora es", "explica Python") **no** envían captura, ahorrando tokens.

### Captura por monitor

En sistemas con múltiples monitores, captura solo el monitor donde está el cursor del ratón.

## Configuración

### Modelo Whisper (`src/transcriber.py`)

```python
self.transcriber = Transcriber(model_size="base")
```

| Modelo | Tamaño | Velocidad | Precisión |
|---|---|---|---|
| `tiny` | ~75MB | Muy rápido | Baja |
| `base` | ~140MB | Rápido | Media (default) |
| `small` | ~460MB | Medio | Alta |
| `medium` | ~1.5GB | Lento | Muy alta |
| `large` | ~3GB | Muy lento | Máxima |

### Voz TTS (`src/tts.py`)

```python
self.tts = TextToSpeech()  # default: es-ES-AlvaroNeural
```

Voces disponibles:
- `es-ES-AlvaroNeural` - Masculina España
- `es-ES-ElviraNeural` - Femenina España
- `es-MX-JorgeNeural` - Masculina México
- `es-MX-DaliaNeural` - Femenina México
- `es-AR-TomasNeural` - Masculina Argentina
- `es-CO-SalomeNeural` - Femenina Colombia

### Modelo opencode

Por defecto usa el modelo configurado en opencode. Para cambiarlo, edita `~/.config/opencode/opencode.jsonc`:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "opencode-go/qwen3.6-plus-free"
}
```

### Debug

```bash
journalctl --user -u ai-voice-assistant -f
```

O ejecutando manualmente:
```bash
python main.py 2>&1 | tee debug.log
```

## Estructura

```
ai-voice-assistant/
├── main.py                 # Punto de entrada
├── requirements.txt        # Dependencias Python
├── trigger.sh              # Script para atajo de teclado
├── install.sh              # Script de instalación
├── uninstall.sh            # Script de desinstalación
├── ai-voice-assistant.service  # Servicio systemd user
├── .gitignore
├── README.md
├── src/
│   ├── __init__.py
│   ├── audio_recorder.py   # Grabación con parecord (PulseAudio/PipeWire)
│   ├── transcriber.py      # Transcripción con Whisper
│   ├── tts.py              # Texto a voz con edge-tts + ffplay
│   ├── opencode_client.py  # Cliente de opencode con captura inteligente
│   ├── screen_capture.py   # Captura universal (detecta herramienta disponible)
│   ├── terminal_window.py  # Ventana tipo terminal PyQt6
│   └── hotkey_manager.py   # Hotkey vía archivo trigger (X11/Wayland)
└── temp_audio/             # Archivos temporales (audio, capturas)
```

## Solución de problemas

**La ventana no aparece al pulsar el atajo:**
- Verifica que el atajo esté bien configurado en tu DE
- Comprueba que `trigger.sh` sea ejecutable: `chmod +x trigger.sh`
- Ejecuta manualmente: `touch /tmp/ai_voice_trigger`

**No graba audio:**
- Verifica que PulseAudio o PipeWire estén corriendo: `pulseaudio --check` o `systemctl --user status pipewire`
- Prueba: `parecord test.wav` (habla, Ctrl+C, reproduce con `ffplay test.wav`)

**La captura sale negra:**
- En Wayland, algunos compositores no soportan captura. Usa `scrot` en X11 o `gnome-screenshot` en GNOME
- En KDE Wayland, `spectacle` funciona correctamente

**opencode no responde:**
- Verifica: `opencode run "di hola"`
- El timeout es de 5 minutos por consulta

**El servicio no arranca:**
- Verifica logs: `journalctl --user -u ai-voice-assistant --no-pager`
- Asegúrate de que `opencode` está en el PATH del usuario
